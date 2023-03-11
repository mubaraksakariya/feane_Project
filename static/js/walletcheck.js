wallet_chekbox = document.getElementById('wallet-balance')
const paymenent_radio = document.getElementsByName('payment_method');
wallet_chekbox.addEventListener('change',function(e){
    total = document.getElementById('total')
    if (this.checked) {
        var wallet_balance = parseInt(this.value);
        var order_total = parseInt(total.value);
        document.getElementById('wallet-amount').value = wallet_balance
        if (wallet_balance >= order_total){
            for (let i = 0; i < paymenent_radio.length-1; i++) {
                paymenent_radio[i].disabled = true;
              }
            document.getElementById('wallet_radio').checked = true
            document.getElementById('wallet-amount').value = order_total
        }
        
    } 
    else {
        for (let i = 0; i < paymenent_radio.length-1; i++) {
            paymenent_radio[i].disabled = false;
            if (i==0)
            paymenent_radio[i].checked = true
            }
            document.getElementById('wallet-amount').value = 0   
        // do something if unchecked
    }
})