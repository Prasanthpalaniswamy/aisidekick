# subscribe_plan()
# cancel_subscription()
# billing_portal()
# generate_api_key()
# usage_dashboard()

# services/views/subscription_views.py

import time
import logging

from django.shortcuts import (
render,
get_object_or_404,
redirect
)

from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings

from ..models import (
SubscriptionPlan,
Subscription
)

from .utils import get_razorpay_client

logger = logging.getLogger(__name__)

@login_required
def subscribe_plan(request, plan_id):


    # Get selected plan
    plan = get_object_or_404(
        SubscriptionPlan,
        id=plan_id,
        active=True
    )

    try:

        # Create Subscription record first
        subscription = Subscription.objects.create(
            user=request.user,
            plan=plan,
            status="PENDING"
        )

        # Razorpay amount in paise
        amount = int(plan.price * 100)

        client = get_razorpay_client()

        # Create Razorpay Order
        order_data = {
            "amount": amount,
            "currency": "INR",
            "receipt": f"subscription_{subscription.id}",
            "notes": {
                "subscription_id": str(subscription.id),
                "user_id": str(request.user.id),
                "plan_name": plan.name,
            },
            "payment_capture": 1
        }

        razorpay_order = client.order.create(data=order_data)

        # Save Razorpay Order ID
        subscription.razorpay_order_id = razorpay_order["id"]
        subscription.save()

        # Callback URL
        callback_url = request.build_absolute_uri(
            f"/process-subscription-payment/{subscription.id}/"
        )

        context = {
            "plan": plan,
            "subscription": subscription,
            "razorpay_order_id": razorpay_order["id"],
            "razorpay_key_id": settings.RAZORPAY_KEY_ID,
            "amount": amount,
            "amount_display": plan.price,
            "callback_url": callback_url,
            "debug_version": int(time.time()),
        }

        return render(
            request,
            "subscriptions/checkout.html",
            context
        )

    except Exception as e:

        logger.error(
            f"Subscription creation failed: {str(e)}"
        )

        messages.error(
            request,
            "Unable to initialize subscription payment."
        )

        return redirect("pricing")

