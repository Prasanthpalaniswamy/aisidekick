from django.contrib import admin
# from django.contrib import admin
from .models import SubscriptionPlan, Subscription,Feature,SubscriptionRequest
from .models import ServiceCategory, Service, Booking, Helper, TrainingSlot

admin.site.site_header = "Service Booking System Administration"
admin.site.site_title = "Service Booking System Admin Portal"
admin.site.index_title = "Welcome to the Service Booking System Management"

@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'icon')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'duration_minutes')
    list_filter = ('category',)
    search_fields = ('name', 'description')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'service', 'booking_date', 'booking_time', 'assigned_helper', 'status')
    list_editable = ('assigned_helper', 'status')
    list_filter = ('status', 'booking_date', 'assigned_helper')
    search_fields = ('user__username', 'service__name', 'address', 'assigned_helper__full_name')


@admin.register(Helper)
class HelperAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'user', 'status', 'rating', 'is_certified')
    list_filter = ('status', 'is_certified')
    search_fields = ('full_name', 'user__username', 'skills')

@admin.register(TrainingSlot)
class TrainingSlotAdmin(admin.ModelAdmin):
    list_display = ('title', 'participant_count', 'max_participants', 'date', 'start_time', 'is_completed')
    list_filter = ('is_completed', 'date')
    search_fields = ('title',)

    def participant_count(self, obj):
        return obj.participants.count()
    participant_count.short_description = 'Participants'



# admin.site.register(SubscriptionPlan)
admin.site.register(Subscription)
admin.site.register(SubscriptionRequest)


# from django.contrib import admin
# from .models import SubscriptionPlan, Feature


@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    search_fields = ["name"]


@admin.register(SubscriptionPlan)
class SubscriptionPlanAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "plan_type",
        "price",
        "billing_period",
        "active"
    )

    list_filter = (
        "plan_type",
        "billing_period",
        "active"
    )

    filter_horizontal = (
        "features",
    )