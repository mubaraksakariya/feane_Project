from django.urls import path
from . import views
urlpatterns = [
    path('',views.index,name='user_home'),
    path('signin/',views.user_signin,name='signin'),
    path('signup/',views.user_signup,name='signup'),
    # path('otp_signup',views.otp_signup,name='otp_signup'),
    path('otp_check/<id>',views.otp_check,name='otp_check'),
    path('signout',views.user_signout,name='customer_signout'),
    path('profile',views.user_profile,name='profile'),
    path('signup/userexist',views.userexist,name='userexist'),
    path('profile_update/<id>',views.profile_update,name='profile_update'),
    path('addaddress/<id>',views.addaddress,name='addaddress'),
    path('deleteAddress/<id>',views.deleteAddress,name='deleteAddress'),
    path('updateAddress/<id>',views.updateAddress,name='updateAddress'),
    path('forgot_Password',views.forgot_Password,name='forgot_Password'),
    path('check_for_acoount',views.check_for_acoount,name='check_for_acoount'),
    
    path('user_messages',views.user_messages,name='user_messages'),
    path('user_messages/<int:id>/<str:item>',views.user_messages,name='user_messages'),
    path('message_read',views.message_read,name='message_read'),
]
