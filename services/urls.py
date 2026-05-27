from django.urls import path
from . import views

urlpatterns = [
    path('servicebooking/', views.home, name='home'),
    path('', views.aiskhome, name='aiskhome'),
    path('signup/', views.signup, name='signup'),
    path('category/<int:category_id>/', views.service_list, name='service_list'),
    path('service/<int:service_id>/', views.service_detail, name='service_detail'),
    path('book/<int:service_id>/', views.book_service, name='book_service'),
    path('cart/', views.view_cart, name='view_cart'),
    path('cart/remove/<int:booking_id>/', views.remove_from_cart, name='remove_from_cart'),
    path('payment-cart/<int:cart_id>/', views.payment, name='payment'),
    path('process-payment-cart/<int:cart_id>/', views.process_payment_cart, name='process_payment_cart'),
    path('my-bookings/', views.my_bookings, name='my_bookings'),
    path('helper/enroll/', views.helper_enroll, name='helper_enroll'),
    path('helper/dashboard/', views.helper_dashboard, name='helper_dashboard'),
    path('helper/training/', views.training_slots_view, name='training_slots'),
    path('helper/training/book/<int:slot_id>/', views.book_training_slot, name='book_training_slot'),
    path('helper/training/complete/<int:slot_id>/', views.complete_training_slot, name='complete_training_slot'),
    path('helper/job/update/<int:booking_id>/', views.update_job_status, name='update_job_status'),
    path('submit-review/<int:booking_id>/', views.submit_review, name='submit_review'),



    
    # API Parity Paths (Matching Node script structure)
    path('api/payment/<str:payment_id>/', views.get_payment_details, name='api_get_payment'),
    path('health/', views.health_check, name='health_check'),

]
