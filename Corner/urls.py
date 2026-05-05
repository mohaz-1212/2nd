from django.urls import path
from .views import *

urlpatterns = [
    # Products
    path('',Product_ListView.as_view() ,name='home' ),
     path('product/create/', ProductCreateView.as_view(), name='product-create'),
    path('product/<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('product/<int:pk>/update/', ProductUpdateView.as_view(), name='product-update'),
    path('product/<int:pk>/delete/', Product_DeleteView.as_view(), name='product-delete'),
    path('category/create/', CategoryCreateView.as_view(), name='category-create'),
    
    # Address
    path('address/', AddressListView.as_view(), name='address-list'),
    path('address/create/', AddressCreateView.as_view(), name='address-create'),
    
    # Cart
     path('cart/', CartDetailView.as_view(), name='cart'),
    path('cart/add/<int:pk>/', AddToCart.as_view(), name='add-to-cart'),
    path('cart/remove/<int:pk>/', RemoveFromCart.as_view(), name='remove-from-cart'),

    # Orders
    
    path('orders/', OrderListView.as_view(), name='order-list'),
    path('orders/<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    
    # Check Out
    
    path('checkout/', CheckoutView.as_view(), name='checkout'),
    path('payment/<int:order_pk>/', PaymentView.as_view(), name='payment'),
    
    # Login$Register
    path('login/', UserLogin.as_view(), name='login'),
    path('logout/', UserLogout.as_view(), name='logout'),
    path('register/', Register.as_view(), name='register'),
    path('register/admin/', RegisterAdmin.as_view(), name='register-admin'),

    
    
    ]

