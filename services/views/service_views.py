from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
import razorpay
import logging
from ..models import ServiceCategory, Service, Booking
# , Helper, TrainingSlot, Review, 
from ..models import Cart
from ..forms import BookingForm, HelperEnrollmentForm, ReviewForm
import json
import hmac
import hashlib
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal


from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest


logger = logging.getLogger(__name__)




from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

def home(request):
    categories = ServiceCategory.objects.all()
    return render(request, 'services/home.html', {'categories': categories})



def service_list(request, category_id):
    category = get_object_or_404(ServiceCategory, id=category_id)
    services = category.services.all()
    return render(request, 'services/service_list.html', {'category': category, 'services': services})

def service_detail(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    return render(request, 'services/service_detail.html', {'service': service})

@login_required
def book_service(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.service = service
            booking.user = request.user
            
            # Associate with active cart
            cart = get_or_create_active_cart(request.user)
            booking.cart = cart
            booking.save()
            
            messages.success(request, f"{service.name} added to your cart!")
            return redirect('view_cart')
    else:
        form = BookingForm()
    
    return render(request, 'services/booking_form.html', {'service': service, 'form': form})

def get_or_create_active_cart(user):
    cart, created = Cart.objects.get_or_create(user=user, is_paid=False)
    return cart

@login_required
def view_cart(request):
    cart = get_or_create_active_cart(request.user)
    bookings = cart.bookings.all()
    total = cart.total_price()
    return render(request, 'services/cart.html', {'cart': cart, 'bookings': bookings, 'total': total})

@login_required
def remove_from_cart(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user, cart__is_paid=False)
    service_name = booking.service.name
    booking.delete()
    messages.success(request, f"{service_name} removed from your cart.")
    return redirect('view_cart')


@login_required
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'services/my_bookings.html', {'bookings': bookings})

@login_required
def submit_review(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user, status='COMPLETED')
    
    # Check if review already exists
    if hasattr(booking, 'review'):
        messages.info(request, "You have already reviewed this service.")
        return redirect('my_bookings')
        
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.helper = booking.assigned_helper
            review.customer = request.user
            review.save()
            messages.success(request, "Thank you for your feedback!")
            return redirect('my_bookings')
    else:
        form = ReviewForm()
    
    return render(request, 'services/submit_review.html', {'form': form, 'booking': booking})







