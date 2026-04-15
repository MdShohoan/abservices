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
    schema = current_app.config.get("SWIFT_SETTLEMENT_SCHEMA", "public")
    table = current_app.config.get("SWIFT_SETTLEMENT_TABLE", "settlement_data")
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
    schema = current_app.config.get("SWIFT_SETTLEMENT_SCHEMA", "public")
    table = current_app.config.get("SWIFT_SETTLEMENT_TABLE", "settlement_data")
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
    base = {"id", "account_name", "phone_number", "customer_name", "branch_name"}
    optional = {"status", "tin", "email", "nid_front_path", "nid_back_path", "updated_at"}
    available = _read_table_columns()
    return [col for col in list(base) + sorted(optional) if col in available]


def _fetch_records():
    cols = _selectable_columns()
    if not {"id", "account_name", "phone_number", "customer_name", "branch_name"}.issubset(set(cols)):
        raise RuntimeError("Required columns missing from settlement_data table.")

    select_clause = ", ".join([f'"{col}"' for col in cols])
    sql = text(
        f"""
        SELECT {select_clause}
        FROM {_qualified_table_name()}
        ORDER BY "branch_name" ASC, "id" DESC
        """
    )
    rows = db.session.execute(sql).mappings().all()
    normalized = []
    for row in rows:
        item = dict(row)
        item["status"] = _safe_status_value(item.get("status"))
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
    item["status"] = _safe_status_value(item.get("status"))
    return item


def _update_record_status(record_id, status):
    columns = _read_table_columns()
    set_parts = ['"status" = :status']
    params = {"record_id": record_id, "status": status}
    if "updated_at" in columns:
        set_parts.append('"updated_at" = :updated_at')
        params["updated_at"] = datetime.datetime.now()

    sql = text(
        f"""
        UPDATE {_qualified_table_name()}
        SET {", ".join(set_parts)}
        WHERE "id" = :record_id
        """
    )
    db.session.execute(sql, params)
    db.session.commit()


def _update_submission_fields(record_id, tin, email, nid_front_web_path, nid_back_web_path):
    columns = _read_table_columns()
    updates = []
    params = {"record_id": record_id}

    if "tin" in columns:
        updates.append('"tin" = :tin')
        params["tin"] = tin
    if "email" in columns:
        updates.append('"email" = :email')
        params["email"] = email
    if "nid_front_path" in columns:
        updates.append('"nid_front_path" = :nid_front_path')
        params["nid_front_path"] = nid_front_web_path
    if "nid_back_path" in columns:
        updates.append('"nid_back_path" = :nid_back_path')
        params["nid_back_path"] = nid_back_web_path
    if "updated_at" in columns:
        updates.append('"updated_at" = :updated_at')
        params["updated_at"] = datetime.datetime.now()

    if updates:
        sql = text(
            f"""
            UPDATE {_qualified_table_name()}
            SET {", ".join(updates)}
            WHERE "id" = :record_id
            """
        )
        db.session.execute(sql, params)

    _update_record_status(record_id, STATUS_SUBMITTED)


def _build_grouped_records(records):
    grouped = defaultdict(list)
    for row in records:
        grouped[row.get("branch_name") or "Unknown Branch"].append(row)
    return dict(grouped)


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

        token = _serializer().dumps({"record_id": record_id, "phone": record.get("phone_number", "")})
        verify_url = url_for("swift_remittance.verify_entry", token=token, _external=True)
        sms_message = (
            "AB Bank SWIFT Remittance: Complete your verification using this secure link "
            f"(valid for {_token_max_age_seconds() // 60} minutes): {verify_url}"
        )

        sms_response = app.utils.smsnewapi(record["phone_number"], sms_message)
        if sms_response and sms_response.get("status") == "SUCCESS":
            # Reuse existing SMS logging table.
            sms_response["trackingcode"] = str(record_id)
            app.utils.add_ssl_otp(sms_response, str(record_id))
            flash("Secure link sent successfully.", "success")
        else:
            flash("SMS could not be sent. Please try again.", "danger")
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

        sms_message = (
            f"AB Bank SWIFT Remittance OTP: {otp}. "
            f"This OTP expires in {_otp_expiry_seconds() // 60} minutes."
        )
        sms_response = app.utils.smsnewapi(record["phone_number"], sms_message)
        if sms_response and sms_response.get("status") == "SUCCESS":
            sms_response["trackingcode"] = f"swift-otp-{record_id}"
            app.utils.add_ssl_otp(sms_response, f"swift-otp-{record_id}")
            flash("OTP sent successfully.", "success")
        else:
            flash("Failed to send OTP SMS.", "danger")

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
            flash("Maximum OTP attempts exceeded.", "danger")
            return redirect(url_for("swift_remittance.verify_entry", token=token))

        incoming_hash = sha256(user_otp.encode("utf-8")).hexdigest()
        if incoming_hash != otp_session["otp_hash"]:
            session["swift_otp"] = otp_session
            flash("OTP does not match. Please try again.", "danger")
            return redirect(url_for("swift_remittance.verify_entry", token=token))

        otp_session["verified"] = True
        session["swift_otp"] = otp_session
        return redirect(url_for("swift_remittance.submission_form", token=token))
    except Exception as ex:
        LOG.exception("SWIFT OTP verify failed: %s", ex)
        flash("OTP verification failed.", "danger")
        return redirect(url_for("swift_remittance.verify_entry", token=token))


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

    return render_template("swift_remittance/submission.html", token=token, record=record)


@swift_remittance.route("/submit", methods=["POST"])
def submit_documents():
    token = request.form.get("token", "").strip()
    tin_value = request.form.get("tin", "").strip()
    email_value = request.form.get("email", "").strip()
    nid_front = request.files.get("nid_front")
    nid_back = request.files.get("nid_back")

    otp_session = session.get("swift_otp", {})
    if not otp_session or not otp_session.get("verified") or otp_session.get("token") != token:
        flash("Session expired. Please verify again.", "danger")
        return redirect(url_for("swift_remittance.verify_entry", token=token))

    if not tin_value or not email_value:
        flash("TIN and email are required.", "warning")
        return redirect(url_for("swift_remittance.submission_form", token=token))

    if "@" not in email_value:
        flash("Please provide a valid email address.", "warning")
        return redirect(url_for("swift_remittance.submission_form", token=token))

    if not nid_front or not nid_back:
        flash("Both NID front and back images are required.", "warning")
        return redirect(url_for("swift_remittance.submission_form", token=token))

    if not _allowed_upload(nid_front.filename) or not _allowed_upload(nid_back.filename):
        flash("Only JPG, JPEG, and PNG files are allowed.", "warning")
        return redirect(url_for("swift_remittance.submission_form", token=token))

    try:
        upload_dir = _ensure_upload_dir()
        max_bytes = int(current_app.config.get("MAX_CONTENT_LENGTH", 2 * 1024 * 1024))

        nid_front.seek(0, os.SEEK_END)
        front_size = nid_front.tell()
        nid_front.seek(0)
        nid_back.seek(0, os.SEEK_END)
        back_size = nid_back.tell()
        nid_back.seek(0)

        if front_size > max_bytes or back_size > max_bytes:
            flash("Each NID file must be within allowed size.", "warning")
            return redirect(url_for("swift_remittance.submission_form", token=token))

        suffix_front = secure_filename(nid_front.filename)
        suffix_back = secure_filename(nid_back.filename)
        base = f"{otp_session['record_id']}_{uuid.uuid4().hex}"
        front_name = f"{base}_front_{suffix_front}"
        back_name = f"{base}_back_{suffix_back}"
        front_abs = os.path.join(upload_dir, front_name)
        back_abs = os.path.join(upload_dir, back_name)
        nid_front.save(front_abs)
        nid_back.save(back_abs)

        web_base = "/static/uploads/swift_remittance"
        front_web_path = f"{web_base}/{front_name}"
        back_web_path = f"{web_base}/{back_name}"

        _update_submission_fields(
            int(otp_session["record_id"]),
            tin_value,
            email_value,
            front_web_path,
            back_web_path,
        )
        session.pop("swift_otp", None)
        flash("Documents submitted successfully.", "success")
        return redirect(url_for("swift_remittance.submission_success"))
    except Exception as ex:
        LOG.exception("SWIFT document submission failed: %s", ex)
        flash("Failed to save submission data.", "danger")
        return redirect(url_for("swift_remittance.submission_form", token=token))


@swift_remittance.route("/submission-success")
def submission_success():
    return render_template("swift_remittance/success.html")
