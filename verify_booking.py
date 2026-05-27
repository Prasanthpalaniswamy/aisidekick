import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import Client
from django.contrib.auth.models import User
from services.models import Service, Booking, ServiceCategory

def verify_booking_flow():
    # Setup
    client = Client()
    username = 'testuser'
    password = 'Start123!'
    
    # Ensure user exists
    if not User.objects.filter(username=username).exists():
        User.objects.create_user(username=username, password=password)
        print(f"Created user {username}")
    
    # Ensure service exists
    category, _ = ServiceCategory.objects.get_or_create(name='Test Category')
    service, _ = Service.objects.get_or_create(
        name='Test Service', 
        category=category,
        defaults={'price': 100, 'duration_minutes': 60, 'description': 'Test'}
    )
    print(f"Using Service ID: {service.id}")

    # 1. Login
    login_resp = client.login(username=username, password=password)
    if not login_resp:
        print("FAIL: Login failed")
        return
    print("PASS: Login successful")

    # 2. Book Service
    url = f'/book/{service.id}/'
    data = {
        'booking_date': '2026-03-10',
        'booking_time': '10:00',
        'address': '123 Test St'
    }
    response = client.post(url, data, follow=True)
    
    # 3. Verify Redirect to Payment
    if response.redirect_chain:
        print(f"Redirected to: {response.redirect_chain[-1][0]}")
        if 'payment' in response.redirect_chain[-1][0]:
            print("PASS: Redirected to Payment Page")
        else:
            print("FAIL: Redirected to wrong page (Expected Payment)")
    else:
        print(f"FAIL: No redirect after booking. Status: {response.status_code}")
        return

    # Get the booking ID from the current context or URL
    # Instead of parsing URL, let's fetch the latest booking for this user
    booking = Booking.objects.filter(user__username=username, service=service).last()
    if not booking:
        print("FAIL: Booking not created")
        return
    
    if booking.status != 'PENDING_PAYMENT':
        print(f"FAIL: Booking status is {booking.status}, expected PENDING_PAYMENT")
        return
    print(f"PASS: Booking created with status {booking.status}")

    # 4. Process Payment
    payment_url = f'/process-payment/{booking.id}/'
    print(f"Submitting payment to {payment_url}")
    # Simulate form submission (CSRF is handled by Client automatically)
    payment_response = client.post(payment_url, {}, follow=True)

    # 5. Verify Redirect to My Bookings and Status Update
    if payment_response.redirect_chain:
        print(f"Redirected to: {payment_response.redirect_chain[-1][0]}")
        if 'my-bookings' in payment_response.redirect_chain[-1][0]:
            print("PASS: Redirected to My Bookings after payment")
        else:
            print("FAIL: Redirected to wrong page (Expected My Bookings)")
    else:
        print(f"FAIL: No redirect after payment. Status: {payment_response.status_code}")

    # Refresh booking
    booking.refresh_from_db()
    if booking.status == 'CONFIRMED':
         print(f"PASS: Booking status updated to CONFIRMED")
    else:
         print(f"FAIL: Booking status is {booking.status}")

if __name__ == '__main__':
    verify_booking_flow()
