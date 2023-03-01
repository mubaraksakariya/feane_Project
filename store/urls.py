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
    path('cartItems',views.cartItems,name='cartItems'),
    path('cart_count_change',views.cart_count_change,name='cart_count_change'),

    path('cart_in_order/<id>',views.user_order,name='cart_in_order'),
    path('user_order',views.user_order,name='user_order'),

    path('user_order_history',views.user_order_history,name='user_order_history'),
    path('user_order_history_cart/<id>',views.user_order_history,name='user_order_history_cart'),
    
    path('payment_callback/<id>', views.payment_callback, name='payment_callback'),
]