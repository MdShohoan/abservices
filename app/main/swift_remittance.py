
# Add this import at the top with other imports

import datetime
import os
import uuid
from collections import defaultdict
from hashlib import sha256

from flask import (
    Blueprint,
    current_app,
    flash,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_login import login_required
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from sqlalchemy import text
from werkzeug.utils import secure_filename

import app.utils
from app import LOG, db


swift_remittance = Blueprint("swift_remittance", __name__, url_prefix="/swift-remittance")


ALLOWED_UPLOAD_EXTENSIONS = {"png", "jpg", "jpeg"}
STATUS_PENDING = "pending"
STATUS_SUBMITTED = "submitted"
STATUS_VERIFIED = "verified"


def _qualified_table_name():
    schema = current_app.config.get("SWIFT_SETTLEMENT_SCHEMA", "abbl")
    table = current_app.config.get("SWIFT_SETTLEMENT_TABLE", "swift_details")
    if schema:
        return f'"{schema}"."{table}"'
    return f'"{table}"'


def _serializer():
    return URLSafeTimedSerializer(current_app.config["SECRET_KEY"], salt="swift-remittance-link")


def _token_max_age_seconds():
    return int(current_app.config.get("SWIFT_LINK_EXPIRY_SECONDS", 900))


def _otp_expiry_seconds():
    return int(current_app.config.get("SWIFT_OTP_EXPIRY_SECONDS", 300))


def _safe_status_value(value):
    normalized = (value or "").strip().lower()
    if normalized in {STATUS_PENDING, STATUS_SUBMITTED, STATUS_VERIFIED}:
        return normalized
    return STATUS_PENDING


def _allowed_upload(filename):
    if "." not in filename:
        return False
    ext = filename.rsplit(".", 1)[1].lower()
    return ext in ALLOWED_UPLOAD_EXTENSIONS


def _ensure_upload_dir():
    folder = current_app.config.get(
        "SWIFT_UPLOAD_FOLDER",
        os.path.join(current_app.root_path, "static", "uploads", "swift_remittance"),
    )
    os.makedirs(folder, exist_ok=True)
    return folder


def _read_table_columns():
    schema = current_app.config.get("SWIFT_SETTLEMENT_SCHEMA", "abbl")
    table = current_app.config.get("SWIFT_SETTLEMENT_TABLE", "swift_details")
    q = text(
        """
        SELECT column_name
        FROM information_schema.columns
        WHERE table_schema = :schema_name
          AND table_name = :table_name
        """
    )
    rows = db.session.execute(q, {"schema_name": schema, "table_name": table}).scalars().all()
    return set(rows)


def _selectable_columns():
    """
    New table: swift_details
    Fields:
        id, network, sender, receiver, msg_reference, msg_type,
        msg_received_date, msg_received_time, msg_sent_date, msg_sent_time,
        currency_code, value_date, amount, transaction_reference,
        receiver_address, account, mobile, email, email_status,
        otp_status, doc_status, created_at, doc_link_creator, url_reference
    """
    base = {
        "id", "network", "sender", "receiver", "msg_reference", "msg_type",
        "msg_received_date", "msg_received_time", "msg_sent_date", "msg_sent_time",
        "currency_code", "value_date", "amount", "transaction_reference",
        "receiver_address", "account", "mobile",
    }
    optional = {
        "email", "email_status", "otp_status", "doc_status",
        "created_at", "doc_link_creator", "url_reference",
    }
    available = _read_table_columns()
    ordered = (
        ["id", "network", "sender", "receiver", "msg_reference", "msg_type",
         "msg_received_date", "msg_received_time", "msg_sent_date", "msg_sent_time",
         "currency_code", "value_date", "amount", "transaction_reference",
         "receiver_address", "account", "mobile"]
        + sorted(optional)
    )
    return [col for col in ordered if col in available]


def _fetch_records():
    cols = _selectable_columns()
    required = {"id", "account", "mobile", "sender", "receiver"}
    if not required.issubset(set(cols)):
        raise RuntimeError("Required columns missing from swift_details table.")

    select_clause = ", ".join([f'"{col}"' for col in cols])
    sql = text(
        f"""
        SELECT {select_clause}
        FROM {_qualified_table_name()}
        ORDER BY "id" DESC
        """
    )
    rows = db.session.execute(sql).mappings().all()
    normalized = []
    for row in rows:
        item = dict(row)
        item["doc_status"] = _safe_status_value(item.get("doc_status"))
        item["otp_status"] = _safe_status_value(item.get("otp_status"))
        item["email_status"] = _safe_status_value(item.get("email_status"))
        # Provide display-friendly aliases used in templates
        item.setdefault("customer_name", item.get("receiver", ""))
        item.setdefault("account_name", item.get("account", ""))
        item.setdefault("phone_number", item.get("mobile", ""))
        item.setdefault("branch_name", item.get("network", "Unknown"))
        item.setdefault("status", item.get("doc_status", STATUS_PENDING))
        normalized.append(item)
    return normalized


def _fetch_record(record_id):
    cols = _selectable_columns()
    select_clause = ", ".join([f'"{col}"' for col in cols])
    sql = text(
        f"""
        SELECT {select_clause}
        FROM {_qualified_table_name()}
        WHERE "id" = :record_id
        LIMIT 1
        """
    )
    row = db.session.execute(sql, {"record_id": record_id}).mappings().first()
    if not row:
        return None
    item = dict(row)
    item["doc_status"] = _safe_status_value(item.get("doc_status"))
    item["otp_status"] = _safe_status_value(item.get("otp_status"))
    item["email_status"] = _safe_status_value(item.get("email_status"))
    # Aliases for template compatibility
    item.setdefault("customer_name", item.get("receiver", ""))
    item.setdefault("account_name", item.get("account", ""))
    item.setdefault("phone_number", item.get("mobile", ""))
    item.setdefault("branch_name", item.get("network", "Unknown"))
    item.setdefault("status", item.get("doc_status", STATUS_PENDING))
    return item


def _update_record_status(record_id, doc_status):
    """Update doc_status (and otp_status if relevant) in swift_details."""
    columns = _read_table_columns()
    set_parts = []
    params = {"record_id": record_id}

    if "doc_status" in columns:
        set_parts.append('"doc_status" = :doc_status')
        params["doc_status"] = doc_status

    if not set_parts:
        return  # nothing to update

    sql = text(
        f"""
        UPDATE {_qualified_table_name()}
        SET {", ".join(set_parts)}
        WHERE "id" = :record_id
        """
    )
    db.session.execute(sql, params)
    db.session.commit()


def _update_otp_status(record_id, otp_status_value):
    """Update otp_status field in swift_details."""
    columns = _read_table_columns()
    if "otp_status" not in columns:
        return
    sql = text(
        f"""
        UPDATE {_qualified_table_name()}
        SET "otp_status" = :otp_status
        WHERE "id" = :record_id
        """
    )
    db.session.execute(sql, {"record_id": record_id, "otp_status": otp_status_value})
    db.session.commit()


def _update_email_status(record_id, email_status_value):
    """Update email_status field in swift_details."""
    columns = _read_table_columns()
    if "email_status" not in columns:
        return
    sql = text(
        f"""
        UPDATE {_qualified_table_name()}
        SET "email_status" = :email_status
        WHERE "id" = :record_id
        """
    )
    db.session.execute(sql, {"record_id": record_id, "email_status": email_status_value})
    db.session.commit()


def _update_url_reference(record_id, url_ref):
    """Store the secure link token reference in url_reference field."""
    columns = _read_table_columns()
    if "url_reference" not in columns:
        return
    sql = text(
        f"""
        UPDATE {_qualified_table_name()}
        SET "url_reference" = :url_reference
        WHERE "id" = :record_id
        """
    )
    db.session.execute(sql, {"record_id": record_id, "url_reference": url_ref})
    db.session.commit()


def _update_submission_fields(record_id, email_value, doc_link):
    """
    After document upload, update email, doc_status = 'submitted',
    and doc_link_creator with the upload path reference.
    """
    columns = _read_table_columns()
    updates = []
    params = {"record_id": record_id}

    if "email" in columns:
        updates.append('"email" = :email')
        params["email"] = email_value

    if "doc_link_creator" in columns:
        updates.append('"doc_link_creator" = :doc_link_creator')
        params["doc_link_creator"] = doc_link

    if "doc_status" in columns:
        updates.append('"doc_status" = :doc_status')
        params["doc_status"] = STATUS_SUBMITTED

    if updates:
        sql = text(
            f"""
            UPDATE {_qualified_table_name()}
            SET {", ".join(updates)}
            WHERE "id" = :record_id
            """
        )
        db.session.execute(sql, params)
        db.session.commit()


def _build_grouped_records(records):
    grouped = defaultdict(list)
    for row in records:
        grouped[row.get("network") or "Unknown Network"].append(row)
    return dict(grouped)


# ---------------------------------------------------------------------------
# Routes
# ---------------------------------------------------------------------------

@swift_remittance.route("/")
@login_required
def admin_panel():
    try:
        records = _fetch_records()
        grouped_records = _build_grouped_records(records)
        return render_template("swift_remittance/admin_panel.html", grouped_records=grouped_records)
    except Exception as ex:
        LOG.exception("SWIFT admin panel load failed: %s", ex)
        flash("Unable to load SWIFT remittance data right now.", "danger")
        return render_template("swift_remittance/admin_panel.html", grouped_records={})


@swift_remittance.route("/send-link/<int:record_id>", methods=["POST"])
@login_required
def send_secure_link(record_id):
    try:
        record = _fetch_record(record_id)
        if not record:
            flash("Record not found.", "warning")
            return redirect(url_for("swift_remittance.admin_panel"))

        token = _serializer().dumps({
            "record_id": record_id,
            "phone": record.get("mobile", ""),
        })

        # Store url_reference in the table
        _update_url_reference(record_id, token[:20])  # store first 20 chars as reference
        _update_email_status(record_id, "sent")

        verify_url = url_for(
            "swift_remittance.verify_entry",
            token=token,
            _external=True,
        )

        sms_message = (
            "AB Bank SWIFT Remittance: Complete your verification using this secure link "
            f"(valid for {_token_max_age_seconds() // 60} minutes): {verify_url}"
        )
        # ✅ TEST MODE (no SMS)
        print("\n====== SWIFT TEST LINK ======")
        print(f"Phone: {record['phone_number']}")
        print(f"Link: {verify_url}")
        print("================================\n")

        flash("Test mode: Link printed in console.", "success")
        # Send SMS
        # mobile = record.get("mobile", "")
        # if mobile:
        #     sms_response = app.utils.smsnewapi(mobile, sms_message)
        #     if sms_response and sms_response.get("status") == "SUCCESS":
        #         sms_response["trackingcode"] = str(record_id)
        #         app.utils.add_ssl_otp(sms_response, str(record_id))
        #         flash("Secure link sent successfully via SMS.", "success")
        #     else:
        #         # TEST MODE fallback
        #         print("\n====== SWIFT TEST LINK ======")
        #         print(f"Phone : {mobile}")
        #         print(f"Link  : {verify_url}")
        #         print("================================\n")
        #         flash("SMS gateway unavailable – link printed in console (test mode).", "warning")
        # else:
        #     print(f"\nSWIFT LINK (no mobile): {verify_url}\n")
        #     flash("No mobile number on record – link printed in console.", "warning")

    except Exception as ex:
        LOG.exception("SWIFT send-link failed for record %s: %s", record_id, ex)
        flash("Unexpected error while sending SMS.", "danger")

    return redirect(url_for("swift_remittance.admin_panel"))


@swift_remittance.route("/mark-verified/<int:record_id>", methods=["POST"])
@login_required
def mark_verified(record_id):
    try:
        _update_record_status(record_id, STATUS_VERIFIED)
        flash("Record marked as verified.", "success")
    except Exception as ex:
        LOG.exception("SWIFT status update failed for %s: %s", record_id, ex)
        flash("Could not update status to verified.", "danger")
    return redirect(url_for("swift_remittance.admin_panel"))


@swift_remittance.route("/verify")
def verify_entry():
    token = request.args.get("token", "").strip()
    if not token:
        flash("Invalid verification link.", "danger")
        return redirect(url_for("main.index"))

    try:
        payload = _serializer().loads(token, max_age=_token_max_age_seconds())
        record_id = int(payload.get("record_id"))
        record = _fetch_record(record_id)
        if not record:
            flash("Record not found for this link.", "danger")
            return redirect(url_for("main.index"))
        return render_template("swift_remittance/verify.html", token=token, record=record)
    except SignatureExpired:
        flash("Verification link expired. Please request a new SMS.", "danger")
        return redirect(url_for("main.index"))
    except (BadSignature, ValueError):
        flash("Invalid verification link.", "danger")
        return redirect(url_for("main.index"))


@swift_remittance.route("/send-otp", methods=["POST"])
def send_otp():
    token = request.form.get("token", "").strip()
    if not token:
        flash("Invalid request.", "danger")
        return redirect(url_for("main.index"))

    try:
        payload = _serializer().loads(token, max_age=_token_max_age_seconds())
        record_id = int(payload.get("record_id"))
        record = _fetch_record(record_id)
        if not record:
            flash("Record not found.", "danger")
            return redirect(url_for("main.index"))

        otp = str(app.utils.otpgen())
        expires_at = datetime.datetime.utcnow() + datetime.timedelta(seconds=_otp_expiry_seconds())
        otp_hash = sha256(otp.encode("utf-8")).hexdigest()

        session["swift_otp"] = {
            "record_id": record_id,
            "otp_hash": otp_hash,
            "expires_at": expires_at.isoformat(),
            "verified": False,
            "token": token,
            "tries": 0,
        }
        # ✅ TEST MODE (NO SMS)
        print("\n====== SWIFT TEST OTP ======")
        print(f"Phone: {record['phone_number']}")
        print(f"OTP: {otp}")
        print("================================\n")
        # Update otp_status = 'sent'
        # _update_otp_status(record_id, "sent")

        # mobile = record.get("mobile", "")
        # sms_message = (
        #     f"AB Bank SWIFT Remittance OTP: {otp}. "
        #     f"Valid for {_otp_expiry_seconds() // 60} minutes. Do not share."
        # )

        # if mobile:
        #     sms_response = app.utils.smsnewapi(mobile, sms_message)
        #     if sms_response and sms_response.get("status") == "SUCCESS":
        #         sms_response["trackingcode"] = f"swift-otp-{record_id}"
        #         app.utils.add_ssl_otp(sms_response, f"swift-otp-{record_id}")
        #         flash("OTP sent successfully.", "success")
        #     else:
        #         print(f"\n====== SWIFT TEST OTP ======\nPhone: {mobile}\nOTP: {otp}\n============================\n")
        #         flash(f"Test OTP (console): {otp}", "success")
        # else:
        #     print(f"\nSWIFT OTP (no mobile): {otp}\n")
        #     flash(f"Test OTP (no mobile): {otp}", "success")

        return redirect(url_for("swift_remittance.verify_entry", token=token))

    except SignatureExpired:
        flash("Verification link expired.", "danger")
        return redirect(url_for("main.index"))
    except Exception as ex:
        LOG.exception("SWIFT OTP send failed: %s", ex)
        flash("Unable to send OTP now.", "danger")
        return redirect(url_for("main.index"))


@swift_remittance.route("/verify-otp", methods=["POST"])
def verify_otp():
    token = request.form.get("token", "").strip()
    user_otp = request.form.get("otp", "").strip()
    otp_session = session.get("swift_otp", {})

    if not otp_session or otp_session.get("token") != token:
        flash("OTP session not found. Please request OTP again.", "danger")
        return redirect(url_for("swift_remittance.verify_entry", token=token))

    try:
        expires_at = datetime.datetime.fromisoformat(otp_session["expires_at"])
        if datetime.datetime.utcnow() > expires_at:
            session.pop("swift_otp", None)
            flash("OTP expired. Please request a new OTP.", "warning")
            return redirect(url_for("swift_remittance.verify_entry", token=token))

        tries = int(otp_session.get("tries", 0)) + 1
        otp_session["tries"] = tries
        if tries > int(current_app.config.get("MAX_OTP_LIMIT", 3)):
            session.pop("swift_otp", None)
            _update_otp_status(int(otp_session.get("record_id", 0)), "failed")
            flash("Maximum OTP attempts exceeded.", "danger")
            return redirect(url_for("swift_remittance.verify_entry", token=token))

        incoming_hash = sha256(user_otp.encode("utf-8")).hexdigest()
        if incoming_hash != otp_session["otp_hash"]:
            session["swift_otp"] = otp_session
            flash("OTP does not match. Please try again.", "danger")
            return redirect(url_for("swift_remittance.verify_entry", token=token))

        # OTP verified
        otp_session["verified"] = True
        session["swift_otp"] = otp_session
        _update_otp_status(int(otp_session["record_id"]), STATUS_VERIFIED)

        return redirect(url_for("swift_remittance.submission_form", token=token))

    except Exception as ex:
        LOG.exception("SWIFT OTP verify failed: %s", ex)
        flash("OTP verification failed.", "danger")
        return redirect(url_for("swift_remittance.verify_entry", token=token))


# @swift_remittance.route("/submit")
# def submission_form():
#     token = request.args.get("token", "").strip()
#     otp_session = session.get("swift_otp", {})
#     if not otp_session or not otp_session.get("verified") or otp_session.get("token") != token:
#         flash("Please complete OTP verification first.", "warning")
#         return redirect(url_for("swift_remittance.verify_entry", token=token))

#     record = _fetch_record(int(otp_session["record_id"]))
#     if not record:
#         flash("Record not found.", "danger")
#         return redirect(url_for("main.index"))

#     return render_template("swift_remittance/submission.html", token=token, record=record)
@swift_remittance.route("/submit")
def submission_form():
    token = request.args.get("token", "").strip()
    otp_session = session.get("swift_otp", {})
    if not otp_session or not otp_session.get("verified") or otp_session.get("token") != token:
        flash("Please complete OTP verification first.", "warning")
        return redirect(url_for("swift_remittance.verify_entry", token=token))

    record = _fetch_record(int(otp_session["record_id"]))
    if not record:
        flash("Record not found.", "danger")
        return redirect(url_for("main.index"))

    # Check if amount > 20000 — pass flag to template
    amount = float(record.get("amount") or 0)
    show_formc = amount > 20000

    return render_template(
        "swift_remittance/submission.html",
        token=token,
        record=record,
        show_formc=show_formc
    )

# @swift_remittance.route("/submit", methods=["POST"])
# def submit_documents():
#     token = request.form.get("token", "").strip()
#     email_value = request.form.get("email", "").strip()
#     doc_file = request.files.get("doc_file")  # single document upload

#     otp_session = session.get("swift_otp", {})
#     if not otp_session or not otp_session.get("verified") or otp_session.get("token") != token:
#         flash("Session expired. Please verify again.", "danger")
#         return redirect(url_for("swift_remittance.verify_entry", token=token))

#     if not email_value:
#         flash("Email is required.", "warning")
#         return redirect(url_for("swift_remittance.submission_form", token=token))

#     if "@" not in email_value:
#         flash("Please provide a valid email address.", "warning")
#         return redirect(url_for("swift_remittance.submission_form", token=token))

#     doc_link = ""
#     if doc_file and doc_file.filename:
#         if not _allowed_upload(doc_file.filename):
#             flash("Only JPG, JPEG, and PNG files are allowed.", "warning")
#             return redirect(url_for("swift_remittance.submission_form", token=token))

#         try:
#             upload_dir = _ensure_upload_dir()
#             max_bytes = int(current_app.config.get("MAX_CONTENT_LENGTH", 2 * 1024 * 1024))

#             doc_file.seek(0, os.SEEK_END)
#             file_size = doc_file.tell()
#             doc_file.seek(0)

#             if file_size > max_bytes:
#                 flash("File size exceeds the allowed limit.", "warning")
#                 return redirect(url_for("swift_remittance.submission_form", token=token))

#             suffix = secure_filename(doc_file.filename)
#             base = f"{otp_session['record_id']}_{uuid.uuid4().hex}"
#             file_name = f"{base}_{suffix}"
#             abs_path = os.path.join(upload_dir, file_name)
#             doc_file.save(abs_path)

#             web_base = "/static/uploads/swift_remittance"
#             doc_link = f"{web_base}/{file_name}"

#         except Exception as ex:
#             LOG.exception("SWIFT document file save failed: %s", ex)
#             flash("Failed to save uploaded document.", "danger")
#             return redirect(url_for("swift_remittance.submission_form", token=token))

#     try:
#         _update_submission_fields(
#             int(otp_session["record_id"]),
#             email_value,
#             doc_link[:10] if doc_link else "",  # doc_link_creator is varchar(10), store short ref
#         )
#         session.pop("swift_otp", None)
#         flash("Documents submitted successfully.", "success")
#         return redirect(url_for("swift_remittance.submission_success"))
#     except Exception as ex:
#         LOG.exception("SWIFT submission DB update failed: %s", ex)
#         flash("Failed to save submission data.", "danger")
#         return redirect(url_for("swift_remittance.submission_form", token=token))
# Add import at top
from app.models import SwiftFormCSubmission

# Update submit_documents route
@swift_remittance.route("/submit", methods=["POST"])
def submit_documents():
  
    from app.models import SwiftFormCSubmission  # Import here
    
    token = request.form.get("token", "").strip()
    email_value = request.form.get("email", "").strip()
    doc_file = request.files.get("doc_file")

    otp_session = session.get("swift_otp", {})
    if not otp_session or not otp_session.get("verified") or otp_session.get("token") != token:
        flash("Session expired. Please verify again.", "danger")
        return redirect(url_for("swift_remittance.verify_entry", token=token))

    if not email_value or "@" not in email_value:
        flash("Please provide a valid email address.", "warning")
        return redirect(url_for("swift_remittance.submission_form", token=token))

    doc_link = ""
    now = datetime.datetime.utcnow()

    if doc_file and doc_file.filename:
        if not _allowed_upload(doc_file.filename):
            flash("Only JPG, JPEG, and PNG files are allowed.", "warning")
            return redirect(url_for("swift_remittance.submission_form", token=token))
        try:
            upload_dir = _ensure_upload_dir()
            max_bytes = int(current_app.config.get("MAX_CONTENT_LENGTH", 2 * 1024 * 1024))
            doc_file.seek(0, os.SEEK_END)
            file_size = doc_file.tell()
            doc_file.seek(0)
            if file_size > max_bytes:
                flash("File size exceeds the allowed limit.", "warning")
                return redirect(url_for("swift_remittance.submission_form", token=token))
            suffix = secure_filename(doc_file.filename)
            base = f"{otp_session['record_id']}_{uuid.uuid4().hex}"
            file_name = f"{base}_{suffix}"
            abs_path = os.path.join(upload_dir, file_name)
            doc_file.save(abs_path)
            doc_link = f"/static/uploads/swift_remittance/{file_name}"
        except Exception as ex:
            LOG.exception("File save failed: %s", ex)
            flash("Failed to save uploaded document.", "danger")
            return redirect(url_for("swift_remittance.submission_form", token=token))

    try:
        record_id = int(otp_session["record_id"])
        record = _fetch_record(record_id)
        amount = float(record.get("amount") or 0)

        # Update swift_details table
        _update_submission_fields(
            record_id,
            email_value,
            doc_link[:10] if doc_link else ""
        )

        # Save to swift_formc_submission table
        dt = datetime.datetime.now()
        submission_id = int(dt.strftime("%Y%m%d%H%M%S%f")[:-3])
        
        current_app.logger.info(f"Creating submission record with ID: {submission_id}")

        new_submission = SwiftFormCSubmission(
            id=submission_id,
            swift_record_id=record_id,
            applicant_name=record.get("receiver", ""),
            applicant_address=record.get("receiver_address", ""),
            applicant_mobile=record.get("mobile", ""),
            applicant_email=email_value,
            applicant_nationality="bangladeshi",
            remittance_amount=amount,
            remittance_currency=record.get("currency_code", "USD"),
            remitter_name=record.get("sender", ""),
            remitter_address="",
            remitted_bank_name="",
            remitted_bank_address="",
            remittance_reference=record.get("transaction_reference", ""),
            remittance_type="Others",
            purpose_of_remittance_id=None,
            purpose_specify="",
            doc_file_path=doc_link,
            doc_upload_at=now if doc_link else None,
            formc_id=None,
            formc_submitted=0,
            status=1,  # doc submitted
            created_at=dt,
            updated_at=dt
        )
        db.session.add(new_submission)
        db.session.commit()
        
        current_app.logger.info(f"Submission record {submission_id} created successfully")

        # Store submission_id in session for Form-C step
        session["swift_formc_data"] = {
            "record_id": record_id,
            "submission_id": submission_id,
            "applicant_name": record.get("receiver", ""),
            "applicant_address": record.get("receiver_address", ""),
            "applicant_mobile": record.get("mobile", ""),
            "remittance_amount": amount,
            "remittance_currency": record.get("currency_code", "USD"),
            "remitter_name": record.get("sender", ""),
            "token": token
        }
        
        current_app.logger.info(f"Session data set with submission_id: {submission_id}")

        session.pop("swift_otp", None)

        if amount > 20000:
            flash("Document submitted. Please complete Form-C declaration.", "info")
            return redirect(url_for("swift_remittance.swift_formc_form", token=token))

        flash("Documents submitted successfully!", "success")
        return redirect(url_for("swift_remittance.submission_success"))

    except Exception as ex:
        db.session.rollback()
        LOG.exception("Submission failed: %s", ex)
        flash(f"Failed to save submission: {str(ex)}", "danger")
        return redirect(url_for("swift_remittance.submission_form", token=token))
@swift_remittance.route("/formc-form")
def swift_formc_form():
    token = request.args.get("token", "").strip()
    formc_data = session.get("swift_formc_data", {})
    
    if not formc_data or formc_data.get("token") != token:
        flash("Session expired.", "danger")
        return redirect(url_for("main.index"))
    
    from app.dbmodels.formc import Remittance_Purpose
    purposes = Remittance_Purpose.query.all()
    
    return render_template(
        "swift_remittance/swift_formc.html",
        token=token,
        formc_data=formc_data,
        purposes=purposes,
        applicant_name=formc_data.get("applicant_name", ""),
        applicant_address=formc_data.get("applicant_address", ""),
        applicant_mobile=formc_data.get("applicant_mobile", ""),
    )

@swift_remittance.route("/formc-submit", methods=["POST"])
def swift_formc_submit():
    from app.models import SwiftFormCSubmission

    token = request.form.get("token", "").strip()
    formc_data = session.get("swift_formc_data", {})

    current_app.logger.info(f"Form-C Submit - Token: {token[:20] if token else 'None'}...")
    current_app.logger.info(f"Session data exists: {bool(formc_data)}")

    if not formc_data or formc_data.get("token") != token:
        current_app.logger.warning("Session expired or token mismatch")
        flash("Session expired. Please start over.", "danger")
        return redirect(url_for("main.index"))

    try:
        # Get form data
        remittance_type = request.form.get("remittance_type", "Others")
        opt = request.form.get("opt", "0")
        ictPurposeSpecify = request.form.get("ictPurposeSpecify", "").strip()
        purposeSpecify = request.form.get("purposeSpecify", "").strip()
        remitter_name = request.form.get("remitter_name", "").strip()
        remitter_address = request.form.get("remitter_address", "").strip()
        remitted_bank_name = request.form.get("remitted_bank_name", "").strip()
        remitted_bank_address = request.form.get("remitted_bank_address", "").strip()
        remittance_reference = request.form.get("remittance_reference", "").strip()
        applicant_name = request.form.get("applicant_name", "").strip()
        applicant_address = request.form.get("applicant_address", "").strip()
        applicant_nationality = request.form.get("nationality", "bangladeshi")
        applicant_mobile = request.form.get("applicant_mobile", "").strip()

        # Determine purpose
        purpose_of_remittance_id = int(opt) if (remittance_type == "ICT" and opt.isdigit()) else 0
        if remittance_type != "ICT":
            ictPurposeSpecify = purposeSpecify

        dt = datetime.datetime.now()
        formc_id = int(dt.strftime("%Y%m%d%H%M%S%f")[:-3])

        # Update swift_formc_submission table only (no separate remittance table needed)
        submission_id = formc_data.get("submission_id")
        current_app.logger.info(f"Updating submission_id: {submission_id}")
        
        if submission_id:
            submission = SwiftFormCSubmission.query.filter_by(id=submission_id).first()
            if submission:
                current_app.logger.info(f"Found submission record {submission_id}, updating with formc_id: {formc_id}")
                
                # Update all Form-C fields
                submission.formc_id = formc_id
                submission.formc_submitted = 1
                submission.remitter_name = remitter_name
                submission.remitter_address = remitter_address
                submission.remitted_bank_name = remitted_bank_name
                submission.remitted_bank_address = remitted_bank_address
                submission.remittance_reference = remittance_reference
                submission.remittance_type = remittance_type
                submission.purpose_of_remittance_id = purpose_of_remittance_id
                submission.purpose_specify = ictPurposeSpecify
                submission.applicant_name = applicant_name
                submission.applicant_address = applicant_address
                submission.applicant_nationality = applicant_nationality
                submission.status = 2  # formc submitted
                submission.updated_at = dt
                
                db.session.commit()
                current_app.logger.info(f"Successfully updated submission {submission_id} with formc_id {formc_id}")
            else:
                current_app.logger.error(f"Submission record {submission_id} not found!")
                flash("Error: Submission record not found.", "danger")
                return redirect(url_for("swift_remittance.swift_formc_form", token=token))
        else:
            current_app.logger.error("No submission_id in session data!")
            flash("Error: No submission ID found in session.", "danger")
            return redirect(url_for("swift_remittance.swift_formc_form", token=token))

        # Clear session data
        session.pop("swift_formc_data", None)
        session.pop("swift_otp", None)

        flash(f"Form-C submitted successfully! Tracking ID: {formc_id}", "success")
        return redirect(url_for("swift_remittance.submission_success"))

    except Exception as ex:
        db.session.rollback()
        LOG.exception("Form-C submit failed: %s", ex)
        flash(f"Failed to submit Form-C: {str(ex)}", "danger")
        return redirect(url_for("swift_remittance.swift_formc_form", token=token))
@swift_remittance.route("/submission-success")
def submission_success():
    return render_template("swift_remittance/success.html")