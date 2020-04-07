from django.conf import settings
from django.http import JsonResponse, HttpResponse
from django.shortcuts import render, redirect
# from django.views.generic import CreateView

from accounts.forms import LoginForm, GuestForm
from accounts.models import GuestEmail
from addresses.models import Address
from addresses.forms import AddressCheckoutForm

from billing.models import BillingProfile
from orders.models import Order
from products.models import Product
from .models import Cart

import stripe

STRIPE_SECRET_KEY = getattr(settings, "STRIPE_SECRET_KEY", None)
STRIPE_PUB_KEY = getattr(settings, "STRIPE_PUB_KEY", None)

stripe.api_key = STRIPE_SECRET_KEY


def cart_detail_api_view(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    products = [{
            "id": x.id,
            "url": x.get_absolute_url(),
            "title": x.title,
            "price": x.price
            } for x in cart_obj.products.all()] # turn list [<object>, <object>] into dict, serialize
    cart_data = {"products": products, "subtotal": cart_obj.subtotal, "total": cart_obj.total}
    return JsonResponse(cart_data)

def cart_home(request):
    cart_obj, new_obj = Cart.objects.new_or_get(request)
    # the signal receivers in models.py is handling below so following is not necessary any more
    # products = cart_obj.products.all()
    # total = 0
    # for p in products:
    #   total += p.price
    # cart_obj.total = total
    # cart_obj.save()
    return render(request, "carts/home.html", {"cart": cart_obj})

def cart_update(request):
    # print(request.POST)
    product_id = request.POST.get('product_id')
    if product_id is not None:
        try:
            product_obj = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            print('Product is gone???')
            return redirect('cart:home')
        cart_obj, new_obj = Cart.objects.new_or_get(request)
        if product_obj in cart_obj.products.all():
            cart_obj.products.remove(product_obj)
            product_added = False
        else:
            cart_obj.products.add(product_obj)
            product_added = True
        request.session['cart_items'] = cart_obj.products.count()
    # return redirect(product_obj.get_absolute_url())
    if request.is_ajax():
        json_data = {
            "added": product_added,
            "removed": not product_added,
            "cartItemCount": cart_obj.products.count()
        }
        return JsonResponse(json_data, status=200)

    return redirect('cart:home')


def checkout_home(request):
    cart_obj, cart_created = Cart.objects.new_or_get(request)
    order_obj = None
    if cart_created or cart_obj.products.count() == 0:
        return redirect("cart:home")

    # user = request.user
    # billing_profile = None
    login_form = LoginForm(request=request)
    guest_form = GuestForm(request=request)
    address_form = AddressCheckoutForm()
    billing_address_id = request.session.get("billing_address_id", None)
    shipping_address_id = request.session.get("shipping_address_id", None)

    billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
    address_qs = None
    has_card = False
    if billing_profile is not None:
        if request.user.is_authenticated:
            address_qs = Address.objects.filter(billing_profile=billing_profile)
        # shipping_address_qs = address_qs.filter(address_type='shipping')
        # billing_address_qs = address_qs.filter(address_type='billing')
        
        order_obj, order_obj_created = Order.objects.new_or_get(billing_profile, cart_obj)
        if shipping_address_id:
            order_obj.shipping_address = Address.objects.get(id=shipping_address_id)
            del request.session["shipping_address_id"]
        if billing_address_id:
            order_obj.billing_address = Address.objects.get(id=billing_address_id)
            del request.session["billing_address_id"]
        if shipping_address_id or billing_address_id:
            order_obj.save()
        has_card = billing_profile.has_card
        
    if request.method == "POST":
        # check if order is canceled
        if request.POST.get('cancel'):
            return redirect("cart:home")

        # check if order is prepared
        is_prepared = order_obj.check_done()
        if is_prepared:
            did_charge, crg_msg = billing_profile.charge(order_obj)
            if did_charge:
                order_obj.mark_paid()
                request.session['cart_items'] = 0
                del request.session['cart_id']
                if not billing_profile.user:
                    billing_profile.set_cards_inactive()
                return redirect("cart:success")
            else:
                print(crg_msg)
                return redirect("cart:checkout")

    context = {
        "object": order_obj,
        "billing_profile": billing_profile,
        "login_form": login_form,
        "guest_form": guest_form,
        "address_form": address_form,
        "address_qs": address_qs,
        "has_card": has_card,
        "publish_key": STRIPE_PUB_KEY,
        # "billing_address_form": billing_address_form,
    }

    return render(request, "carts/checkout.html", context)


def checkout_done_view(request):
    try:
        user = request.user
        # print(request.cart_id)
        # cart_obj, cart_created = Cart.objects.new_or_get(request)
        # billing_profile, billing_profile_created = BillingProfile.objects.new_or_get(request)
        # order_obj, order_obj_created = Order.objects.new_or_get(billing_profile, cart_obj)
        # print("checkout_done_view")
        # print("cart_obj", cart_obj)
        # print("order_obj", order_obj)
        context = {
            "user": user,
        }
        return render(request, "carts/checkout-done.html", context)
    except:
        print('Error in checkout_done_view')

