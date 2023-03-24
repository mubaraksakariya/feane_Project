import json
from django.conf import settings
from django.shortcuts import render,redirect,HttpResponse
from django.views.decorators.cache import never_cache
from customer.models import User,Address,Wallet
from store.models import Order,Images,Coupon
from .models import Product,Category,Cart,Order,Payment,Anonymous_Cart
from django.contrib.auth.decorators import login_required
from django.http import FileResponse, HttpResponseRedirect, JsonResponse
from django.core.serializers import serialize
from django.db.models import ExpressionWrapper,F,FloatField
from django.contrib import messages
import razorpay
import requests
from django.views.decorators.csrf import csrf_exempt
from django.core.paginator import Paginator


### Store homepage #####################################

def store(request,id=None):
    cat = request.GET.get('item')
    if id is not None:
        category = Category.objects.get(id = id)
        products = Product.objects.filter(is_deleted = False,product_category = category).exclude(product_stock_amount__lte = 1).order_by('-updated_at')
        cat = id
    elif cat is not None and cat !='None':
        category = Category.objects.get(id = cat)
        products = Product.objects.filter(is_deleted = False,product_category = category).exclude(product_stock_amount__lte = 1).order_by('-updated_at')
    else:  
        products = Product.objects.filter(is_deleted = False).exclude(product_stock_amount__lte = 1).order_by('-updated_at')     
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user = request.user).exclude(purchased = True).count()
        request.session['cart_count'] = cart_count
    else:
        cart_count = Anonymous_Cart.objects.filter(session_id = request.session.session_key).count()
        request.session['cart_count'] = cart_count
    paginator = Paginator(products, 6)
    page_number = request.GET.get('page')
    products = paginator.get_page(page_number)
    context = {
        'products':products,
        'cart_count':cart_count,
        'category':Category.objects.all(),
        'item' : cat,
    }
    return render(request,"index.html",context=context)


def search(request):
    if request.method == 'POST':
        search_term =  request.POST['search-term']
    else:
        search_term =  request.GET.get('item')
    if search_term is None:
        search_term = ""
    products = Product.objects.filter(product_name__icontains = search_term).exclude(product_stock_amount__lte = 1).order_by('-updated_at')
    if request.user.is_authenticated:
        cart_count = Cart.objects.filter(user = request.user).exclude(purchased = True).count()
        request.session['cart_count'] = cart_count
    else:
        cart_count = Anonymous_Cart.objects.filter(session_id = request.session.session_key).count()
        request.session['cart_count'] = cart_count
    search_pages = Paginator(products, 6)
    page_number = request.GET.get('page')
    print(request.GET.get('page'))
    products = search_pages.get_page(page_number)
    
    context = {
        'products':products,
        'cart_count':cart_count,
        'item':search_term,
    }
    return render(request,"index.html",context=context)   

#### Product page ###############################

def product(request,id):
    product = Product.objects.get(id = id)
    images = Images.objects.filter(product = product)
    
    try:
        if request.user.is_authenticated:
            item_count = Cart.objects.get(product=product,user = request.user,purchased = False).quantity
        else:
            item_count = Anonymous_Cart.objects.get(product = product).quantity
    except:
        item_count = 1
    context = {
        'product': product,
        'user': request.user,
        'item_count':item_count,
        'images':images
    }
    return render(request,'product.html',context = context)

##########  Cart and Cart logic #########################
@never_cache
def cart(request):
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user = request.user.id,purchased = False)
        sum = 0
        for item in cart:
            sum = sum + (item.product.product_prize * item.quantity)
    else:
        cart = Anonymous_Cart.objects.filter(session_id = request.session.session_key)
        sum = 0
        for item in cart:
            sum = sum + (item.product.product_prize * item.quantity)
    context = {
        'cart' : cart,
        'sum':sum,      
    }
    return render(request,'cart.html',context=context)


@never_cache
def cartItems(request):
    if request.user.is_authenticated:
        id_list = Cart.objects.filter(user = request.user,purchased = False)
    else:
        id_list = Anonymous_Cart.objects.filter(session_id = request.session.session_key)
    id_list = list(id_list.values_list('product', flat=True))
    response_data = {'myList': id_list}
    return JsonResponse(response_data)

@never_cache
def addToCart(request,id=None):
    if request.method == 'POST':
        data = request.body.decode("utf-8")
        data = json.loads(data)
        product_id = data.get('product_id')
        print(product_id)
        quantity = data.get('quantity')
        product = Product.objects.get(id = product_id)
        try:
            if not Cart.objects.filter(user = request.user,product=product,purchased = False).exists():
                Cart.objects.create(user = request.user,product = product,quantity = 1)
                request.session['cart_count'] += 1
        except:
            if not Anonymous_Cart.objects.filter(session_id = request.session.session_key,product=product).exists():
                Anonymous_Cart.objects.create(session_id = request.session.session_key,product = product,quantity = 1)    
                request.session['cart_count'] += 1
        if request.user.is_authenticated:
            cartItem = Cart.objects.get(user = request.user,product=product,purchased = False)
        else:
            cartItem = Anonymous_Cart.objects.get(session_id = request.session.session_key,product=product)
        if(int(quantity) != 0):
            cartItem.quantity = int(quantity)
        cartItem.save()
        if request.user.is_authenticated:
            cart_count = Cart.objects.filter(user = request.user,purchased = False).count()
        else:
            cart_count = Anonymous_Cart.objects.filter(session_id = request.session.session_key).count()
        response = {
            'cart_count':cart_count,
        }
        return JsonResponse(response)
    else:
        return redirect('user_home')


@never_cache
def removefromcart(request,id):
    if request.user.is_authenticated:
        item = Cart.objects.get(id = id)
        request.session['cart_count'] -= 1
    else:
        item = Anonymous_Cart.objects.filter(id = id)
        request.session['cart_count'] -= 1
    item.delete()
    return redirect('cart')

@never_cache
@login_required(login_url='/signin')
def checkout(request): 
    cart = Cart.objects.filter(user = request.user.id,purchased = False)
    # cart = cart.annotate(total = ExpressionWrapper(F('product__product_prize') *F('quantity'),FloatField()))
    if cart.count() < 1:
        return redirect('cart')
    Total = 0
    for item in cart:
        Total = Total + item.total 
    wallet = Wallet.objects.filter(user = request.user)

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
        if not address_id:
            messages.info(request,'Please add a delivery address with the order')
            return redirect('checkout')
        payment_method = request.POST['payment']
        wallet_amount = int(request.POST['wallet-amount'])
        print(wallet_amount)
        coupon = request.POST['coupon']
        cart = Cart.objects.filter(user = request.user,purchased = False)
        amount = 0
        for item in cart:
            amount += item.total
        if payment_method == 'wallet':
            payment = Payment.objects.create(
                user = request.user,
                payment_type = 'wallet'
            )
            order = Order.objects.create(
                user = request.user,
                paid = True,
                payment_details = payment,
                delivery_address = Address.objects.get(id = address_id)     
            )
            wallet_entry = Wallet.objects.create(
                user = request.user,
                transaction_type = '3',
                amount = -(wallet_amount)
            )
            order.payment_details.payment_type = 'wallet'
            order.payment_details.payment_id = wallet_entry.id
            order.save()
            for item in cart:
                item.purchased = True
                item.save()
                product = Product.objects.get(id = item.product.id)
                product.product_stock_amount -= item.quantity
                product.save()
                order.cart.add(item)
            if Coupon.objects.filter(name = coupon, is_deleted = False).exists():
                coupon = Coupon.objects.get(name = coupon,is_deleted = False)
                order.coupon = coupon
                order.save()
            context = {
                'cart' : cart,
                'total' : order.discounted_total,
                'order' : order
            }
            return render(request,'order_confirmation.html',context)

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
            if wallet_amount > 0 :
                wallet_entry = Wallet.objects.create(
                    user = request.user,
                    transaction_type = '3',
                    amount = -(wallet_amount)
                )
                payment_details = order.payment_details
                payment_details.payment_type = 'cod + wallet'
                payment_details.payment_id = wallet_entry.id
                payment_details.wallet_transaction = wallet_entry
                payment_details.save()
                order.save()
            for item in cart:
                item.purchased = True
                item.save()
                product = Product.objects.get(id = item.product.id)
                product.product_stock_amount -= item.quantity
                product.save()
                order.cart.add(item)
            if Coupon.objects.filter(name = coupon, is_deleted = False).exists():
                coupon = Coupon.objects.get(name = coupon,is_deleted = False)
                order.coupon = coupon
                order.save()
            context = {
                'cart' : cart,
                'total' : order.amount_to_pay,
                'order' : order
            }
            return render(request,'order_confirmation.html',context)
        else:
            request.session['delivery_address'] = address_id
            request.session['wallet_amount'] = wallet_amount

            if Coupon.objects.filter(name = coupon, is_deleted = False).exists():
                coupon = Coupon.objects.get(name = coupon,is_deleted = False)
                amount *= (100 - coupon.discount)/100
                request.session['coupon'] = coupon.name
            client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_SECRET_KEY))
            data = { "amount": (amount - wallet_amount) *100, "currency": "INR", "receipt": "Online_Payment" }
            payment = client.order.create(data=data)
            context = {
                'YOUR_KEY_ID': settings.RAZORPAY_KEY_ID,
                'amount':(amount - wallet_amount) *100,
                'order_id' : payment['id'],
                'name':request.user.first_name,
                'email': request.user.email,
                'contact':request.user.phone_number,
            }
            return render(request,'payment.html',context)
    else:
        return redirect('user_home')

@never_cache
@csrf_exempt
@login_required(login_url='/signin')
def payment_callback(request,id):
    client = razorpay.Client(auth=(settings.RAZORPAY_KEY_ID,settings.RAZORPAY_SECRET_KEY))
    online_payment = client.payment.fetch(id)
    cart = Cart.objects.filter(user = request.user,purchased = False)
    amount = 0
    wallet_amount = request.session.get('wallet_amount')
    for item in cart:
        amount += item.total
    amount -= wallet_amount
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
        if wallet_amount > 0 and  request.user.wallet_balance >= wallet_amount:
                wallet_entry = Wallet.objects.create(
                    user = request.user,
                    transaction_type = '3',
                    amount = -(wallet_amount)
                )
                print("wallet used")
                payment_details = order.payment_details
                payment_type = payment_details.payment_type
                payment_details.payment_type = payment_type +"+"+ ' wallet'
                payment_details.wallet_transaction = wallet_entry
                payment_details.save()
                order.save()
        for item in cart:
                item.purchased = True
                item.save()
                product = Product.objects.get(id = item.product.id)
                product.product_stock_amount -= item.quantity
                product.save()
                order.cart.add(item)
        if 'coupon' in request.session:
            coupon = request.session['coupon']    
            coupon = Coupon.objects.get(name = coupon,is_deleted = False)
            order.coupon = coupon
            order.save()
           
        order.save()
        context = {
                'cart' : cart,
                'total': order.amount_to_pay,
                'order' : order
            }
        return render(request, 'order_confirmation.html',context)
    else:
        messages.info(request,"Payment Failed, Try Again")
        return redirect('checkout')


####### Order section #####################

@never_cache
@login_required(login_url='/signin')
def user_order(request,id = None):
    if id is not None:
        context = {
            'cart' : Order.objects.get(id = id).cart.all(),
            'orders'  : Order.objects.filter(user = request.user,order_processed = False),
            'id' : id,
            'order': Order.objects.get(id = id)
        }
    else:
        try:
            order = Order.objects.filter(user = request.user,order_processed = False).order_by('-order_modified')
            cart = order.first().cart.all()
            id = order.first().id
        except:
            cart = None
            id = None
        context = {
            'cart' : cart,
            'orders' : Order.objects.filter(user = request.user,order_processed = False),
            'id' : id,
            
        }
    return render(request,'user_orders.html',context)

@never_cache
@login_required(login_url='/signin')
def user_order_history(request,id = None):
    if id is not None:
        context = {
            'cart' : Order.objects.get(id = id).cart.all(),
            'orders'  : Order.objects.filter(user = request.user,order_processed = True).order_by('-order_modified'),
            'id' : id,
        }
    else:
        try:
            order = Order.objects.filter(user = request.user,order_processed = True).order_by('-order_modified')
            cart = order.first().cart.all()
            id = order.first().id
        except:
            print("error")
            cart = None
            id = None
        context = {
            'cart' : cart,
            'orders' : order,
            'id' : id
        } 
    return render(request,'user_order_history.html',context)

@never_cache
def cart_count_change(request):
    if request.method == 'POST':
        data = request.body.decode("utf-8")
        data = json.loads(data)
        cart_item_id = data.get('cart_item_id')
        count = data.get('count')
        if request.user.is_authenticated:
            cart_item = Cart.objects.get(id = cart_item_id)
            cart = Cart.objects.filter(user = request.user,purchased = False)
        else:
            cart_item = Anonymous_Cart.objects.get(id = cart_item_id)
            cart = Anonymous_Cart.objects.filter(session_id = request.session.session_key)
        cart_item.quantity = count
        cart_item.save()
        cart_total = 0
        cart_total = sum([item.total for item in cart])
        response = {
            'cart_count': cart_total,
        }
        return JsonResponse(response)

@never_cache
@login_required(login_url='/signin')
def wallet(request):
    wallet_page = Paginator(Wallet.objects.filter(user = request.user).order_by('-transaction_date'),10)
    page_number = request.GET.get('page')
    wallet = wallet_page.get_page(page_number)
    context = {
        'balance': request.user.wallet_balance,
        'wallet': wallet,
    }
    return render(request,'wallet.html',context)


@login_required(login_url='/signin')
def cancel_request(request,order_id):
    order = Order.objects.get(id = order_id)
    order.status = '0'
    order.save()
    
    return redirect('cart_in_order',order_id)

@login_required(login_url='/signin')
def check_coupon(request):
    if request.method == 'POST':
        coupon_string = request.POST['coupon_string']
        
        if Coupon.objects.filter(name = coupon_string,is_deleted = False).exists():
            cart = Cart.objects.filter(user = request.user, purchased = False)
            discount = Coupon.objects.get(name = coupon_string,is_deleted = False).discount
            total = 0
            for item in cart:
                total += item.total
            total *= (100-discount)/100
            response = {
                'exist': True,
                'total': total,
            }
        else:
            response = {
                'exist': False,
            }
        return JsonResponse(response)


@login_required(login_url='/signin')
def invoice(request,order_id):
    order = Order.objects.get(id = order_id)
    address = Address.objects.get(id = order.delivery_address.id)
    context = {
        'order': order,
        'user':request.user,
        'address' : address ,
        'cart' : order.cart.all()
    }
    return render(request,'invoice.html',context)

