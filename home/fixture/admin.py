from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (
    User, UserProfile, Category, Service, ServiceProfessional,
    ProfessionalDocuments, Booking, JobTracking, Payment, Invoice,
    Review, Complaint, Notification
)

class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'email', 'role', 'is_verified', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('is_customer', 'is_professional', 'phone_number', 'role', 'is_verified')}),
    )
    add_fieldsets = UserAdmin.add_fieldsets + (
        (None, {'fields': ('is_customer', 'is_professional', 'phone_number', 'role', 'is_verified')}),
    )

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'latitude', 'longitude')

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'base_price', 'duration')
    list_filter = ('category',)

@admin.register(ServiceProfessional)
class ServiceProfessionalAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'experience_years', 'safety_score', 'availability_status', 'is_verified')
    list_filter = ('category', 'is_verified', 'availability_status')
    search_fields = ('user__username', 'bio')

@admin.register(ProfessionalDocuments)
class ProfessionalDocumentsAdmin(admin.ModelAdmin):
    list_display = ('professional', 'document_type', 'verification_status', 'uploaded_at')
    list_filter = ('document_type', 'verification_status')

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'customer', 'professional', 'service', 'booking_date', 'status')
    list_filter = ('status', 'booking_date')
    search_fields = ('customer__username', 'professional__user__username')

@admin.register(JobTracking)
class JobTrackingAdmin(admin.ModelAdmin):
    list_display = ('booking', 'status', 'updated_at')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('booking', 'amount', 'payment_method', 'payment_status', 'paid_at')
    list_filter = ('payment_method', 'payment_status')

@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ('invoice_number', 'booking', 'total_amount', 'generated_at')

@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ('booking', 'rating', 'created_at')

@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('booking', 'status', 'created_at')
    list_filter = ('status',)

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'is_read', 'created_at')
    list_filter = ('is_read',)

# Register existing User model
admin.site.register(User, CustomUserAdmin)