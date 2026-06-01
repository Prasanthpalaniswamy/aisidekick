from django.urls import path
# from . import views
from .views.page_views import landing, pricing, products, features, docs, contact, privacy, terms, subscribe, apikey, health_check, dashboard
from .views.service_views import home,my_bookings,submit_review,service_list, service_detail, book_service, view_cart, remove_from_cart
from .views.helper_views import get_payment_details,signup, payment, process_payment_cart, helper_enroll, helper_dashboard, training_slots_view, book_training_slot, complete_training_slot, update_job_status
from .views.payment_views import process_subscription_payment
from .views.subscription_views import subscribe_plan
# from .views.api_views import get_payment_details
    

urlpatterns = [
    path('', landing, name='landing'),
    path('pricing/', pricing, name='pricing'),
    path('products/', products, name='products'),
    path('features/', features, name='features'),
    path('docs/', docs, name='docs'),
    path('contact/', contact, name='contact'),
    path('privacy/', privacy, name='privacy'),
    path('terms/', terms, name='terms'),
    path('subscribe/', subscribe, name='subscribe'),
    path('apikey/', apikey, name='apikey'),
    path('servicebooking/', home, name='home'),
    path('signup/', signup, name='signup'),
    path('category/<int:category_id>/', service_list, name='service_list'),
    path('service/<int:service_id>/', service_detail, name='service_detail'),
    path('book/<int:service_id>/', book_service, name='book_service'),
    path('cart/', view_cart, name='view_cart'),
    path('cart/remove/<int:booking_id>/', remove_from_cart, name='remove_from_cart'),
    path('payment-cart/<int:cart_id>/', payment, name='payment'),
    path('process-payment-cart/<int:cart_id>/', process_payment_cart, name='process_payment_cart'),
    path(
    'process-subscription-payment/<int:subscription_id>/',
    process_subscription_payment,
    name='process_subscription_payment'
),
path(
    'subscribe/<int:plan_id>/',
    subscribe_plan,
    name='subscribe_plan'
),
path(
    "checkout/<int:plan_id>/",
    subscribe_plan,
    name="subscribe_plan"
),

path(
    'dashboard/',
    dashboard,
    name='dashboard'
),
    path('my-bookings/', my_bookings, name='my_bookings'),
    
    
    path('helper/enroll/', helper_enroll, name='helper_enroll'),
    path('helper/dashboard/', helper_dashboard, name='helper_dashboard'),
    path('helper/training/', training_slots_view, name='training_slots'),
    path('helper/training/book/<int:slot_id>/', book_training_slot, name='book_training_slot'),
    path('helper/training/complete/<int:slot_id>/', complete_training_slot, name='complete_training_slot'),
    path('helper/job/update/<int:booking_id>/', update_job_status, name='update_job_status'),
    path('submit-review/<int:booking_id>/', submit_review, name='submit_review'),
    

    # API Parity Paths (Matching Node script structure)
    path('api/payment/<str:payment_id>/', get_payment_details, name='api_get_payment'),
    path('health/', health_check, name='health_check'),


    # path('', views.landing, name='landing'),
    # path('pricing/', views.pricing, name='pricing'),
    # path('products/', views.products, name='products'),
    # path('features/', views.features, name='features'),
    # path('docs/', views.docs, name='docs'),
    # path('contact/', views.contact, name='contact'),
    # path('privacy/', views.privacy, name='privacy'),
    # path('terms/', views.terms, name='terms'),
    # path('subscribe/', views.subscribe, name='subscribe'),
    # path('apikey/', views.apikey, name='apikey'),
    # path('servicebooking/', views.home, name='home'),
    # path('signup/', views.signup, name='signup'),
    # path('category/<int:category_id>/', views.service_list, name='service_list'),
    # path('service/<int:service_id>/', views.service_detail, name='service_detail'),
    # path('book/<int:service_id>/', views.book_service, name='book_service'),
    # path('cart/', views.view_cart, name='view_cart'),
    # path('cart/remove/<int:booking_id>/', views.remove_from_cart, name='remove_from_cart'),
    # path('payment-cart/<int:cart_id>/', views.payment, name='payment'),
    # path('process-payment-cart/<int:cart_id>/', views.process_payment_cart, name='process_payment_cart'),
    # path('my-bookings/', views.my_bookings, name='my_bookings'),
    # path('helper/enroll/', views.helper_enroll, name='helper_enroll'),
    # path('helper/dashboard/', views.helper_dashboard, name='helper_dashboard'),
    # path('helper/training/', views.training_slots_view, name='training_slots'),
    # path('helper/training/book/<int:slot_id>/', views.book_training_slot, name='book_training_slot'),
    # path('helper/training/complete/<int:slot_id>/', views.complete_training_slot, name='complete_training_slot'),
    # path('helper/job/update/<int:booking_id>/', views.update_job_status, name='update_job_status'),
    # path('submit-review/<int:booking_id>/', views.submit_review, name='submit_review'),
    
    # # API Parity Paths (Matching Node script structure)
    # path('api/payment/<str:payment_id>/', views.get_payment_details, name='api_get_payment'),
    # path('health/', views.health_check, name='health_check'),

]
