
document.getElementById('blockbtn').addEventListener('click',function(e){
    e.preventDefault()
    popup = document.getElementById('blk-box')
    popup.style.display = 'block'  
})
document.getElementById('no').addEventListener('click',function(){
    popup = document.getElementById('blk-box')
    popup.style.display = 'none'
})

document.getElementById('dltbtn').addEventListener('click',function(e){
    e.preventDefault()
    popup = document.getElementById('dlt-box')
    popup.style.display = 'block' 
})
document.getElementById('nodel').addEventListener('click',function(){
    popup = document.getElementById('dlt-box')
    popup.style.display = 'none'
})

