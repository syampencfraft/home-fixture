from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import (
    RegistrationForm, ServiceProfessionalProfileForm, LoginForm, 
    CustomerProfileForm, ServiceListingForm, ServiceSearchForm, 
    BookingForm, PaymentForm, ReviewForm, AdminManagementForm,
    JobUpdateForm
)
from .models import Category, ServiceProfessional, Booking, Service, JobTracking, UserProfile, Payment, Review

from django.shortcuts import get_object_or_404


def index(request):
    if request.user.is_authenticated:
        if request.user.is_professional:
            return redirect('dashboard')
        else:
            return redirect('home')
    return render(request,'index.html')


def home(request):
    categories = Category.objects.all()
    services = Service.objects.all()
    # Relaxed filter for development/testing visibility
    top_pros = ServiceProfessional.objects.all().order_by('-safety_score')[:4]
    
    context = {
        'categories': categories,
        'services': services,
        'top_pros': top_pros
    }
    return render(request, 'home.html', context)

def category_professionals(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    professionals = ServiceProfessional.objects.filter(category=category)
    return render(request, 'category_pros.html', {'category': category, 'professionals': professionals})

def service_professionals(request, service_id):
    service = get_object_or_404(Service, id=service_id)
    professionals = ServiceProfessional.objects.filter(category=service.category)
    return render(request, 'service_pros.html', {'service': service, 'professionals': professionals})

def register_view(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, "Registration successful! Please login to continue.")
            return redirect('login') 
    else:
        form = RegistrationForm()
    return render(request, 'register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"You are now logged in as {username}.")
                if user.is_professional:
                    return redirect('dashboard')
                else:
                    return redirect('home')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.")
    
    form = LoginForm()
    return render(request, 'login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('index')

@login_required
def dashboard(request):
    if request.user.is_professional:
        return render(request, 'pro_dashboard.html')
    else:
        return redirect('home')
    


@login_required
def update_customer_profile(request):
    if not request.user.is_customer:
        messages.error(request, "Only customers can access this page.")
        return redirect('home')

    profile, created = UserProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = CustomerProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Save User fields
            if form.cleaned_data.get('profile_picture'):
                request.user.profile_picture = form.cleaned_data['profile_picture']
                request.user.save()
            form.save()
            messages.success(request, "Your profile has been updated!")
            return redirect('profile_view')
    else:
        form = CustomerProfileForm(instance=profile, initial={'profile_picture': request.user.profile_picture})

    return render(request, 'update_customer_profile.html', {'form': form, 'profile': profile})

@login_required
def update_professional_profile(request):
    if not request.user.is_professional:
        messages.error(request, "Only service professionals can access this page.")
        return redirect('home')

    profile, created = ServiceProfessional.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ServiceProfessionalProfileForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            # Save User fields
            if form.cleaned_data.get('profile_picture'):
                request.user.profile_picture = form.cleaned_data['profile_picture']
                request.user.save()
            form.save()
            messages.success(request, "Your professional profile has been updated!")
            return redirect('profile_view')
    else:
        form = ServiceProfessionalProfileForm(instance=profile, initial={'profile_picture': request.user.profile_picture})

    return render(request, 'update_profile.html', {'form': form, 'profile': profile})

@login_required
def book_professional(request, pro_id):
    if not request.user.is_customer:
        messages.error(request, "Only customers can book professionals.")
        return redirect('home')

    professional = get_object_or_404(ServiceProfessional, id=pro_id)
    
    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.customer = request.user
            booking.professional = professional
            booking.save()
            messages.success(request, f"Booking request for {booking.service.name} sent!")
            return redirect('customer_bookings')
    else:
        selected_service_id = request.GET.get('service')
        initial_data = {}
        if selected_service_id:
            initial_data['service'] = selected_service_id
        
        form = BookingForm(initial=initial_data)
        # Filter services to only those offered by the professional's category
        form.fields['service'].queryset = Service.objects.filter(category=professional.category)

    return render(request, 'book_service.html', {
        'pro': professional,
        'form': form
    })

@login_required
def customer_bookings(request):
    if not request.user.is_customer:
        return redirect('home')
    bookings = Booking.objects.filter(customer=request.user).order_by('-booking_date')
    return render(request, 'customer_bookings.html', {'bookings': bookings})

@login_required
def professional_bookings(request):
    if not request.user.is_professional:
        return redirect('home')
    
    profile = get_object_or_404(ServiceProfessional, user=request.user)
    bookings = Booking.objects.filter(professional=profile).order_by('-booking_date')
    return render(request, 'professional_bookings.html', {'bookings': bookings})

@login_required
def update_booking_status(request, booking_id, status):
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Check permission (only professional can update status)
    if not request.user.is_professional or booking.professional.user != request.user:
        messages.error(request, "You do not have permission to update this booking.")
        return redirect('home')
    
    status_upper = status.upper()
    if status_upper in dict(Booking.STATUS_CHOICES):
        booking.status = status_upper
        booking.save()
        messages.success(request, f"Booking status updated to {status.capitalize()}.")
        
        # Auto-generate invoice if completed
        if status_upper == 'COMPLETED':
            from .models import Invoice
            import uuid
            Invoice.objects.get_or_create(
                booking=booking,
                defaults={
                    'invoice_number': str(uuid.uuid4())[:8].upper(),
                    'total_amount': booking.service.base_price if booking.service else 0
                }
            )
            messages.success(request, "Invoice generated.")
    else:
        messages.error(request, "Invalid status update.")
        
    return redirect('professional_bookings')
@login_required
def upload_documents(request):
    if not request.user.is_professional:
        return redirect('home')
    
    profile = get_object_or_404(ServiceProfessional, user=request.user)
    from .models import ProfessionalDocuments
    
    if request.method == 'POST':
        doc_type = request.POST.get('document_type')
        doc_file = request.FILES.get('document_file')
        
        if doc_type and doc_file:
            ProfessionalDocuments.objects.create(
                professional=profile,
                document_type=doc_type,
                document_file=doc_file
            )
            messages.success(request, "Document uploaded for verification.")
            return redirect('upload_documents')
            
    docs = ProfessionalDocuments.objects.filter(professional=profile)
    return render(request, 'upload_docs.html', {'docs': docs})

@login_required
def view_invoice(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.user != booking.customer and request.user != booking.professional.user:
        return redirect('home')
    
    from .models import Invoice
    invoice = get_object_or_404(Invoice, booking=booking)
    return render(request, 'invoice.html', {'invoice': invoice, 'booking': booking})

@login_required
def submit_review(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.user != booking.customer or booking.status != 'COMPLETED':
        messages.error(request, "You can only review completed services you booked.")
        return redirect('customer_bookings')
    
    if Review.objects.filter(booking=booking).exists():
        messages.warning(request, "You have already reviewed this service.")
        return redirect('customer_bookings')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.booking = booking
            review.save()
            messages.success(request, "Thank you for your feedback!")
            return redirect('customer_bookings')
    else:
        form = ReviewForm()
            
    return render(request, 'submit_review.html', {'booking': booking, 'form': form})

@login_required
def submit_complaint(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.user != booking.customer:
        return redirect('home')
        
    if request.method == 'POST':
        description = request.POST.get('description')
        if description:
            from .models import Complaint
            Complaint.objects.create(booking=booking, description=description)
            messages.success(request, "Complaint submitted. Our admin will look into it.")
            return redirect('customer_bookings')
            
    return render(request, 'submit_complaint.html', {'booking': booking})

@login_required
def notifications_view(request):
    notifications = request.user.notifications.all().order_by('-created_at')
    notifications.update(is_read=True)
    return render(request, 'notifications.html', {'notifications': notifications})

@login_required
def track_job(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.user != booking.customer and request.user != booking.professional.user:
        return redirect('home')
    
    # Mock tracking status or get existing
    tracking, created = JobTracking.objects.get_or_create(
        booking=booking,
        defaults={'latitude': 12.9716, 'longitude': 77.5946, 'status': 'ON_THE_WAY'}
    )
    
    # Timeline steps based on status
    steps = [
        {'id': 'PENDING', 'label': 'Booking Received', 'completed': True},
        {'id': 'CONFIRMED', 'label': 'Pro Confirmed', 'completed': booking.status in ['CONFIRMED', 'COMPLETED']},
        {'id': 'ON_THE_WAY', 'label': 'On the Way', 'completed': tracking.status in ['ON_THE_WAY', 'ARRIVED'] or booking.status == 'COMPLETED'},
        {'id': 'ARRIVED', 'label': 'Work in Progress', 'completed': tracking.status == 'ARRIVED' or booking.status == 'COMPLETED'},
        {'id': 'COMPLETED', 'label': 'Service Finished', 'completed': booking.status == 'COMPLETED'},
    ]

    return render(request, 'tracking.html', {
        'booking': booking, 
        'tracking': tracking,
        'steps': steps
    })

@login_required
def job_details(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.user != booking.customer and request.user != booking.professional.user:
        return redirect('home')
    
    payment = getattr(booking, 'payment', None)
    review = getattr(booking, 'review', None)
    
    return render(request, 'job_details.html', {
        'booking': booking,
        'payment': payment,
        'review': review
    })

@login_required
def search_services(request):
    form = ServiceSearchForm(request.GET or None)
    services = Service.objects.all()
    if form.is_valid():
        if form.cleaned_data.get('category'):
            services = services.filter(category=form.cleaned_data['category'])
        if form.cleaned_data.get('price_range'):
            services = services.filter(base_price__lte=form.cleaned_data['price_range'])
        # Location and Rating filtering would require geolocation or complex queries
        
    return render(request, 'search_results.html', {'form': form, 'services': services})

@login_required
def list_service(request):
    if not request.user.is_professional:
        return redirect('home')
    
    if request.method == 'POST':
        form = ServiceListingForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Service listed successfully!")
            return redirect('dashboard')
    else:
        form = ServiceListingForm()
    
    return render(request, 'list_service.html', {'form': form})

@login_required
def process_payment(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if request.user != booking.customer:
        return redirect('home')
    
    payment, created = Payment.objects.get_or_create(
        booking=booking,
        defaults={'amount': booking.service.base_price if booking.service else 0}
    )
    
    if request.method == 'POST':
        form = PaymentForm(request.POST, instance=payment)
        if form.is_valid():
            payment = form.save()
            payment.payment_status = 'SUCCESS'
            payment.save()
            messages.success(request, "Payment successful!")
            return redirect('customer_bookings')
    else:
        form = PaymentForm(instance=payment)
    
    return render(request, 'payment.html', {'form': form, 'booking': booking})

@login_required
def admin_management(request):
    if not request.user.is_staff:
        return redirect('home')
    
    if request.method == 'POST':
        form = AdminManagementForm(request.POST)
        if form.is_valid():
            # Logic for admin actions
            messages.success(request, "Admin action processed.")
            return redirect('admin_management')
    else:
        form = AdminManagementForm()
    
    return render(request, 'admin_management.html', {'form': form})
@login_required
def update_job(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    if not request.user.is_professional or booking.professional.user != request.user:
        messages.error(request, "Access denied.")
        return redirect('home')
    
    if request.method == 'POST':
        form = JobUpdateForm(request.POST, instance=booking)
        if form.is_valid():
            booking = form.save()
            # If status changed to completed, ensure invoice exists
            if booking.status == 'COMPLETED':
                from .models import Invoice
                import uuid
                Invoice.objects.get_or_create(
                    booking=booking,
                    defaults={
                        'invoice_number': str(uuid.uuid4())[:8].upper(),
                        'total_amount': booking.service.base_price if booking.service else 0
                    }
                )
            
            # Update tracking status if applicable
            tracking = getattr(booking, 'tracking', None)
            if tracking:
                if booking.status == 'COMPLETED':
                    tracking.status = 'ARRIVED' # Or add a 'FINISHED' status if models allow
                    tracking.save()

            messages.success(request, "Job updated successfully.")
            return redirect('professional_bookings')
    else:
        form = JobUpdateForm(instance=booking)
    
    return render(request, 'update_job.html', {'form': form, 'booking': booking})

@login_required
def profile_view(request):
    return render(request, 'profile.html')
