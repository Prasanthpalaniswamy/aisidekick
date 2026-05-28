from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
import razorpay
import logging
from .models import ServiceCategory, Service, Booking, Helper, TrainingSlot, Review, Cart
from .forms import BookingForm, HelperEnrollmentForm, ReviewForm
import json
import hmac
import hashlib
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from decimal import Decimal


from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest


logger = logging.getLogger(__name__)

# Initialize Razorpay Client (using a function to ensure fresh settings)
def get_razorpay_client():
    key_id = settings.RAZORPAY_KEY_ID
    key_secret = settings.RAZORPAY_KEY_SECRET
    print(f"--- Razorpay Client Init: ID={key_id[:8]}... Secret={key_secret[:4]}... ---")
    return razorpay.Client(auth=(key_id, key_secret))


from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login

def get_or_create_active_cart(user):
    cart, created = Cart.objects.get_or_create(user=user, is_paid=False)
    return cart

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, f"Welcome, {user.username}! Your account has been created.")
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})

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
def payment(request, cart_id):
    print(f"--- DEBUG: payment view called for cart_id: {cart_id} ---")
    cart = get_object_or_404(Cart, id=cart_id, user=request.user, is_paid=False)
    bookings = cart.bookings.all()
    
    if not bookings:
        messages.error(request, "Your cart is empty.")
        return redirect('home')

    # Create Razorpay Order for the total cart amount
    total_amount = cart.total_price()
    amount = int(total_amount * 100)  # Amount in paise (INR)
    client = get_razorpay_client()
    import time

    try:
        order_options = {
            'amount': amount,
            'currency': 'INR',
            'receipt': f'cart_{cart.id}',
            'notes': {
                'description': f'Payment for {bookings.count()} services',
                'cart_id': str(cart.id)
            },
            'payment_capture': 1  # Auto-capture
        }

        print(f"Creating Order with Data: {order_options}")
        razorpay_order = client.order.create(data=order_options)
        print(f"Order Created: {razorpay_order['id']}")
        logger.info(f"Created Razorpay Order: {razorpay_order['id']} for Cart: {cart.id}")

        # Build absolute callback URL
        callback_url = request.build_absolute_uri(f'/process-payment-cart/{cart.id}/')

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
        messages.error(request, f'Payment initialization failed: {str(e)}')
        return redirect('view_cart')

@csrf_exempt
def process_payment_cart(request, cart_id):
    print(f"--- DEBUG: process_payment_cart called for cart_id: {cart_id} ---")

    cart = get_object_or_404(Cart, id=cart_id)

    if request.method == 'POST':
        razorpay_payment_id = request.POST.get('razorpay_payment_id', '')
        razorpay_order_id   = request.POST.get('razorpay_order_id', '')
        razorpay_signature  = request.POST.get('razorpay_signature', '')

        params_dict = {
            'razorpay_order_id':   razorpay_order_id,
            'razorpay_payment_id': razorpay_payment_id,
            'razorpay_signature':  razorpay_signature,
        }

        client = get_razorpay_client()
        try:
            client.utility.verify_payment_signature(params_dict)

            # Update Cart to PAID
            cart.is_paid = True
            cart.razorpay_order_id   = razorpay_order_id
            cart.razorpay_payment_id = razorpay_payment_id
            cart.razorpay_signature  = razorpay_signature
            cart.save()

            # Update all Bookings in the Cart to PAID
            for booking in cart.bookings.all():
                booking.status = 'PAID'
                booking.save()

            print("[SUCCESS] Signature Verified! Cart PAID.")
            return render(request, 'services/paymentsuccess.html', {
                'payment_id': razorpay_payment_id,
                'cart': cart,
                'bookings': cart.bookings.all(),
            })

        except razorpay.errors.SignatureVerificationError:
            print("[ERROR] Signature Verification Failed!")
            logger.error(f"Signature mismatch for cart {cart_id}")
            return render(request, 'services/paymentfail.html')

        except Exception as e:
            logger.error(f"Razorpay Verification Error: {str(e)}")
            return HttpResponseBadRequest(str(e))

    return redirect('payment', cart_id=cart.id)

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

@login_required
def helper_enroll(request):
    # Check if user is already a helper
    if hasattr(request.user, 'helper_profile'):
        messages.info(request, "You are already registered as a helper.")
        return redirect('home')

    if request.method == 'POST':
        form = HelperEnrollmentForm(request.POST, request.FILES)
        if form.is_valid():
            helper = form.save(commit=False)
            helper.user = request.user
            helper.status = 'APPLIED'
            helper.save()
            messages.success(request, "Your application to join as a helper has been submitted! We will review it shortly.")
            return redirect('home')
    else:
        form = HelperEnrollmentForm()
    
    return render(request, 'services/helper_enroll.html', {'form': form})

@login_required
def helper_dashboard(request):
    helper = get_object_or_404(Helper, user=request.user)
    upcoming_training = helper.training_slots.filter(is_completed=False).order_by('date', 'start_time')
    completed_training = helper.training_slots.filter(is_completed=True).order_by('-date')
    
    # Assigned Jobs (Requirement 15)
    assigned_jobs = helper.assigned_jobs.exclude(status__in=['COMPLETED', 'CANCELLED']).order_by('booking_date', 'booking_time')
    completed_jobs = helper.assigned_jobs.filter(status='COMPLETED').order_by('-booking_date')

    # Prepare formatted strings to bypass template format issues
    for job in assigned_jobs:
        job.display_date = job.booking_date.strftime("%b. %d, %Y")
        job.display_address = job.address

    context = {
        'helper': helper,
        'upcoming_training': upcoming_training,
        'completed_training': completed_training,
        'assigned_jobs': assigned_jobs,
        'completed_jobs': completed_jobs,
    }

    return render(request, 'services/helper_dashboard.html', context)


@login_required
def training_slots_view(request):
    helper = get_object_or_404(Helper, user=request.user)
    # Slots that are not completed and haven't reached max participants
    available_slots = []
    all_open_slots = TrainingSlot.objects.filter(is_completed=False).order_by('date')
    
    for slot in all_open_slots:
        if slot.participants.count() < slot.max_participants and helper not in slot.participants.all():
            available_slots.append(slot)
            
    my_slots = helper.training_slots.all().order_by('date')
    
    return render(request, 'services/training_slots.html', {
        'available_slots': available_slots,
        'my_slots': my_slots
    })

@login_required
def book_training_slot(request, slot_id):
    helper = get_object_or_404(Helper, user=request.user)
    slot = get_object_or_404(TrainingSlot, id=slot_id, is_completed=False)
    
    if slot.participants.count() < slot.max_participants:
        if helper not in slot.participants.all():
            slot.participants.add(helper)
            messages.success(request, f"You have successfully booked the training: {slot.title}")
        else:
            messages.info(request, "You are already enrolled in this training.")
    else:
        messages.error(request, "This training slot is already full.")
        
    return redirect('helper_dashboard')

@login_required
def complete_training_slot(request, slot_id):
    # Only Admin (or a specific lead helper) should probably do this, 
    # but for now, we'll keep it as any participant for simplicity in this proto.
    helper = get_object_or_404(Helper, user=request.user)
    slot = get_object_or_404(TrainingSlot, id=slot_id, participants=helper)
    
    if not slot.is_completed:
        participants = slot.participants.all()
        slot.is_completed = True
        slot.save()
        
        # Update hours for ALL participants
        for p in participants:
            # p.total_training_hours += slot.duration_hours
            p.total_training_hours += Decimal(str(slot.duration_hours))
            if p.total_training_hours >= 5:
                p.is_certified = True
                p.status = 'CERTIFIED'
            p.save()
        
        messages.success(request, f"Training '{slot.title}' marked as completed. Hours awarded to all participants.")
    
    return redirect('helper_dashboard')
@login_required
def update_job_status(request, booking_id):
    helper = get_object_or_404(Helper, user=request.user)
    booking = get_object_or_404(Booking, id=booking_id, assigned_helper=helper)
    
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['IN_PROGRESS', 'COMPLETED']:
            booking.status = new_status
            booking.save()
            messages.success(request, f"Job status updated to: {booking.get_status_display()}")
    
    return redirect('helper_dashboard')

@login_required
def get_payment_details(request, payment_id):
    """Mirror of Node's /api/payment/:paymentId"""
    try:
        client = get_razorpay_client()
        payment = client.payment.fetch(payment_id)
        return JsonResponse({
            "success": True,
            "payment": payment
        })
    except Exception as e:
        logger.error(f"Error fetching payment {payment_id}: {str(e)}")
        return JsonResponse({
            "success": False,
            "error": "Failed to fetch payment details",
            "message": str(e)
        }, status=500)



def landing(request):
    categories = ServiceCategory.objects.all()
    return render(request, 'pages/landing.html', {'categories': categories})

def pricing(request):
    return render(request, 'pages/pricing.html')

def products(request):
    return render(request, 'pages/products.html')

def features(request):
    return render(request, 'pages/features.html')

def docs(request):
    return render(request, 'pages/docs.html')

def contact(request):
    return render(request, 'pages/contact.html')

def privacy(request):
    return render(request, 'pages/privacy.html')

def terms(request):
    return render(request, 'pages/terms.html')

def health_check(request):
    """Mirror of Node's /health"""
    return JsonResponse({"status": "OK", "message": "Server is running"})





