
from collections import defaultdict
from itertools import count
import json
from django.http import JsonResponse
from django.shortcuts import render,redirect
from urllib3 import HTTPResponse
from customer.models import User,Wallet,Message
from store.models import Cart,Category,Order,Coupon
from store.models import Product,Category,Images,Size
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F
from django.db.models import Q
import pytz
from datetime import datetime
from django.core.paginator import Paginator
from django.db.models import Sum,Count
from datetime import datetime
from .models import Notification


###############
from django.http import HttpResponse
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle,Paragraph
from io import BytesIO

###########

## Admin login required Decorator###########
def admin_login_required(view_func, redirect_url="admin_signin"):
    def wrapper(request, *args, **kwargs):
        if request.user.is_authenticated and request.user.is_superuser:
            return view_func(request,*args, **kwargs)
        elif request.user.is_authenticated:
            return redirect('user_home')
        else:
            messages.info(request,"Your credentials dose not meet the admin privilages")
            return redirect(redirect_url)
    return wrapper

# Admin Home##########################

@admin_login_required
def adminHome(request): 
    admin = request.user
    orders = Order.objects.all()
    total_sale = sum([order.total for order in orders])
    low_items = Product.objects.filter(product_stock_amount__lt=15, is_deleted = False).order_by('product_stock_amount')[:3]
    low_items = low_items.annotate(total_sale = Sum('cart__quantity'))

    context = {
        'admin':admin,
        'total_sale':total_sale,
        'low_items': low_items,
        'order':orders

    }
    return render(request,"admin.html",context=context)
    

############### signinin / signout ################# 
def signin(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request,email=email,password=password)
        if user is not None and user.is_superuser:
            login(request,user)
            return redirect('admin_home')
        else:
            messages.info(request,'credentials are not matching')
            return redirect('admin_signin')      
    elif not request.user.is_authenticated:
        return render(request,'adminsignin.html')
    else:
        return redirect('admin_home')
def signout(request):
    logout(request)
    return redirect('admin_signin')

############## inventory ##################

@admin_login_required
def inventory(request):
    product =  Product.objects.filter(is_deleted = False).order_by('-updated_at')
    paged_product = Paginator(product, 7) 
    page_number = request.GET.get('page')
    product = paged_product.get_page(page_number)
    context = {
        'products':product,
        'item' : 'product',
    }
    return render(request,'inventory.html',context=context)

@admin_login_required
def editproduct(request,id):
    product = Product.objects.get(id = id)
    images = Images.objects.filter(product = product)
    print(images)
    context = {
        'product' : product ,
        'categories': Category.objects.all().exclude(id = Product.objects.get(id = id).product_category.id ),
        'sizes' : Size.objects.all().exclude(id = Product.objects.get(id = id).product_size.id),
        'images' : images,
    }  
    return render(request,'editproduct.html',context)


@admin_login_required
def additem(request,id = None):
    if request.method == 'POST':
        id = request.POST.get('id')
        product_name = request.POST.get('product_name')
        product_prize = request.POST.get('product_prize')
        product_stock_amount = request.POST.get('product_stock_amount')
        product_text = request.POST.get('product_text')
        images = request.FILES.getlist('images')
        try:
            product_category = Category.objects.get(id = int(request.POST.get('category')))
        except:
            product_category = None
        try:
            product_size = Size.objects.get(id = int(request.POST.get('size')))
        except:
            product_size = None
        if int(product_stock_amount) > 1:
            product_available = True
        else:
            product_available = False
        if id is not None:
            product = Product.objects.get(id = id)
            product.product_name = product_name
            product.product_prize = product_prize
            product.product_stock_amount = product_stock_amount
            product.product_text = product_text
            if product_category is not None:
                product.product_category = product_category
            if product_size is not None:
                product.product_size = product_size
            product.product_available = product_available
            product.save()
            # if images:
            #     image = Images.objects.filter(product = id)
            #     image.delete()
            for image in images:
                    image = Images.objects.create(product=product,image = image) 
        else:
            product = Product.objects.create(
                product_name = product_name,
                product_stock_amount = product_stock_amount,
                product_prize = product_prize,
                product_text = product_text,
                product_available = product_available,
                product_category = product_category,
                product_size = product_size,
            )
            for image in images:
                image = Images.objects.create(product=product,image = image)
            # product.save()       
        return redirect('inventory')
    context = {
        'categories' : Category.objects.all(),
        'sizes' : Size.objects.all()
    }
    return render(request,'additem.html',context=context)

@admin_login_required
def deleteitem(request,id):
    product = Product.objects.get(id = id)
    product.is_deleted=True
    product.save()
    return redirect('inventory')

def delete_image(request,id):
    image = Images.objects.get(id = id)
    image.delete()
    data = {
        'message': f'Photo with ID {id} deleted successfully',
    }
    return JsonResponse(data)

############## Add Category ##########################

@admin_login_required
def addcategory(request,id = None):
    if request.method == 'POST':
        category_name = request.POST['category']
        try:
            id = request.POST['id']
        except:
            id = None    
        if not Category.objects.filter(category_name = category_name).exists() and id is None:
            catogery = Category.objects.create(category_name = category_name)
        elif id is None:
            category = Category.objects.get(category_name = category_name)
            category.is_deleted = False
            category.save()
            messages.info(request,'Category already exists')
        else:
            category = Category.objects.get(id = id)
            cat_old = category.category_name
            if cat_old != category_name and bool(category_name.strip()):
                category.category_name = category_name
                category.save()
            return redirect('addcategory')
        return redirect('addcategory')
    else:
        categories = Category.objects.filter(is_deleted = False).order_by('-updated_at')
        categories = categories.annotate(total = F('id')*1)
        paginator = Paginator(categories, 7)
        page_number = request.GET.get('page')
        categories = paginator.get_page(page_number)
        for item in categories:
            total = Product.objects.filter(product_category = item.id).count()
            item.total = total
        context = {
            'categories':categories,
            'item' : 'category',
        }
        return render(request,'categories.html',context)

@admin_login_required
def delete_category(request,id):
    category = Category.objects.get(id = id)
    category.is_deleted = True
    category.save()
    return redirect('addcategory')

############## Add Size type ##########################

@admin_login_required
def addsize(request,id=None):
    if request.method == 'POST':
        size_name = request.POST['size']
        try:
            id = request.POST['id']
        except:
            id = None
        print(id)
        print(size_name)
        if not Size.objects.filter(size_type = size_name).exists() and id == None:
            size = Size.objects.create(size_type = size_name)
        elif id == None:
            size = Size.objects.get(size_type = size_name)
            size.is_deleted = False
            size.save()
            messages.info(request,'Size already exists')
        else:
            size = Size.objects.get(id = id)
            if bool(size_name.strip()): 
                size.size_type = size_name
                size.save()
        return redirect('addsize')
    else:
        size = Size.objects.filter(is_deleted = False).order_by('updated_at')
        size = size.annotate(total = F('id')*1)
        paginator = Paginator(size, 7) # 10 objects per page
        page_number = request.GET.get('page')
        size = paginator.get_page(page_number)
        for item in size:
            count = Product.objects.filter(product_size = item).count()
            item.total = count
        context = {
            'size':size,
            'item': 'size',
        }
        return render(request,'size.html',context)

@admin_login_required
def deletesize(request,id):
    size = Size.objects.get(id = id)
    size.is_deleted = True
    size.save()
    return redirect('addsize')

############## User Profiles at admin side #############

@admin_login_required
def users(request):
    users = User.objects.filter(blocked = False,is_deleted = False).exclude(is_superuser = True).order_by('-updated_at')
    paginator = Paginator(users, 7) # 10 objects per page
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    context = {
        'users' : users,
        'blocked':'False',
    }
    return render(request,'users.html',context=context)

@admin_login_required
def blocked_users(request):
    users = User.objects.filter(blocked = True).order_by('-updated_at')
    paginator = Paginator(users, 7) # 10 objects per page
    page_number = request.GET.get('page')
    users = paginator.get_page(page_number)
    context = {
        'users' : users,
        'blocked':'True',
    }
    return render(request,'users.html',context=context)

@admin_login_required
def user_update(request,id):
    user = User.objects.get(id = id)
    if request.method == 'POST':
        name = request.POST['name']
        number = request.POST['number']
        email = request.POST['email']
        if name != user.first_name and bool(name.strip()):
            user.first_name = name
        if number != user.phone_number and bool(number.strip()):
            user.phone_number = number
        if email != user.email and bool(email.strip()):
            user.email = email
        user.save()
        return redirect('users')
    else:
        admin = User.objects.get(email=request.user.email)
        context = {
            'admin' : admin,
            'user' : user,
        }
        return render(request,'user_update.html',context=context)

@admin_login_required
def delete_profile(request,id):
    user = User.objects.get(id = int(id))
    user.is_deleted = True
    user.save()
    return redirect('users')

@admin_login_required
def block_user(request,id):
    user = User.objects.get(id = int(id))
    user.blocked = True
    user.save()
    return redirect('users')

@admin_login_required
def unblock_user(request,id):
    user = User.objects.get(id = int(id))
    user.blocked = False
    user.save()
    return redirect('users')

###### orders management at admin side ###############################

@admin_login_required
def show_orders(request):
    orders = Order.objects.filter(order_processed = False).order_by('-order_created')
    paged_orders = Paginator(orders, 7) 
    page_number = request.GET.get('page')
    order = paged_orders.get_page(page_number)
    context = {
        'orders' : order,
        'admin':request.user,
        'order_processed': 'False', 
    }
    return render(request,'orders.html',context=context)

@admin_login_required
def all_orders(request):
    orders = Order.objects.filter(order_processed = True).order_by('-order_created')
    paged_orders = Paginator(orders, 7) 
    page_number = request.GET.get('page')
    order = paged_orders.get_page(page_number)
    context = {
        'orders' : order,
        'admin':request.user,
        'order_processed': 'True', 
    }
    return render(request,'orders.html',context=context)

@admin_login_required
def manage_order(request,id):
    order = Order.objects.get(id = id)
    context = {
        'cart' : order.cart.all(),
        'address': order.delivery_address,
        'user':User.objects.get(id = order.user.id),
        'order_id':id,
        'order' : order,

    }
    return render(request,'order_detailes.html',context=context)

@admin_login_required
def accept_order(request,id):
    order = Order.objects.get(id = id)
    if int( order.status) > 3:
        cart = order.cart.all()
        order.order_processed = True
        order.save()
        for item in cart:
            item.status = "accepted"
            item.save()
        order.status = str(int(order.status)+1)
        order.save()
        return redirect('show_orders')
    order.status = str(int(order.status)+1)
    order.save()
    print(order.order_processed)
    print(order.status)
    return redirect('manage_order',id)

@admin_login_required
def update_order_status(request,id):
    order = Order.objects.get(id = id)
    order.status = '1'
    order.save()
    print(order.status)
    print(order.get_status_display())
    return redirect('manage_order',id)

@admin_login_required
def cancel_order(request,order_id):
    order = Order.objects.get(id = order_id)
    if order.payment_details.payment_type != 'cod':
        wallet = Wallet.objects.create(user = order.user,amount = order.total)
        wallet = Wallet.objects.create(user = request.user,amount = -1 * order.total)
    order.order_processed = True
    order.status = '6'
    order.save()
    return redirect('all_orders')

@admin_login_required
def refuse_order(request):
    if request.method == 'POST':
        order_id = request.POST['order_id']
        message = request.POST['message']
        heading = request.POST['heading']
        order = Order.objects.get(id = order_id)
        user = order.user
        order.status = '7'
        order.order_processed = True
        
        message = Message.objects.create(
            user = user,
            heading = heading,
            text = message,
            sender = request.user
        )
        waller_entry = Wallet.objects.create(
            user = user,
            transaction_type = '5',
            amount = order.amount_to_pay,
            order = order,
        )
        order.save()
    return redirect('manage_order',order_id)


############ serach admin side #####################

@admin_login_required
def adminside_search(request):
    if request.method == 'POST':
        search_string = request.POST.get('search_string') 
        item = request.POST['item']
        order_processed = request.POST.get('order_processed')
        blocked = request.POST.get('blocked')
    else:
        search_string = request.GET.get('search_string') 
        item = request.GET.get('item')
        order_processed = request.GET.get('order_processed')
        blocked = request.POST.get('blocked')

    if item == 'product':
        product = Product.objects.filter(product_name__icontains = search_string,is_deleted = False).order_by('-updated_at')
        paged_product = Paginator(product, 7) 
        page_number = request.GET.get('page')
        product = paged_product.get_page(page_number)
       
        context = {
            'products': product,
            'search_string':search_string,
        }
        return render(request,'inventory.html',context)
    if item == 'category':
        categories = Category.objects.filter(category_name__icontains = search_string,is_deleted = False).order_by('-updated_at')
        categories = categories.annotate(total = F('id')*1)
        paged_product = Paginator(categories, 7) 
        page_number = request.GET.get('page')
        categories = paged_product.get_page(page_number)
        for item in categories:
            total = Product.objects.filter(product_category = item.id).count()
            item.total = total
        context = {
            'categories':categories,
            'search_string':search_string,
        }
        return render(request,'categories.html',context)
    if item == 'size':
        size = Size.objects.filter(size_type__icontains = search_string,is_deleted = False)
        size = size.annotate(total = F('id')*1)
        paged_product = Paginator(size, 7) 
        page_number = request.GET.get('page')
        size = paged_product.get_page(page_number)
        for item in size:
            count = Product.objects.filter(product_size = item).count()
            item.total = count
        context = {
            'size':size,
            'search_string':search_string,
        }
        return render(request,'size.html',context)
    if item == 'user':
        users = User.objects.filter(Q(first_name__icontains = search_string) |  Q(email__icontains = search_string),is_deleted = False,blocked=blocked,is_superuser = False).order_by('-updated_at')
        paginator = Paginator(users, 7) # 10 objects per page
        page_number = request.GET.get('page')
        users = paginator.get_page(page_number)
        context = {
            'users' : users,
            'search_string':search_string,
            'blocked':blocked,
        }
        return render(request,'users.html',context=context)

    if item == 'coupon':
        coupon = Coupon.objects.filter(name__icontains = search_string, is_deleted = False).order_by('-created_at')
        paginator = Paginator(coupon, 7) # 10 objects per page
        page_number = request.GET.get('page')
        coupon = paginator.get_page(page_number)
        context = {
            'coupon' : coupon,
        }
        return render(request,'coupons.html',context=context)
    if item == 'order':
        orders = Order.objects.filter(Q(id__icontains = search_string) |  Q(payment_details__payment_type__icontains = search_string) | Q(order_modified__icontains = search_string),order_processed = order_processed).order_by('-order_created')
        paged_orders = Paginator(orders, 7) 
        page_number = request.GET.get('page')
        order = paged_orders.get_page(page_number)
        context = {
            'orders' : order,
            'search_string':search_string,
            'order_processed':order_processed
        }
        return render(request,'orders.html',context=context)
    

########## Coupon ##################

@admin_login_required
def coupons(request):
    if request.method == 'POST':
        coupon_string = request.POST['coupon']
        discount = request.POST['discount']
        if not Coupon.objects.filter(name = coupon_string,is_deleted = False).exists():
            new_coupon = Coupon.objects.create(name = coupon_string,discount = discount)
            response = {
                'done':True,
                'id':new_coupon.id,
            }
        else:
             response = {
                'done':False,
                'message':"Coupon string alredy exists"
            }
        return JsonResponse(response)
    else:
        coupon = Coupon.objects.filter(is_deleted = False).order_by('-created_at')
        paginator = Paginator(coupon, 7) # 10 objects per page
        page_number = request.GET.get('page')
        coupon = paginator.get_page(page_number)
        context = {
            'coupon' : coupon,

        }
        return render(request,'coupons.html',context)

@admin_login_required
def edit_coupon(request):
    if request.method == 'POST':
        id = request.POST['coupon_id']
        coupon_string = request.POST['coupon']
        discount = request.POST['discount']
        coupon = Coupon.objects.get(id = id)
        response = dict
        if not Coupon.objects.filter(name = coupon_string,is_deleted = False).exists() and coupon_string.strip():
            coupon.name = coupon_string
            coupon.discount = discount
            coupon.save()
            response = {
                'message':'Coupon Updated',
                'done':True,
            }
        else:
            coupon.discount = discount
            coupon.save()
            response = {
                'message':'Coupon code cannot be applied, check if it already exists or empty',
                'done':False,
            }
        return JsonResponse(response)

@admin_login_required
def delete_coupon(request):
    if request.method == 'POST':
        id = request.POST['coupon_id']
        coupon = Coupon.objects.get(id = id)
        coupon.is_deleted = True
        coupon.save()
        response = {
            'done':True,
        }
        return JsonResponse(response)

########## Sales Reports ##############

@admin_login_required
def product_sale_status(request):
    data = json.loads(request.body)
    product_counts = Cart.objects.filter(
        Q(updated_at__gte = data['startdate']) & 
        Q(updated_at__lte = data['enddate'])
        ,purchased = True).annotate(total_quantity=Sum('quantity')).distinct()
    product_counts = list(product_counts.values_list('product__product_name', 'total_quantity'))
    product_count = {}
    for item in product_counts:
        key, value = item   
        if key in product_count:
            product_count[key] += value      
        else:
            product_count[key] = value
    return JsonResponse(product_count)


@admin_login_required
def sales_report(request):
    orders = Paginator(Order.objects.all().exclude(status = 0),10)
    page_number = request.GET.get('page')
    order = orders.get_page(page_number)
    context = {
        'order' : Order.objects.all().exclude(status = 0),
    }
    return render(request,'sales_table.html',context)


@admin_login_required
def payment_chart(request):
    if request.method == 'POST':
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        print(start_date)
        print(end_date)
        payment_type_count = Order.objects.filter(
            Q(order_created__lte = end_date) & Q(order_created__gte = start_date)
        ).values('payment_details__payment_type').annotate(count=Count('payment_details__payment_type'))
        payment_type_count = {item['payment_details__payment_type']:item['count'] for item in payment_type_count}
        list1 = {'cod':25,'upi':15}
        list2 = [25,15]
        data = {
            'list1': payment_type_count,
        }
        return JsonResponse(data)
    context = {
        'list1':['cod','upi'],
        'list2' : [25,15],
    }
    return render(request,'payment_reports.html',context)


@admin_login_required
def category_sale(request):
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')
    category = defaultdict(int)
    orders = Order.objects.filter(
        Q(order_created__lte = end_date ) & 
        Q(order_created__gte = start_date),
        order_processed = True
    )
    for order in orders:
        cart = order.cart.all()
        for item in cart:
            category[item.product.product_category.category_name] += item.total
    print(category)
    return JsonResponse(category)

############## Messages to Users ########################

@admin_login_required
def message_all_users(request):
    if request.method == 'POST':
        heading = request.POST['heading']
        text = request.POST['text']
        ntf = Notification.objects.create(heading = heading,text = text)
        if 'image' in request.FILES:
            image = request.FILES['image']
            ntf.image = image    
        ntf.save()
        return redirect('users')
    return render(request,'message_all.html')

