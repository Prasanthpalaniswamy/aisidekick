# services/views/utils.py

import logging
import razorpay

from django.conf import settings
from ..models import Cart

logger = logging.getLogger(__name__)

def get_razorpay_client():
    key_id = settings.RAZORPAY_KEY_ID
    key_secret = settings.RAZORPAY_KEY_SECRET

    return razorpay.Client(auth=(key_id, key_secret))

def get_or_create_active_cart(user):
    cart, created = Cart.objects.get_or_create(
    user=user,
    is_paid=False
    )
    return cart
