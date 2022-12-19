let timerOn = true;
function timer(remaining) {
  var m = Math.floor(remaining / 60);
  var s = remaining % 60;
  m = m < 10 ? "0" + m : m;
  s = s < 10 ? "0" + s : s;
  document.getElementById("countdown").innerHTML = `OTP has been sent to your mobile. It will expire in ${m}m${s}s`;
  remaining -= 1;

  if (remaining==0){
    
      document.getElementById("resend").innerHTML = 'Click Resend Button. ';
      document.getElementById("resendBtn").disabled=false;
  }

  if (remaining >= 0 && timerOn) {
    setTimeout(function () {
      timer(remaining);
    }, 1000);
   
    return;
  }
  if (!timerOn) {
    return;
  }
  /*document.getElementById("resend").innerHTML = `Don't receive the code?
  <a class="btn btn-primary" href="#" role="button" onclick="timer(120)">Resend</a> 
 `;*/
}
timer(otp_expire_time);
