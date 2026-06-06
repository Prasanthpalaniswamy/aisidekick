# services/views/payment_views.py

import logging
import time

from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse, HttpResponseBadRequest

import razorpay

from ..models import Cart,Subscription
from .utils import get_razorpay_client

logger = logging.getLogger(__name__)

@login_required
def payment(request, cart_id):
    cart = get_object_or_404(
        Cart,
        id=cart_id,
        user=request.user,
        is_paid=False
    )

    bookings = cart.bookings.all()

    if not bookings:
        messages.error(request, "Your cart is empty.")
        return redirect('home')

    total_amount = cart.total_price()
    amount = int(total_amount * 100)

    client = get_razorpay_client()

    try:

        order_options = {
            'amount': amount,
            'currency': 'INR',
            'receipt': f'cart_{cart.id}',
            'notes': {
                'description': f'Payment for {bookings.count()} services',
                'cart_id': str(cart.id)
            },
            'payment_capture': 1
        }

        razorpay_order = client.order.create(data=order_options)

        callback_url = request.build_absolute_uri(
            f'/process-payment-cart/{cart.id}/'
        )

        context = {
            'cart': cart,
            'bookings': bookings,
            'razorpay_order_id': razorpay_order['id'],
            'razorpay_key_id': settings.RAZORPAY_KEY_ID,
            'amount': amount,
            'amount_display': total_amount,
            'callback_url': callback_url,
            'debug_version': int(time.time()),
        }

        return render(request, 'services/payment.html', context)

    except Exception as e:

        logger.error(f"Razorpay Order Creation Failed: {str(e)}")

        messages.error(
            request,
            f'Payment initialization failed: {str(e)}'
        )

        return redirect('view_cart')
    

@csrf_exempt
# @login_required
def process_subscription_payment(request, subscription_id):
    

    if request.method == 'POST':

        razorpay_payment_id = request.POST.get(
            'razorpay_payment_id',
            ''
        )

        razorpay_order_id = request.POST.get(
            'razorpay_order_id',
            ''
        )

        subscription = get_object_or_404(
        Subscription,
        id=subscription_id,
        razorpay_order_id=razorpay_order_id
        # ,user=request.user
    )


        razorpay_signature = request.POST.get(
            'razorpay_signature',
            ''
        )

        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature,
        }

        client = get_razorpay_client()

        try:

            client.utility.verify_payment_signature(
                params_dict
            )

            subscription.status = 'ACTIVE'

            subscription.razorpay_order_id = razorpay_order_id
            subscription.razorpay_payment_id = razorpay_payment_id
            subscription.razorpay_signature = razorpay_signature

            subscription.save()
            from services.models import APIKey
            APIKey.objects.get_or_create(
                user=subscription.user
            )
            return render(
                request,
                'pages/paymentsuccess.html',
                {
                    'payment_id': razorpay_payment_id,
                    'subscription': subscription,
                }
            )

        except razorpay.errors.SignatureVerificationError:

            logger.error(
                f"Signature mismatch for subscription {subscription_id}"
            )

            return render(
                request,
                'pages/paymentfail.html'
            )

        except Exception as e:

            logger.error(
                f"Razorpay Verification Error: {str(e)}"
            )

            return HttpResponseBadRequest(str(e))

    return redirect('pricing')


@csrf_exempt
def process_payment_cart(request, cart_id):
    cart = get_object_or_404(Cart, id=cart_id)

    if request.method == 'POST':

        razorpay_payment_id = request.POST.get(
            'razorpay_payment_id', ''
        )

        razorpay_order_id = request.POST.get(
            'razorpay_order_id', ''
        )

        razorpay_signature = request.POST.get(
            'razorpay_signature', ''
        )

        params_dict = {
            'razorpay_order_id': razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature': razorpay_signature,
        }

        client = get_razorpay_client()

        try:

            client.utility.verify_payment_signature(params_dict)

            cart.is_paid = True
            cart.razorpay_order_id = razorpay_order_id
            cart.razorpay_payment_id = razorpay_payment_id
            cart.razorpay_signature = razorpay_signature

            cart.save()

            for booking in cart.bookings.all():
                booking.status = 'PAID'
                booking.save()

            return render(
                request,
                'services/paymentsuccess.html',
                {
                    'payment_id': razorpay_payment_id,
                    'cart': cart,
                    'bookings': cart.bookings.all(),
                }
            )

        except razorpay.errors.SignatureVerificationError:

            logger.error(
                f"Signature mismatch for cart {cart_id}"
            )

            return render(
                request,
                'services/paymentfail.html'
            )

        except Exception as e:

            logger.error(
                f"Razorpay Verification Error: {str(e)}"
            )

            return HttpResponseBadRequest(str(e))


@login_required
def get_payment_details(request, payment_id):
    try:

        client = get_razorpay_client()

        payment = client.payment.fetch(payment_id)

        return JsonResponse({
            "success": True,
            "payment": payment
        })

    except Exception as e:

        logger.error(
            f"Error fetching payment {payment_id}: {str(e)}"
        )

        return JsonResponse({
            "success": False,
            "error": "Failed to fetch payment details",
            "message": str(e)
        }, status=500)

from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect
from services.models import APIKey


@login_required
def regenerate_api_key(request):

    if request.method == "POST":

        token = APIKey.objects.get(
            user=request.user
        )

        token.key = APIKey.generate_key()

        token.save()

    return redirect('dashboard')