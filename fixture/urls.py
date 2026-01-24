
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('home/', views.home, name='home'),
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/update/', views.update_professional_profile, name='update_profile'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Booking URLs
    path('category/<int:category_id>/', views.category_professionals, name='category_professionals'),
    path('service/<int:service_id>/', views.service_professionals, name='service_professionals'),
    path('book/<int:pro_id>/', views.book_professional, name='book_professional'),
    path('bookings/customer/', views.customer_bookings, name='customer_bookings'),
    path('bookings/professional/', views.professional_bookings, name='professional_bookings'),
    path('bookings/update/<int:booking_id>/<str:status>/', views.update_booking_status, name='update_booking_status'),
    path('profile/documents/', views.upload_documents, name='upload_documents'),
    path('invoice/<int:booking_id>/', views.view_invoice, name='view_invoice'),
    path('review/<int:booking_id>/', views.submit_review, name='submit_review'),
    path('complaint/<int:booking_id>/', views.submit_complaint, name='submit_complaint'),
    path('notifications/', views.notifications_view, name='notifications'),
    path('track/<int:booking_id>/', views.track_job, name='track_job'),
]
