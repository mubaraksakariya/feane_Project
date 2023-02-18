
const form = document.getElementById("RegForm");

form.addEventListener("submit", function(event) {
    event.preventDefault();
    let password1 = form.elements.namedItem('password1').value; 
    let password2 = form.elements.namedItem('password2').value; 
    let name = form.elements.namedItem('name').value; 
    let email = form.elements.namedItem('email').value; 
    let phone = form.elements.namedItem('number').value; 
    let phoneRegex = /^\d{10}$/;
    let emailRegex = /^[a-zA-Z0-9.!#$%&'*+/=?^_`{|}~-]+@[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?(?:\.[a-zA-Z0-9](?:[a-zA-Z0-9-]{0,61}[a-zA-Z0-9])?)*$/


    // if (!phoneRegex.test(phone)) {
    //     alert("Invalid phone number. Please enter a 10-digit phone numberrrrrrrrrrrr.");
    //     event.preventDefault();
    // }
    // if (!emailRegex.test(email)) {
    //     alert("Invalid email.");
    //     event.preventDefault();
    // }
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
          var user = JSON.parse(xhr.responseText)
          if (user.exist == "true"){
            document.getElementById('message').innerHTML = "Email already taken"
          }
          else{
            form.submit()
           }
        }
      };
    xhr.send("email=" + email);  
});


