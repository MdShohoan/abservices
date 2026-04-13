
//console.log ("baseurl:" +base_url);
//let base_url = 'http://192.168.19.72:5000';


function handlecsrferror(){

	/*let request_type = trackingcode.substring(1, 2);
	if (request_type == 'LN'){

		resultCode = '';
		url = bkash_api_url+'/account/link/redirect?id='+trackingcode+'&resultCode='+resultCode;
	}else {
		resultCode = '';
		url = bkash_api_url+'/add/money/redirect?id='+trackingcode+'&resultCode='+resultCode;
	}*/

}

function resendOtp(csrf_token)
{
	var number = $("#mobile").val();
	var input = {
		"mobile_number" : number,
		"csrf_token" :csrf_token,
		"action" : "send_otp"
	};

	$.ajaxSetup({
        beforeSend: function(xhr, settings) {
            if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        }
    });

	$.ajax({
		url : base_url+'/resend/',
		type : 'POST',
		dataType : "json",
		data : input,
		success : function(response) {
				//alert (response[1].message);
				//alert (response[0].message);
				console.log (response)
				if (response[0].status=='fail'){
                        
					console.log ('URL : ' +response[1].redirectUrl )
					window.location.href = response[1].redirectUrl;
				   

				}
				$("." + response.type).html(response[1].message)
				$("." + response.type).show();

				console.log ('URL : ' +response[1].redirectUrl )
				window.location.href = response[1].redirectUrl;
			},
			error : function() {
				alert("error");
			}
		});
	

}


function verifyOTP() {
	$("#err-div").html("").hide();
	$(".success").html("").hide();
	let otp 			= $("#mobileOtp").val();
	//let type 			= $('#request_type').val();
	
	if (otp ==""){

		$("#err-div").html("OTP Cannot be blank.").show();
		return false;
	}

	$('#submitBtn').prop('disabled', true);
	
	let trackingcode	= $("#trackingcode").val();
	let type 			= $("#request_type").val();

	//alert (type);
	//var csrf_token = "{{ csrf_token() }}";
	//var mobile = $("#mobile").val();
	var csrf_token = $("#csrf_token").val();
	//alert (csrf_token);
    //alert (otp);
	var input = {
		"otp" : otp,
		"action" : "verify_otp",
		"csrf_token" : csrf_token,
		"trackingcode" : trackingcode,
		"request_type" : type
	};

	$.ajaxSetup({
        beforeSend: function(xhr, settings) {
            
			if (!/^(GET|HEAD|OPTIONS|TRACE)$/i.test(settings.type) && !this.crossDomain) {
                xhr.setRequestHeader("X-CSRFToken", csrf_token);
            }
        }
    });
	
	//if (otp.length == 6 && otp != null) {
		if (otp != null) {
		console.log ('ajax');
		$("#spinning-div").show();
		ajax_url =  base_url+'verify/'+otp+'/'+type+'/'
		console.log ('ajax_url:' + ajax_url)
        $.ajax({
			//url : base_url+'verify/'+otp+'/'+type+'/',
			url :ajax_url , 
			type : 'POST',
			dataType : "json",
			data : input,
			//headers : {'charset': 'utf-8', 'Content-Type': 'application/json','Username':'bkashabbl','Password':'abbl@123'},
			success : function(response) {
				$('#submitBtn').prop('disabled', false);
				console.log (response);
				//alert (response[1].redirectUrl);
				//alert (response[0].status);
				//alert (response[2].message);
				//console.log (response);
				//spinning-div
				
				if (response[0].status=='warning'){
					//$(".error").html(response[2].message)
					$("#spinning-div").hide();
					$("#err-div").html(response[2].message).show();
					//$(".success").html("").hide();
					console.log (response);

				}else{
					//alert (response[1].redirectUrl)
					$("#spinning-div").hide();
					console.log ('URL : ' +response[1].redirectUrl )
					//alert (response[1].redirectUrl);
					$("#err-div").html(response[2].message).show();
					window.location.href = response[1].redirectUrl;
					//$.redirect(response[1].redirectUrl, {"Content-Type": "application/json", "Username":"bkashabbl","Password":"abbl@123"});
				}
				
				
                //$("." + response.type).html(response[1].redirectUrl)
				//$("." + response.type).show();
			},
			error : function() {
				alert("error");
			}
		});
	} else {
		$(".error").html('You have entered wrong OTP.')
		$(".error").show();
	}
}