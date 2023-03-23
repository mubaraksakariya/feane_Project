function sendotp(){
    phone = document.getElementById('mobile').value;
    document.getElementById('get_otp_error').innerHTML ="";
    const regex = /^(\+91|0)?[6789]\d{9}$/;
    if (regex.test(phone)){
        console.log(phone);
        document.getElementById('enter_otp').style.display = 'block';
        document.getElementById('get_otp').style.display = 'none'
        
    }
    else{
        document.getElementById('get_otp_error').innerHTML = "Enter valid number";
    }

}