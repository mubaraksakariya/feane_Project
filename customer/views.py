from django.shortcuts import render,HttpResponse,redirect
from django.contrib.auth import authenticate,login,logout
from django.contrib import messages
from twilio.rest import Client
from .models import User,Address
from store.models import Product
import random
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

OTP = 123
# Create your views here.

# to home page###################
@login_required(login_url='signin')
def index(request):
    return redirect('/store')


# to send otp###########################

def send_otp(phone_number,OTP):
    account_sid = 'ACba9264ed85bf6990cb2dbaa8bd80d92c'
    auth_token = '47b0bc61b8d096da0bebbabfa7109f87'
    client = Client(account_sid, auth_token)
    message = client.messages \
        .create(
            body= f"Your otp to signup is {OTP}" ,
            from_= '+14305410892',
            to = phone_number 
    )
# to sign up###########################
def userexist(request):
    email = request.POST.get('email','')
    user = User.objects.filter(email=email).exists()
    print(user)
    if user:
        return JsonResponse({'exist': 'true'})
    else:
        return JsonResponse({'exist': 'false'})


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
        return redirect('/signin')
    elif not request.user.is_authenticated:
        return render(request,'signup.html')
    else:
        return redirect('/')

# # signup with otp#########################

# def otp_signup(request):
#     if request.method == 'POST':
#         phone_number = request.POST['number']
#         send_otp(phone_number)
#         return render(request,'otp_check.html')
#     elif not request.user.is_authenticated:    
#         return render(request,'otp_signup.html')
#     else:
#         return redirect('/')
# to verify the otp#######################

def otp_check(request,id):
    user = User.objects.get(id = id)
    return_url = request.COOKIES.get('return_url')
    if request.method == 'POST':
        val = request.POST['OTP']      
        if val == str(user.otp):
            user.phone_number_verified = True
            user.save()
            login(request,user)
            return redirect(return_url)
        else:
            messages.info(request,'OTP is not correct, try again')
            return render(request,'otp_check.html')
    elif not user.phone_number_verified:
        OTP = random.randrange(111111, 999999)
        user.otp = OTP
        user.save()
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
        elif user is not None:
            login(request,user)
            return redirect('/')
        else:
            messages.info(request,f'Invalid credential')
            return redirect('/signin')
    elif not request.user.is_authenticated:    
        return render(request,'signin.html')
    else:
        return redirect('/')    
    
@login_required(login_url='signin')
def user_profile(request):
    context = {
        'user' : request.user,
        'address': Address.objects.filter(user = request.user)
    }
    return render(request,'profile.html',context=context)

@login_required(login_url='signin')   
def profile_update(request,id):
    user = User.objects.get(id = id)
    old_number = user.phone_number
    if request.method == 'POST':
        name = request.POST['name']
        number = request.POST['number']
        email = request.POST['email']
        if name != user.first_name and bool(name.strip()):
            user.first_name = name
        if email != user.email and bool(email.strip()) and not User.objects.filter(email=email).exists():
            user.email = email
        else:
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


# ############Add Address ######################

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
        return redirect(request.META.get('HTTP_REFERER'))
    else:
        return render(request,'address.html')
def deleteAddress(request,id):
    Address.objects.get(id = id).delete()
    return redirect('profile')
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
