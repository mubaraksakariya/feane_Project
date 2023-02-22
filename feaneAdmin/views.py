from django.shortcuts import render,redirect
from customer.models import User
from store.models import Cart,Category,Order
from store.models import Product,Category,Images,Size
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.db.models import F



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

@admin_login_required
def editproduct(request,id):
    context = {
        'product' : Product.objects.get(id = id),
        'categories': Category.objects.all(),
        'sizes' : Size.objects.all()
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
            if images:
                image = Images.objects.filter(product = id)
                image.delete()
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
    Product.objects.get(id = id).delete()
    return redirect('inventory')
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
        categories = Category.objects.all()
        categories = categories.annotate(total = F('id')*1)
        for item in categories:
            total = Product.objects.filter(product_category = item.id).count()
            item.total = total
        context = {
            'categories':categories
        }
        return render(request,'categories.html',context)

@admin_login_required
def delete_category(request,id):
    category = Category.objects.get(id = id)
    category.delete()
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
            messages.info(request,'Size already exists')
        else:
            size = Size.objects.get(id = id)
            size.size_type = size_name
            size.save()
        return redirect('addsize')
    else:
        size = Size.objects.all()
        size = size.annotate(total = F('id')*1)
        for item in size:
            count = Product.objects.filter(product_size = item).count()
            item.total = count
        context = {
            'size':size,
        }
        return render(request,'size.html',context)

@admin_login_required
def deletesize(request,id):
    category = Size.objects.get(id = id)
    category.delete()
    return redirect('addsize')
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
        'admin':request.user
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



