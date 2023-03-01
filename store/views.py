import json
from django.conf import settings
from django.shortcuts import render,redirect,HttpResponse
from customer.models import User,Address
from store.models import Order,Images
from .models import Product,Category,Cart,Order,Payment
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, JsonResponse
from django.core.serializers import serialize
from django.db.models import ExpressionWrapper,F,FloatField
from django.contrib import messages
import razorpay
import requests
from django.views.decorators.csrf import csrf_exempt
# Create your views here.


### Store homepage #####################################
@login_required(login_url='/signin')
def store(request):
    products = Product.objects.filter(is_deleted = False)
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
def cartItems(request):
    id_list = Cart.objects.filter(user = request.user,purchased = False)
    id_list = list(id_list.values_list('product', flat=True))
    response_data = {'myList': id_list}
    return JsonResponse(response_data)

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
    # cart = cart.annotate(total = ExpressionWrapper(F('product__product_prize') *F('quantity'),FloatField()))
    Total = 0
    for item in cart:
        Total = Total + item.total 
    context = {
        'address' : Address.objects.filter(user = request.user),
            'cart':cart,
            'total':Total
    }
    return render(request,'checkout.html',context=context)


########### Placing order and Payments##############

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
            amount += item.total
        
        if payment_method == 'cod':
            payment = Payment.objects.create(
                user = request.user,
                payment_type = 'cod'
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
            request.session['delivery_address'] = address_id
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_SECRET_KEY))
            data = { "amount": amount*100, "currency": "INR", "receipt": "Online_Payment" }
            payment = client.order.create(data=data)
            context = {
                'YOUR_KEY_ID': settings.RAZORPAY_KEY_ID,
                'amount':amount*100,
                'order_id' : payment['id'],
                'name':request.user.first_name,
                'email': request.user.email,
                'contact':request.user.phone_number,
            }
            return render(request,'payment.html',context)
    else:
        return redirect('user_home')

@csrf_exempt
def payment_callback(request,id):
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_SECRET_KEY))
    online_payment = client.payment.fetch(id)
    cart = Cart.objects.filter(user = request.user,purchased = False)
    amount = 0
    for item in cart:
        amount += item.total
    delivery_address = Address.objects.get(id = request.session.get('delivery_address'))
    if online_payment['status'] != 'failed':
        payment = Payment.objects.create(
                user = request.user,
                payment_type = online_payment['method'],
                payment_id = online_payment['id']
        )
        order = Order.objects.create(
                user = request.user,
                paid = True,
                payment_details = payment,
                delivery_address = delivery_address
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
        return render(request, 'order_confirmation.html',context)
    else:
        messages.info(request,"Payment Failed, Try Again")
        return redirect('checkout')




@login_required(login_url='/signin')
def user_order(request,id = None):
    if id is not None:
        context = {
            'cart' : Order.objects.get(id = id).cart.all(),
            'orders'  : Order.objects.filter(user = request.user,order_processed = False),
            'id' : id,
        }
    else:
        try:
            cart = Order.objects.filter(user = request.user,order_processed = False).first().cart.all()
            id = cart.id
            print(id)
        except:
            cart = None
            id = None

        context = {
            'cart' : cart,
            'orders' : Order.objects.filter(user = request.user,order_processed = False),
            'id' : id
        } 
    return render(request,'user_orders.html',context)


@login_required(login_url='/signin')
def user_order_history(request,id = None):
    if id is not None:
        context = {
            'cart' : Order.objects.get(id = id).cart.all(),
            'orders'  : Order.objects.filter(user = request.user,order_processed = True),
            'id' : id,
        }
    else:
        try:
            cart = Order.objects.filter(user = request.user,order_processed = True).first().cart.all()
            id = cart.id
        except:
            cart = None
            id = None
        context = {
            'cart' : cart,
            'orders' : Order.objects.filter(user = request.user,order_processed = True),
            'id' : id
        } 
    return render(request,'user_order_history.html',context)

@login_required(login_url='/signin')
def cart_count_change(request):
    if request.method == 'POST':
        data = request.body.decode("utf-8")
        data = json.loads(data)
        cart_item_id = data.get('cart_item_id')
        count = data.get('count')
        cart_item = Cart.objects.get(id = cart_item_id)
        cart_item.quantity = count
        cart_item.save()

        cart = Cart.objects.filter(user = request.user,purchased = False)
        cart_total = 0
        cart_total = sum([item.total for item in cart])
        response = {
            'cart_count': cart_total,
        }
        return JsonResponse(response)