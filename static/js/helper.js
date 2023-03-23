
const form = document.getElementById("RegForm");

form.addEventListener("submit", function(event) {
    event.preventDefault();
    let password1 = form.elements.namedItem('password1').value; 
    let password2 = form.elements.namedItem('password2').value; 
    let name = form.elements.namedItem('name').value; 
    let email = form.elements.namedItem('email').value; 
    let phone = document.getElementById('number').value; 
    let phoneRegex = /^(\+91?)?[0]?(91)?\d{10}$/;
    let emailRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/
    console.log(phone);
    if (!phoneRegex.test(phone)) {
        document.getElementById('message').innerHTML = "Invalid phone number. Please enter a 10-digit phone number."
        event.preventDefault();
        return false;
    }
    
    if (!emailRegex.test(email)) {
        document.getElementById('message').innerHTML = "Invalid email.";
        event.preventDefault();
        return false;
    }
    if (password1 != password2) {
        document.getElementById('message').innerHTML = "Passwords do not match"
        event.preventDefault();
        return false;
    }

    var xhr = new XMLHttpRequest();
    var csrf_token = document.getElementsByName("csrfmiddlewaretoken")[0].value;
    xhr.open("POST", "userexist", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.setRequestHeader("X-CSRFToken", csrf_token);
    xhr.onreadystatechange = function() {
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
          var response = JSON.parse(xhr.responseText)
          if (response.phone == "true"){
            console.log(response.phone);
            document.getElementById('message').innerHTML = "Phone number already taken"
          }
          else if (response.user == "true"){
            console.log(response.user);
            document.getElementById('message').innerHTML = "Email already taken"
          }
          else{
            form.submit()
           }
        }
      };
    xhr.send("email=" + email + "&phone_number="+phone);
});


