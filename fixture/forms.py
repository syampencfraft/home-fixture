from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, ServiceProfessional

class RegistrationForm(UserCreationForm):
    ROLE_CHOICES = [
        ('customer', 'Customer'),
        ('professional', 'Service Professional'),
    ]
    role = forms.ChoiceField(choices=ROLE_CHOICES, widget=forms.RadioSelect)

    class Meta(UserCreationForm.Meta):
        model = User
        fields = UserCreationForm.Meta.fields + ('email', 'phone_number')

    def save(self, commit=True):
        user = super().save(commit=False)
        role = self.cleaned_data.get('role')
        if role == 'customer':
            user.is_customer = True
        elif role == 'professional':
            user.is_professional = True
        if commit:
            user.save()
        return user
    

class ServiceProfessionalProfileForm(forms.ModelForm):
    class Meta:
        model = ServiceProfessional
        fields = ['category', 'bio', 'experience_years', 'profile_picture']
        widgets = {
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'experience_years': forms.NumberInput(attrs={'class': 'form-control'}),
            'profile_picture': forms.FileInput(attrs={'class': 'form-control'}),
        }