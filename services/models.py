from django.db import models
from django.contrib.auth.models import User

class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='categories/', blank=True, null=True)
    icon = models.CharField(max_length=50, default='fa-tools', help_text="FontAwesome icon class")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = "Service Categories"

class Service(models.Model):
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration_minutes = models.IntegerField(help_text="Duration in minutes")
    image = models.ImageField(upload_to='services/', blank=True, null=True)

    def __str__(self):
        return f"{self.name} - ${self.price}"

class Cart(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='carts')
    is_paid = models.BooleanField(default=False)
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def total_price(self):
        return sum(booking.service.price for booking in self.bookings.all())

    def __str__(self):
        status = "Paid" if self.is_paid else "Active"
        return f"Cart {self.id} for {self.user.username} ({status})"

class Booking(models.Model):
    STATUS_CHOICES = [
        ('PENDING_PAYMENT', 'Pending Payment'),
        ('PAID', 'Paid (Awaiting Assignment)'),
        ('ASSIGNED', 'Assigned'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('CANCELLED', 'Cancelled'),
    ]


    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='bookings')
    assigned_helper = models.ForeignKey('Helper', on_delete=models.SET_NULL, related_name='assigned_jobs', null=True, blank=True)
    booking_date = models.DateField()
    booking_time = models.TimeField()
    address = models.TextField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING_PAYMENT')
    cart = models.ForeignKey(Cart, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')

    
    # Razorpay fields
    razorpay_order_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_payment_id = models.CharField(max_length=100, blank=True, null=True)
    razorpay_signature = models.CharField(max_length=200, blank=True, null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.service.name} ({self.status})"

class Helper(models.Model):
    STATUS_CHOICES = [
        ('APPLIED', 'Applied'),
        ('TRAINING', 'Training'),
        ('CERTIFIED', 'Certified'),
        ('INACTIVE', 'Inactive'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='helper_profile')
    full_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    bio = models.TextField(blank=True)
    skills = models.TextField(help_text="Enter skills separated by commas")
    profile_image = models.ImageField(upload_to='helpers/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='APPLIED')
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    is_certified = models.BooleanField(default=False)
    total_training_hours = models.DecimalField(max_digits=5, decimal_places=1, default=0.0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} - {self.status}"

    @property
    def average_rating(self):
        reviews = self.reviews.all()
        if not reviews:
            return 0.0
        return round(sum(r.rating for r in reviews) / reviews.count(), 1)

class TrainingSlot(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    date = models.DateField()
    start_time = models.TimeField()
    duration_hours = models.FloatField(default=1.0)
    max_participants = models.IntegerField(default=1)
    participants = models.ManyToManyField(Helper, related_name='training_slots', blank=True)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.title} ({self.participants.count()}/{self.max_participants})"

class Review(models.Model):
    booking = models.OneToOneField('Booking', on_delete=models.CASCADE, related_name='review')
    helper = models.ForeignKey(Helper, on_delete=models.CASCADE, related_name='reviews')
    customer = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review for {self.booking} - {self.rating} stars"

# Subscripon Plan model


from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta

# class SubscriptionPlan(models.Model):

#     name = models.CharField(max_length=100)

#     price = models.DecimalField(
#         max_digits=10,
#         decimal_places=2
#     )

#     credits = models.IntegerField(default=0)

#     active = models.BooleanField(default=True)

#     def __str__(self):
#         return self.name


class SubscriptionType(models.TextChoices):
    BASIC = "basic", "Basic"
    PRO = "pro", "Pro"
    ENTERPRISE = "enterprise", "Enterprise"


class BillingPeriod(models.TextChoices):
    MONTHLY = "monthly", "Monthly"
    YEARLY = "yearly", "Yearly"


class Feature(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name   



class SubscriptionPlan(models.Model):

    product_code = models.CharField(
        max_length=50,
            # unique=True,
        default="TEMP"
    )
    plan_type = models.CharField(
        max_length=20,
        choices=SubscriptionType.choices, default=SubscriptionType.BASIC
    )

    name = models.CharField(
        max_length=100
    )

    description = models.CharField(
        max_length=255,
        default=""
    )

    is_custom_pricing = models.BooleanField(
        default=False
    )

    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True
    )

    billing_period = models.CharField(
        max_length=20,
        choices=BillingPeriod.choices,
        default=BillingPeriod.MONTHLY
    )

    features = models.ManyToManyField(
        Feature,
        blank=True
    )

    checkout_button_label = models.CharField(
        max_length=50,
        default="Get Started"
    )

    active = models.BooleanField(
        default=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
        
    )

    updated_at = models.DateTimeField(
        auto_now=True
    )
    is_featured = models.BooleanField(
        default=False
    )   
    included_requests = models.PositiveIntegerField(
    null=True,
    blank=True
    )
    is_unlimited = models.BooleanField(
    default=False
)
    def __str__(self):
        return f"{self.name} ({self.get_plan_type_display()})"


def default_expiry():
        return timezone.now() + timedelta(days=30)
# subscription model
class Subscription(models.Model):


    STATUS_CHOICES = [
        ("PENDING", "Pending"),
        ("ACTIVE", "Active"),
        ("EXPIRED", "Expired"),
        ("CANCELLED", "Cancelled"),
    ]

    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE
    )

    plan = models.ForeignKey(
        SubscriptionPlan,
        on_delete=models.CASCADE
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="PENDING"
    )

    razorpay_order_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    razorpay_payment_id = models.CharField(
        max_length=255,
        blank=True,
        null=True
    )

    razorpay_signature = models.TextField(
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    expires_at = models.DateTimeField(
            default=default_expiry
    )
    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"



   


from django.db import models


class SubscriptionRequest(models.Model):

    plan = models.ForeignKey(
        'SubscriptionPlan',
        on_delete=models.CASCADE
    )

    full_name = models.CharField(
        max_length=200
    )

    email = models.EmailField()

    company = models.CharField(
        max_length=200,
        blank=True
    )

    created_at = models.DateTimeField(
        auto_now_add=True
    )

    def __str__(self):
        return f"{self.full_name} - {self.plan.name}"


import secrets

class APIKey(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    # subscription = models.ForeignKey(
    #     Subscription,
    #     on_delete=models.CASCADE
    # )
    name = models.CharField(
        max_length=100,
        default="AISidekick API Key"
    )
    key = models.CharField(
        max_length=128,
        unique=True
    )
    is_active = models.BooleanField(
        default=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True
    )
    last_used_at = models.DateTimeField(
        blank=True,
        null=True
    )

    @staticmethod
    def generate_key():
        return secrets.token_hex(32)

    def save(self, *args, **kwargs):
        if not self.key:
            self.key = self.generate_key()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"API Key - {self.user.username}"
