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
