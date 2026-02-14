from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.validators import RegexValidator
from .models import User, ServiceProfessional, UserProfile, Category, Service, Booking, Payment, Review, Complaint

# Validators
alphabets_only = RegexValidator(r'^[a-zA-Z\s]+$', 'Only alphabets are allowed.')
digits_only = RegexValidator(r'^\d+$', 'Only digits are allowed.')

class RegistrationForm(UserCreationForm):
    full_name = forms.CharField(validators=[alphabets_only], help_text="Mandatory, alphabets only")
    role = forms.ChoiceField(
        choices=[('customer', 'Customer'), ('professional', 'Service Provider')],
        widget=forms.RadioSelect
    )
    terms_accepted = forms.BooleanField(required=True, label="Terms & Conditions", help_text="Accept policy")
    profile_picture = forms.ImageField(required=False, label="Profile Picture", widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'phone_number', 'full_name', 'role', 'terms_accepted', 'profile_picture')

    def clean_phone_number(self):
        phone = self.cleaned_data.get('phone_number')
        if phone and (not phone.isdigit() or len(phone) != 10):
            raise forms.ValidationError("Mobile number must be exactly 10 digits.")
        return phone

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data.get('role')
        if role == 'customer':
            user.is_customer = True
        elif role == 'professional':
            user.is_professional = True
        user.role = role
        user.terms_accepted = self.cleaned_data.get('terms_accepted')
        user.profile_picture = self.cleaned_data.get('profile_picture')
        if commit:
            user.save()
            # Create UserProfile or ServiceProfessional profile automatically
            UserProfile.objects.get_or_create(user=user, full_name=self.cleaned_data.get('full_name'))
            if user.is_professional:
                ServiceProfessional.objects.get_or_create(user=user)
        return user

class LoginForm(AuthenticationForm):
    username = forms.CharField(label="Email / Mobile", widget=forms.TextInput(attrs={'class': 'form-control'}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

class CustomerProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = UserProfile
        fields = ['address', 'city', 'pincode', 'latitude', 'longitude']
        widgets = {
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'city': forms.TextInput(attrs={'class': 'form-control'}),
            'pincode': forms.TextInput(attrs={'class': 'form-control', 'maxlength': 6}),
            'latitude': forms.HiddenInput(),
            'longitude': forms.HiddenInput(),
        }

    def clean_pincode(self):
        pincode = self.cleaned_data.get('pincode')
        if pincode and (not pincode.isdigit() or len(pincode) != 6):
            raise forms.ValidationError("Pincode must be 6 digits.")
        return pincode

class ServiceProfessionalProfileForm(forms.ModelForm):
    profile_picture = forms.ImageField(required=False, widget=forms.FileInput(attrs={'class': 'form-control'}))

    class Meta:
        model = ServiceProfessional
        fields = ['category', 'bio', 'experience_years', 'availability_status']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'availability_status': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ServiceListingForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ['category', 'name', 'description', 'base_price', 'duration', 'is_active']
        widgets = {
            'category': forms.Select(attrs={'class': 'form-control'}),
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'base_price': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'duration': forms.TextInput(attrs={'class': 'form-control'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class ServiceSearchForm(forms.Form):
    category = forms.ModelChoiceField(queryset=Category.objects.all(), required=False, widget=forms.Select(attrs={'class': 'form-control'}))
    location = forms.CharField(required=False, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Area / city'}))
    price_range = forms.IntegerField(required=False, widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Max price'}))
    rating = forms.ChoiceField(choices=[('', 'Minimum rating')] + [(i, f'{i} Stars') for i in range(1, 6)], required=False, widget=forms.Select(attrs={'class': 'form-control'}))

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['service', 'booking_date', 'time_slot', 'service_address']
        widgets = {
            'service': forms.Select(attrs={'class': 'form-select'}),
            'booking_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'time_slot': forms.Select(attrs={'class': 'form-select'}, choices=[
                ('Morning', 'Morning (8:00 AM – 12:00 PM)'),
                ('Afternoon', 'Afternoon (12:00 PM – 4:00 PM)'),
                ('Evening', 'Evening (4:00 PM – 8:00 PM)'),
            ]),
            'service_address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter service location...'}),
        }
    
    confirmation = forms.BooleanField(required=True, label="Booking confirmation")

    def clean_booking_date(self):
        from django.utils import timezone
        date = self.cleaned_data.get('booking_date')
        if date and date < timezone.now():
            raise forms.ValidationError("Booking date must be in the future.")
        return date

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['payment_method', 'payment_details', 'amount']
        widgets = {
            'payment_method': forms.RadioSelect(attrs={'class': 'form-check-input'}),
            'payment_details': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Transaction details'}),
            'amount': forms.NumberInput(attrs={'class': 'form-control', 'readonly': 'readonly'}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'maxlength': 300}),
        }

class JobUpdateForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['status', 'requirements']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-control'}),
            'requirements': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Add specific requirements or notes for this job...'}),
        }

class AdminManagementForm(forms.Form):
    user_selection = forms.ModelChoiceField(queryset=User.objects.all(), widget=forms.Select(attrs={'class': 'form-control'}))
    action = forms.ChoiceField(choices=[('APPROVE', 'Approve'), ('REJECT', 'Reject')], widget=forms.Select(attrs={'class': 'form-control'}))
    remarks = forms.CharField(required=False, widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2}))
    status_update = forms.BooleanField(required=False, label="Active / Blocked", widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))