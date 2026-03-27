from django.shortcuts import render, redirect, reverse, get_object_or_404, HttpResponse
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.conf import settings

from .forms import OrderForm
from .models import Order, OrderLineItem
from products.models import Product
from profiles.forms import UserProfileForm
from profiles.models import UserProfile
from bag.contexts import bag_contents
from urllib.parse import urlencode

import stripe
import json

import uuid
import hmac
import hashlib
import base64
from django.shortcuts import redirect
from django.conf import settings


@require_POST
def cache_checkout_data(request):
    pass


def checkout(request):
    if request.method == "POST":
        bag = request.session.get("bag", {})

        form_data = {
            "full_name": request.POST["full_name"],
            "email": request.POST["email"],
            "phone_number": request.POST["phone_number"],
            "country": request.POST["country"],
            "postcode": request.POST["postcode"],
            "town_or_city": request.POST["town_or_city"],
            "street_address1": request.POST["street_address1"],
            "street_address2": request.POST["street_address2"],
            "county": request.POST["county"],
        }
        order_form = OrderForm(form_data)

        # if form is valid, get the data, pid and save the order
        if order_form.is_valid():
            order = order_form.save(commit=False)
            pid = "pid"
            order.stripe_pid = pid
            order.original_bag = json.dumps(bag)
            print(bag)
            order.save()

            # for each item in the bag, create a line item in admin
            for item_id, item_data in bag.items():
                try:
                    product = Product.objects.get(id=item_id)
                    if isinstance(item_data, int):
                        order_line_item = OrderLineItem(
                            order=order,
                            product=product,
                            quantity=item_data,
                        )
                        order_line_item.save()
                    else:
                        for size, quantity in item_data["items_by_size"].items():
                            order_line_item = OrderLineItem(
                                order=order,
                                product=product,
                                quantity=quantity,
                                product_size=size,
                            )
                            order_line_item.save()
                except Product.DoesNotExist:
                    messages.error(
                        request,
                        (
                            "One of the products in your bag wasn't found \
                            in our database. "
                            "Please call us for assistance!"
                        ),
                    )
                    order.delete()
                    return redirect(reverse("view_bag"))

            # save the order info in the user's profile
            request.session["save_info"] = "save-info" in request.POST
            return redirect(reverse("checkout_success", args=[order.order_number]))
        # checkout form error
        else:
            messages.error(
                request,
                "There was an error with your form. \
                Please double check your information.",
            )
    else:
        bag = request.session.get("bag", {})
        if not bag:
            messages.error(request, "There's nothing in your bag at the moment")
            return redirect(reverse("products"))

        current_bag = bag_contents(request)
        total = current_bag["grand_total"]

        # Attempt to prefill the form with the relevant info
        # from the user's profile
        if request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(user=request.user)
                order_form = OrderForm(
                    initial={
                        "full_name": profile.user.get_full_name(),
                        "email": profile.user.email,
                        "phone_number": profile.default_phone_number,
                        "country": profile.default_country,
                        "postcode": profile.default_postcode,
                        "town_or_city": profile.default_town_or_city,
                        "street_address1": profile.default_street_address1,
                        "street_address2": profile.default_street_address2,
                        "county": profile.default_county,
                    }
                )
            except UserProfile.DoesNotExist:
                order_form = OrderForm()
        else:
            order_form = OrderForm()

    template = "checkout/checkout.html"
    context = {
        "order_form": order_form,
        "stripe_public_key": "",
        "client_secret": "",
    }

    return render(request, template, context)


def checkout_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    total_amount = str(order.grand_total)
    transaction_uuid = str(uuid.uuid4())
    product_code = "EPAYTEST"
    success_url = request.build_absolute_uri(reverse("payment_success"))
    failure_url = request.build_absolute_uri(reverse("payment_failure"))

    # Prepare data for signature
    signed_fields = f"total_amount={total_amount},transaction_uuid={transaction_uuid},product_code={product_code}"
    secret_key = "8gBm/:&EnhH.1/q"

    hmac_sha256 = hmac.new(
        secret_key.encode("utf-8"), signed_fields.encode("utf-8"), hashlib.sha256
    )
    digest = hmac_sha256.digest()
    signature_base64 = base64.b64encode(digest).decode("utf-8")

    # Prepare payload
    payload = {
        "amount": total_amount,
        "tax_amount": "0",
        "total_amount": total_amount,
        "transaction_uuid": transaction_uuid,
        "product_code": product_code,
        "product_service_charge": "0",
        "product_delivery_charge": "0",
        "success_url": success_url,
        "failure_url": failure_url,
        "signed_field_names": "total_amount,transaction_uuid,product_code",
        "signature": signature_base64,
    }

    save_info = request.session.get("save_info")

    if request.user.is_authenticated:
        profile = UserProfile.objects.get(user=request.user)
        # Attach the user's profile to the order
        order.user_profile = profile
        order.save()

        # Save the user's info
        if save_info:
            profile_data = {
                "default_phone_number": order.phone_number,
                "default_country": order.country,
                "default_postcode": order.postcode,
                "default_town_or_city": order.town_or_city,
                "default_street_address1": order.street_address1,
                "default_street_address2": order.street_address2,
                "default_county": order.county,
            }
            user_profile_form = UserProfileForm(profile_data, instance=profile)
            if user_profile_form.is_valid():
                user_profile_form.save()

    messages.success(
        request,
        f"Order successfully processed! \
        Your order number is {order_number}. A confirmation \
        email will be sent to {order.email}.",
    )

    if "bag" in request.session:
        del request.session["bag"]

    return render(
        request,
        "checkout/payment_redirect.html",
        {"message": "Payment successful! Redirecting to home...", "redirect_url": "/"},
    )


def payment_success(request):
    return render(
        request,
        "checkout/payment_redirect.html",
        {"message": "Payment successful! Redirecting to home...", "redirect_url": "/"},
    )


def payment_failure(request):
    return render(
        request,
        "checkout/payment_redirect.html",
        {
            "message": "Payment failed or canceled. Redirecting to home...",
            "redirect_url": "/",
        },
    )
