from django.shortcuts import render,redirect
from customer.models import User
from store.models import Cart,Category,Order
from store.models import Product,Category,Images,Size
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required



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
    context = {'admin':admin}
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
    products = Product.objects.all()
    admin = User.objects.get(email=request.user.email)
    context = {
        'products':products,
        'admin':admin
    }
    return render(request,'inventory.html',context=context)


############### Add Item ################

@admin_login_required
def additem(request):
    if request.method == 'POST':
        product_name = request.POST['product_name']
        product_prize = request.POST['product_prize']
        product_stock_amount = request.POST['product_stock_amount']
        product_text = request.POST['product_text']
        product_category = Category.objects.get(id = int(request.POST['category']))
        product_size = Size.objects.get(id = int(request.POST['size']))
        if int(product_stock_amount) > 1:
            product_available = True
        else:
            product_available = False
        image = Images.objects.create(image1 = request.FILES['image1'],image2 = request.FILES['image2'],image3 = request.FILES['image3'])
        product = Product.objects.create(
            product_name = product_name,
            product_stock_amount = product_stock_amount,
            product_prize = product_prize,
            product_text = product_text,
            product_available = product_available,
            product_category = product_category,
            product_image = image,
            product_size = product_size,
        )
        # product.save()
        return redirect('inventory')
    context = {
        'categories' : Category.objects.all(),
        'sizes' : Size.objects.all()
    }
    return render(request,'additem.html',context=context)

############## Add Category ##########################

@admin_login_required
def addcategory(request):
    if request.method == 'POST':
        category_name = request.POST['category']
        if not Category.objects.filter(category_name = category_name).exists():
            catogery = Category.objects.create(category_name = category_name)
        else:    
            messages.info(request,'Category already exists')
        return redirect('additem')

############## Add Size type ##########################

@admin_login_required
def addsize(request):
    if request.method == 'POST':
        category_name = request.POST['category']
        if not Size.objects.filter(size_type = category_name).exists():
            catogery = Size.objects.create(size_type = category_name)
        else:    
            messages.info(request,'Size already exists')
        return redirect('additem')

############## User Profiles at admin side #############

@admin_login_required
def users(request):
    users = User.objects.all().order_by('email')
    admin = request.user
    context = {
        'users' : users,
        'admin': admin,
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
    user.delete()
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

@admin_login_required
def show_orders(request):
    context = {
        'orders' : Order.objects.filter(order_processed = False),
    }
    return render(request,'orders.html',context=context)

@admin_login_required
def manage_order(request,id):
    order = Order.objects.get(id = id)
    context = {
        'cart' : order.cart.all(),
        'address': order.delivery_address,
        'user':User.objects.get(id = order.user.id),
        'order_id':id
    }
    return render(request,'order_detailes.html',context=context)


@admin_login_required
def accept_order(request,id):
    order = Order.objects.get(id = id)
    order.order_processed = True
    order.save()
    cart = order.cart.all()
    for item in cart:
        item.status = "accepted"
        item.save()
    return redirect('show_orders')



