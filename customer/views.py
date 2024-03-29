from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth import authenticate,login,logout
from django.views.decorators.cache import never_cache
from django.contrib import messages
from twilio.rest import Client
import vonage
from .models import User,Address
from store.models import Order, Product,Anonymous_Cart,Cart
import random
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.utils import timezone
from .models import Message
from feaneAdmin.models import Notification

OTP = 123
# Create your views here.

# to home page###################
def index(request):
    return redirect('/store')


# to send otp###########################

def send_otp(phone_number,OTP):
    client = vonage.Client(key="a0b774ff", secret="bwrmUdsVg0fhSuGI")
    sms = vonage.Sms(client)
    responseData = sms.send_message(
        {
            "from": "Vonage APIs",
            "to": phone_number,
            "text": f"Enter this OTP  {OTP}",
        }
    )

    if responseData["messages"][0]["status"] == "0":
        print("Message sent successfully.")
        print(OTP)
    else:
        print(f"Message failed with error: {responseData['messages'][0]['error-text']}")


# to sign up###########################

def userexist(request):
    email = request.POST.get('email','')
    phone = request.POST.get('phone_number')
    print(phone)
    print(email)
    if len(phone) == 10:
        phone = "+91" + phone.replace(" ", "")
    if not phone.startswith("+"):
        phone = "+" + phone.replace(" ", "")
    user = User.objects.filter(email=email).exists()
    print(phone)
    phone = User.objects.filter(phone_number=phone).exists()
    print(phone)
    if user:
        response = {
            'user': 'true',
        }
    else:
        response = {
            'user': 'false',
        }
    if phone:
        response.update({'phone': 'true'})
    else:
        response.update({'phone':'false'})
    return JsonResponse(response)   

def user_signup(request):
    if request.method == 'POST':
        name = request.POST['name']
        number = request.POST['number']
        email = request.POST['email']
        password = request.POST['password1']
        password2 = request.POST['password2']
        user = User.objects.filter(email=email).exists()
        if not user:
            user = User.objects.create_user(email = email,password = password,first_name = name,phone_number = number)
            user = User.objects.get(email=email)
            response = redirect('otp_check',user.id)
            response.set_cookie('return_url',request.path_info,max_age=100)
            return response
        else:
            messages.info(request,'Email already exists')
            return render(request,'signup.html')
    elif not request.user.is_authenticated:
        return render(request,'signup.html')
    else:
        return redirect('/')


def otp_check(request,id):
    user = User.objects.get(id = id)
    return_url = request.COOKIES.get('return_url')
    if request.method == 'POST':
        val = request.POST['OTP']      
        if val == str(user.otp):
            user.phone_number_verified = True
            user.otp = None
            user.save()

            if request.user.is_authenticated:
                return redirect(return_url)
            else:
                return redirect('signin')
        else:
            messages.info(request,'OTP is not correct, try again')
            return render(request,'otp_check.html')
    elif not user.phone_number_verified:
        OTP = random.randrange(111111, 999999)
        user.otp = OTP
        user.save()
        print(user.id)
        send_otp(user.phone_number,OTP=OTP)
        context = {
            'user' : user,
        }
        response = render(request,'otp_check.html',context)
        return response
    else:
        return redirect(return_url)

# Log in##########################
def user_signin(request):
    if request.method == 'POST':
        email = request.POST['email']
        password = request.POST['password']
        user = authenticate(request,email=email,password=password)
        if user is not None and  user.blocked:
            messages.info(request,f'{email}  your account is suspended temporarily')
            return redirect('signin')
        elif user is not None and user.phone_number_verified is False:
            OTP = random.randrange(111111, 999999)
            user = User.objects.get(id = user.id)
            user.otp = OTP
            user.save()
            send_otp(user.phone_number,OTP=OTP)
            context = {
            'user' : user,
            }
            response = render(request,'otp_check.html',context)
            response.set_cookie('return_url',request.path)
            return response
        elif user is not None:
            anonymous_Cart = Anonymous_Cart.objects.filter(session_id = request.session.session_key)
            login(request,user)
            cart = Cart.objects.filter(user = request.user, purchased = False)
            user_product_list = [item.product for item in cart]
            ano_product_list = [item.product for item in anonymous_Cart]
            for item in anonymous_Cart:
                if item.product in user_product_list:
                    cart_item = Cart.objects.get(user = request.user, purchased = False,product = item.product)
                    cart_item.quantity = item.quantity
                    cart_item.save()
                else:
                    Cart.objects.create(user = request.user, product = item.product, quantity = item.quantity)
            anonymous_Cart.delete()
            return redirect('/')
        else:
            messages.info(request,f'Invalid credential')
        context = {
            'email': email
        }
        return render(request,'signin.html',context)
    elif not request.user.is_authenticated:    
        return render(request,'signin.html')
    else:
        return redirect('/')    

@never_cache
@login_required(login_url='signin')
def user_profile(request):
    address = Address.objects.filter(user = request.user)
    now = timezone.now()
    
    for item in address:
        if not Order.objects.filter(user = request.user,delivery_address = item,order_processed = False).exists() and (now.date() - item.last_modified).days > 30 and item.disabled == True:
            item.delete()
    context = {
        'user' : request.user,
        'address': Address.objects.filter(user = request.user,disabled = False)
    }
    return render(request,'profile.html',context=context)

@never_cache
@login_required(login_url='signin')   
def profile_update(request,id):
    user = User.objects.get(id = id)
    old_number = user.phone_number
    old_email = user.email
    if request.method == 'POST':
        name = request.POST['name']
        number = request.POST['number']
        email = request.POST['email']
        if name != user.first_name and bool(name.strip()):
            user.first_name = name
        if email != user.email and bool(email.strip()) and not User.objects.filter(email=email).exists():
            user.email = email
        elif  old_email != email:
            messages.info(request,'email already taken, try something else')
        if number != user.phone_number and bool(number.strip()):
            user.phone_number = number
        user.save()
        if old_number != number:
            user.phone_number_verified = False
            user.save()
            return_url = request.path_info
            response = redirect('otp_check',user.id)
            response.set_cookie('return_url',return_url,max_age=100)
        else:
            response =  redirect('profile')
        return response
    else:
        return redirect('profile')

#   logout     ##################
def user_signout(request):
    logout(request)
    return redirect('signin')

######### forgot password ##########
def check_for_acoount(request):
    if request.method == 'POST':
        phone = request.POST.get('phone', '')
        print(phone)
        user_id = 1
    return JsonResponse({'user_id': user_id})
def forgot_Password(request):
    return render(request,'forgot_pass.html')

# ############Add Address ######################
@never_cache
@login_required(login_url='signin')   
def addaddress(request,id):
    if request.method == 'POST':
        address = Address(
            user = request.user,
            house_number = request.POST['House'],
            building_number = request.POST['Bulding'],
            street_name = request.POST['Street'],
            city = request.POST['City'],
            pin_number = request.POST['PIN'],
            phone_number = request.POST['Mobile'],
        )
        address.save()
        
        if request.POST['from'] == '0':
            return redirect('profile')
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return render(request,'address.html')

@login_required(login_url='signin')   
def deleteAddress(request,id):
    address = Address.objects.get(id = id)
    orders = Order.objects.filter(user = request.user,delivery_address = address,order_processed = False).exists()
    if not orders:
        address.delete()
    else:
        address.disabled = True
        address.save()
    return redirect('profile')

@never_cache
@login_required(login_url='signin')  
def updateAddress(request,id):
    if request.method == "POST":
        address = Address.objects.get(id=id)
        if request.POST['House'] != address.house_number and bool(request.POST['House'].strip()):
            address.house_number = request.POST['House']
        if request.POST['Bulding'] != address.house_number and bool(request.POST['Bulding'].strip()):
            address.building_number =  request.POST['Bulding']
        if request.POST['Street'] != address.street_name and bool(request.POST['Street'].strip()):
            address.street_name = request.POST['Street']
        if request.POST['City'] != address.city and bool(request.POST['City'].strip()):
            address.city = request.POST['City']
        if request.POST['PIN'] != address.pin_number and bool(request.POST['PIN'].strip()):
            address.pin_number = request.POST['PIN']
        address.save()
        return redirect('profile')
    else:
        context = {
            'address':Address.objects.get(id = id),
        }
        return render(request,'addressUpdate.html',context)


######## Messages ###############################

@login_required(login_url='signin')
def message_read(request):
    if request.method == "POST":
        message = Message.objects.filter(user = request.user, is_read = False, is_deleted = False)
        for item in message:
            item.is_read = True
            item.save()
        notification = Notification.objects.filter(is_read = False)
        for item in notification:
            item.is_read = True
            item.save()
        return JsonResponse({"status": "success"})

@never_cache
@login_required(login_url='signin')
def user_messages(request,id = None,item = None):
    if id is not None:
        if item == 'msg':
            messages = Message.objects.filter(id = id)
            context = {
                'messages' : messages,
            }
        if item == 'ntf':
            messages = Notification.objects.filter(id = id).order_by('-created_at')
            context = {
                'notifications' : messages,
            }
        return render(request,'messages.html',context)
    else:
        messages = Message.objects.filter(user = request.user).order_by('-created_at')
        ntf = Notification.objects.filter(is_deleted = False).order_by('-created_at')
        context = {
            'messages' : messages,
            'notifications': ntf,
        }
        return render(request,'messages.html',context)



