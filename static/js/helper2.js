// THIS JS IS FOR THE ADD to CART process
// ------------------------------------------//

// add to cart-  xhr to connect to server
function addToCart(){
    let product_id = document.querySelector("#product_id").value
    let quantity = document.getElementById('quantity').value
    
    let csrf_token = document.getElementsByName("csrfmiddlewaretoken")[0].value;

    data = JSON.stringify({'product_id': product_id, 'quantity': quantity})
    var xhr = new XMLHttpRequest();
    xhr.open("POST", "/store/addToCart", true);
    xhr.setRequestHeader("Content-Type", "application/x-www-form-urlencoded");
    xhr.setRequestHeader("X-CSRFToken", csrf_token);
    xhr.onreadystatechange = function() {      
        if (xhr.readyState === XMLHttpRequest.DONE && xhr.status === 200) {
            var response = JSON.parse(xhr.responseText); 
            console.log(response.status);
            document.getElementById('cart_count').innerHTML = response.cart_count
            console.log(response.cart_count);
        };
    }
    xhr.send(data);
}

