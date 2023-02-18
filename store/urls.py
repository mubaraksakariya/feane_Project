from django.urls import path
from . import views


urlpatterns = [
    path('',views.store,name='store'),
    path('product/<id>',views.product,name='product'),
    path('cart',views.cart, name='cart'),
    path('addToCart',views.addToCart, name ="addToCart"),
    path('removefromcart/<id>',views.removefromcart, name ="removefromcart"),
    path('checkout',views.checkout,name='checkout'),
    path('placeOrder',views.placeOrder,name='placeOrder'),
    path('user_order',views.user_order,name='user_order'),
]