import json
from django.shortcuts import render,redirect,HttpResponse
from customer.models import User,Address
from store.models import Order,Images
from .models import Product,Category,Cart,Order,Payment_method,Payment
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.core.serializers import serialize
from django.db.models import ExpressionWrapper,F,FloatField
from django.contrib import messages
# Create your views here.


### Store homepage #####################################
@login_required(login_url='/signin')
def store(request):
    products = Product.objects.all()
    cart_count = Cart.objects.filter(user = request.user).exclude(purchased = True).count()
    context = {
        'user': request.user.first_name,
        'products':products,
        'cart_count':cart_count,
    }
    return render(request,"index.html",context=context)

#### Product page ###############################
@login_required(login_url='/signin')
def product(request,id):
    product = Product.objects.get(id = id)
    images = Images.objects.filter(product = product)
    cart_count = Cart.objects.filter(user = request.user).exclude(purchased = True).count()
    try:
        item_count = Cart.objects.get(product=product,user = request.user,purchased = False).quantity
    except:
        item_count = 1
    context = {
        'product': product,
        'user': request.user,
        'cart_count':cart_count,
        'item_count':item_count,
        'images':images
    }
    return render(request,'product.html',context = context)

##########  Cart and Cart logic #########################
@login_required(login_url='/signin')
def cart(request):
    cart = Cart.objects.filter(user = request.user.id,purchased = False)
    cart_count = Cart.objects.filter(user = request.user).exclude(purchased = True).count()
    sum = 0
    for item in cart:
        sum = sum + (item.product.product_prize * item.quantity)
    context = {
        'cart' : cart,
        'cart_count':cart_count,
        'sum':sum,      
    }
    return render(request,'cart.html',context=context)

@login_required(login_url='/signin')
def addToCart(request,id=None):
    if request.method == 'POST':
        data = request.body.decode("utf-8")
        data = json.loads(data)
        product_id = data.get('product_id')
        quantity = data.get('quantity')
        print(product_id)
        product = Product.objects.get(id = product_id)
        if not Cart.objects.filter(user = request.user,product=product,purchased = False).exists():
            Cart.objects.create(user = request.user,product = product,quantity = 1)
        cartItem = Cart.objects.get(user = request.user,product=product,purchased = False)
        if(int(quantity) != 0):
            cartItem.quantity = int(quantity)
        cartItem.save()
        cart_count = Cart.objects.filter(user = request.user,purchased = False).count()
        response = {
            'cart_count':cart_count,
        }
        return JsonResponse(response)
    else:
        return redirect('user_home')


@login_required(login_url='/signin')
def removefromcart(request,id):
    item = Cart.objects.get(id = id)
    item.delete()
    return redirect('cart')

@login_required(login_url='/signin')
def checkout(request): 
    cart = Cart.objects.filter(user = request.user.id,purchased = False)
    cart = cart.annotate(total = ExpressionWrapper(F('product__product_prize') *F('quantity'),FloatField()))
    total = 0
    for item in cart:
        total = total + item.total 
    context = {
        'address' : Address.objects.filter(user = request.user),
            'cart':cart,
            'total':total
    }
    return render(request,'checkout.html',context=context)
@login_required(login_url='/signin')
def placeOrder(request):
    if request.method == 'POST':
        address_id = request.POST['address']
        if  not address_id:
            messages.info(request,'Please add a delivery address with the order')
            return redirect('checkout')
        payment_method = request.POST['payment']
        cart = Cart.objects.filter(user = request.user,purchased = False)
        amount = 0
        for item in cart:
            amount += item.product.product_prize * item.quantity
        
        if payment_method == 'cod':
            if not Payment_method.objects.filter(user = request.user,name = 'cod').exists():
                payment_type = Payment_method.objects.create(
                    user = request.user,
                    name = 'cod'
                )
            else:
                payment_type = Payment_method.objects.get(user = request.user,name = 'cod')
            payment = Payment.objects.create(
                user = request.user,
                amount = amount,
                payment_type = payment_type
            )         
            order = Order.objects.create(
                user = request.user,
                paid = True,
                payment_details = payment,
                delivery_address = Address.objects.get(id = address_id)     
            )
            for item in cart:
                item.purchased = True
                item.save()
                product = Product.objects.get(id = item.product.id)
                product.product_stock_amount -= item.quantity
                product.save()
                order.cart.add(item)
                
        context = {
            'cart' : cart
        }
        return render(request,'order_confirmation.html',context)
    else:
        return redirect('user_home')

@login_required(login_url='/signin')
def user_order(request,id = None):
    if id is not None:
        context = {
            'cart' : Order.objects.get(id = id).cart.all(),
            'orders'  : Order.objects.filter(user = request.user,order_processed = False),
        }
    else:
        context = {
            'cart' : None,
            'orders' : Order.objects.filter(user = request.user,order_processed = False)
        } 
    return render(request,'user_orders.html',context)