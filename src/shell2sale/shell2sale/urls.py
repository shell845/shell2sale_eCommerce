"""shell2sale URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""

from django.conf import settings
from django.conf.urls.static import static

#from django.conf.urls import url
from django.contrib import admin
from django.contrib.auth.views import LogoutView
from django.contrib.staticfiles.views import serve
from django.views.generic import TemplateView, RedirectView
from django.urls import path, include

from accounts.views import LoginView, RegisterView, GuestRegisterView
from addresses.views import (
    AddressCreateView,
    AddressListView,
    AddressUpdateView,
    checkout_address_create_view, 
    checkout_address_reuse_view
    )
from billing.views import payment_method_view, payment_method_createview
from carts.views import cart_detail_api_view
from .views import home_page, about_page, contact_page

# from products.views import (
#     ProductListView,
#     product_list_view,
#     ProductDetailView,
#     ProductDetailSlugView,
#     product_detail_view,
#     ProductFeaturedListView,
#     ProductFeaturedDetailView
#     )

# from carts.views import cart_home


urlpatterns = [
    path('', home_page, name='home'),
    path('about/', about_page, name='about'),
    path('accounts/', RedirectView.as_view(url='/account')),
    path('account/', include(('accounts.urls','accounts'), namespace='account')),
    path('accounts/', include('accounts.passwords.urls')), # Django default path /accounts/password/
    path('address/', RedirectView.as_view(url='/addresses')),
    path('addresses/', AddressListView.as_view(), name='addresses'),
    path('addresses/create/', AddressCreateView.as_view(), name='address-create'),
    path('addresses/<pk>/', AddressUpdateView.as_view(), name='address-update'),
    path('admin/', admin.site.urls, name='admin'),
    path('api/cart/', cart_detail_api_view, name='api-cart'),
    path('billing/payment-method/', payment_method_view, name='billing-payment-method'),
    path('billing/payment-method/create/', payment_method_createview, name='billing-payment-method-endpoint'),
    path('cart/', include(('carts.urls', 'carts'), namespace='cart')),
    path('checkout/address/create/', checkout_address_create_view, name='checkout_address_create'),
    path('checkout/address/reuse/', checkout_address_reuse_view, name='checkout_address_reuse'),
    path('contact/', contact_page, name='contact'),
    path('favicon.ico', serve, {'path': 'img/favicon.ico'}),
    path('login/', LoginView.as_view(), name='login'), 
    path('logout/', LogoutView.as_view(), name='logout'),
    path('orders/', include('orders.urls', namespace='orders')),
    path('products/', include(('products.urls', 'products'), namespace='products')),
    path('register/guest/', GuestRegisterView.as_view(), name='guest_register'),
    path('register/', RegisterView.as_view(), name='register'),
    path('search/', include(('search.urls', 'search'), namespace='search')),
    path('settings/', RedirectView.as_view(url='/account')),
    # path('accounts/login/', RedirectView.as_view(url='/login')), # not a good way to do, redirect in settings instead: local.py, production.py, base.py
    # path('cart/', cart_home, name='cart'),
    # path('featured/', ProductFeaturedListView.as_view()),
    # path('featured/<pk>/', ProductFeaturedDetailView.as_view()),
    # path('products/', ProductListView.as_view()),
    # path('products-fbv/', product_list_view), # function based
    # path('products/<pk>/', ProductDetailView.as_view()),
    # path('products/<slug:slug>/', ProductDetailSlugView.as_view()),
    # path('products-fbv/<pk>/', product_detail_view), # function based
    # url(r'^$', home_page),   
    # path('products/(?P<pk>\d+)/$', ProductDetailView.as_view()),
    # path('products-fbv/(?P<pk>\d+)/$', product_detail_view),   
]

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)