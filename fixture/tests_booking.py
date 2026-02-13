from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from .models import Category, Service, ServiceProfessional, Booking

User = get_user_model()

class BookingTest(TestCase):
    def setUp(self):
        self.category = Category.objects.create(name="Plumbing", description="Fix leaks")
        self.service = Service.objects.create(category=self.category, name="Leak Fix", base_price=50, duration=60)
        
        self.customer = User.objects.create_user(username="customer", password="password", is_customer=True)
        self.pro_user = User.objects.create_user(username="pro", password="password", is_professional=True)
        
        # We need to manually create the professional profile if it's not created automatically
        self.pro_profile = ServiceProfessional.objects.create(
            user=self.pro_user,
            category=self.category,
            bio="Expert plumber",
            experience_years=5,
            is_verified=False # Testing with unverified pro
        )
        
        self.client = Client()
        self.client.login(username="customer", password="password")

    def test_booking_creation(self):
        url = reverse('book_professional', kwargs={'pro_id': self.pro_profile.id})
        data = {
            'service': self.service.id,
            'time_slot': 'Morning',
            'booking_date': '2026-05-01'
        }
        response = self.client.post(url, data)
        
        # Check if booking exists
        self.assertTrue(Booking.objects.filter(customer=self.customer, professional=self.pro_profile).exists())
        self.assertEqual(response.status_code, 302) # Redirect to customer_bookings

    def test_home_page_shows_pro(self):
        url = reverse('home')
        response = self.client.get(url)
        self.assertContains(response, "pro")

    def test_track_job_view(self):
        # Create a booking first
        booking = Booking.objects.create(
            customer=self.customer,
            professional=self.pro_profile,
            service=self.service,
            booking_date="2026-05-01",
            time_slot="Morning"
        )
        url = reverse('track_job', kwargs={'booking_id': booking.id})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Tracking") # Assuming tracking.html has 'Tracking' or similar content

