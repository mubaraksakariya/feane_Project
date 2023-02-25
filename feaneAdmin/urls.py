from django.urls import path
from . import views

urlpatterns = [
    path('',views.adminHome,name='admin_home'),
    path('signin',views.signin,name='admin_signin'),
    path('signout',views.signout,name='admin_signout'),
    path('inventory',views.inventory,name='inventory'),
    path('editproduct/<id>',views.editproduct,name='editproduct'),
    path('show_orders',views.show_orders,name='show_orders'),
    path('all_orders',views.all_orders,name='all_orders'),
    path('manage_order/<id>',views.manage_order,name='manage_order'),
    path('accept_order/<id>',views.accept_order,name='accept_order'),
    path('additem/<id>',views.additem,name='additem'),
    path('additem',views.additem,name='additem'),
    path('deleteitem/<id>',views.deleteitem,name='deleteitem'),
    path('addcategory',views.addcategory,name='addcategory'),
    path('addsize/<id>',views.addsize,name='addsize'),
    path('delete_category/<id>',views.delete_category,name='delete_category'),
    path('addsize',views.addsize,name='addsize'),
    path('deletesize/<id>',views.deletesize,name='deletesize'),
    path('users',views.users,name='users'),
    path('blocked_users',views.blocked_users,name='blocked_users'),
    path('user_update/<id>',views.user_update,name='user_update'),
    path('delete_profile/<id>',views.delete_profile,name='delete_profile'),
    path('block_user/<id>',views.block_user,name='block_user'),
    path('unblock_user/<id>',views.unblock_user,name='unblock_user'),

    path('adminside_search',views.adminside_search,name='adminside_search'),
]
