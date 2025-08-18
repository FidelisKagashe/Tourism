from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import authenticate
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML
from .models import CustomUser, UserProfile
from django_countries import countries
from phonenumber_field.formfields import PhoneNumberField as PhoneFormField
from phonenumber_field.widgets import PhoneNumberPrefixWidget
from django_countries.widgets import CountrySelectWidget
from django.db import transaction

class CustomUserRegistrationForm(UserCreationForm):
    """
    Registration form that works with intl-tel-input JS.
    The visible phone input has id="id_phone_input" so the JS can initialize it.
    On submit JS will convert the shown phone to E.164 and set the input value before sending.
    """
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={
        'placeholder': 'First Name',
        'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]'
    }))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={
        'placeholder': 'Last Name',
        'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'placeholder': 'Email Address',
        'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]'
    }))

    # Plain text input for JS widget. id must be id_phone_input.
    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'id': 'id_phone_input',
            'placeholder': 'Phone Number',
            'autocomplete': 'tel',
            'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]'
        })
    )

    # Explicitly define nationality to ensure choices populate
    nationality = forms.ChoiceField(
        choices=countries,
        required=False,
        widget=CountrySelectWidget(attrs={
            'id': 'id_nationality', 
            'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]'
        })
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'nationality', 'password1', 'password2')
        widgets = {
            'username': forms.TextInput(attrs={
                'placeholder': 'Username',
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]'
            }),
            'password1': forms.PasswordInput(attrs={
                'placeholder': 'Password',
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]'
            }),
            'password2': forms.PasswordInput(attrs={
                'placeholder': 'Confirm Password',
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Crispy helper with Tailwind layout
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='w-full md:w-1/2 px-2 mb-4'),
                Column('last_name', css_class='w-full md:w-1/2 px-2 mb-4'),
                css_class='flex flex-wrap -mx-2'
            ),
            Row(
                Column('username', css_class='w-full md:w-1/2 px-2 mb-4'),
                Column('email', css_class='w-full md:w-1/2 px-2 mb-4'),
                css_class='flex flex-wrap -mx-2'
            ),
            Row(
                Column('phone_number', css_class='w-full md:w-1/2 px-2 mb-4'),
                Column('nationality', css_class='w-full md:w-1/2 px-2 mb-4'),
                css_class='flex flex-wrap -mx-2'
            ),
            Row(
                Column('password1', css_class='w-full md:w-1/2 px-2 mb-4'),
                Column('password2', css_class='w-full md:w-1/2 px-2 mb-4'),
                css_class='flex flex-wrap -mx-2'
            ),
            Submit('submit', 'Register', css_class='w-full bg-[#C18D45] hover:bg-[#a6783a] text-white font-bold py-3 px-4 rounded-md transition-colors cursor-pointer')
        )

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)

        phone = self.cleaned_data.get('phone_number')
        nationality = self.cleaned_data.get('nationality')

        if phone:
            user.phone_number = phone
        if nationality:
            user.nationality = nationality

        if commit:
            user.save()
            try:
                UserProfile.objects.get_or_create(user=user)
            except Exception:
                pass

        return user

class CustomAuthenticationForm(AuthenticationForm):
    """Custom login form with Tailwind styling."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username',
            'password',
            HTML('<div class="mb-4">'
                 '<label class="flex items-center">'
                 '<input class="form-checkbox text-[#C18D45] focus:ring-[#C18D45] rounded" type="checkbox" name="remember_me" id="remember_me">'
                 '<span class="ml-2 text-gray-700">Remember me</span>'
                 '</label>'
                 '</div>'),
            Submit('submit', 'Login', css_class='w-full bg-[#C18D45] hover:bg-[#a6783a] text-white font-bold py-3 px-4 rounded-md transition-colors cursor-pointer')
        )
        
        # Add Tailwind classes
        self.fields['username'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]',
            'placeholder': 'Username or Email'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]',
            'placeholder': 'Password'
        })

class UserProfileForm(forms.ModelForm):
    """Form for editing user profile with Tailwind styling."""
    
    class Meta:
        model = CustomUser
        fields = [
            'first_name', 'last_name', 'email', 'phone_number', 
            'date_of_birth', 'gender', 'nationality', 'bio',
            'dietary_requirements', 'accessibility_needs',
            'travel_experience_level', 'preferred_accommodation_type',
            'newsletter_subscription', 'marketing_emails'
        ]
        widgets = {
            'first_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]'
            }),
            'last_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]'
            }),
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]'
            }),
            'gender': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]'
            }),
            'nationality': CountrySelectWidget(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]'
            }),
            'bio': forms.Textarea(attrs={
                'rows': 4, 
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]'
            }),
            'dietary_requirements': forms.Textarea(attrs={
                'rows': 3, 
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]'
            }),
            'accessibility_needs': forms.Textarea(attrs={
                'rows': 3, 
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]'
            }),
            'travel_experience_level': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]'
            }),
            'preferred_accommodation_type': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]'
            }),
            'newsletter_subscription': forms.CheckboxInput(attrs={
                'class': 'rounded text-[#C18D45] focus:ring-[#C18D45]'
            }),
            'marketing_emails': forms.CheckboxInput(attrs={
                'class': 'rounded text-[#C18D45] focus:ring-[#C18D45]'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h6 class="text-xl font-semibold mb-4 text-[#C18D45]">Basic Information</h6>'),
            Row(
                Column('first_name', css_class='w-full md:w-1/2 px-2 mb-4'),
                Column('last_name', css_class='w-full md:w-1/2 px-2 mb-4'),
                css_class='flex flex-wrap -mx-2'
            ),
            Row(
                Column('email', css_class='w-full md:w-1/2 px-2 mb-4'),
                Column('phone_number', css_class='w-full md:w-1/2 px-2 mb-4'),
                css_class='flex flex-wrap -mx-2'
            ),
            Row(
                Column('date_of_birth', css_class='w-full md:w-1/3 px-2 mb-4'),
                Column('gender', css_class='w-full md:w-1/3 px-2 mb-4'),
                Column('nationality', css_class='w-full md:w-1/3 px-2 mb-4'),
                css_class='flex flex-wrap -mx-2'
            ),
            'bio',
            HTML('<hr class="my-6 border-gray-300"><h6 class="text-xl font-semibold mb-4 text-[#C18D45]">Travel Preferences</h6>'),
            Row(
                Column('travel_experience_level', css_class='w-full md:w-1/2 px-2 mb-4'),
                Column('preferred_accommodation_type', css_class='w-full md:w-1/2 px-2 mb-4'),
                css_class='flex flex-wrap -mx-2'
            ),
            'dietary_requirements',
            'accessibility_needs',
            HTML('<hr class="my-6 border-gray-300"><h6 class="text-xl font-semibold mb-4 text-[#C18D45]">Communication Preferences</h6>'),
            Row(
                Column('newsletter_subscription', css_class='w-full md:w-1/2 px-2 mb-4'),
                Column('marketing_emails', css_class='w-full md:w-1/2 px-2 mb-4'),
                css_class='flex flex-wrap -mx-2'
            ),
            Submit('submit', 'Update Profile', 
                   css_class='w-full md:w-auto bg-[#C18D45] hover:bg-[#a6783a] text-white font-bold py-2 px-6 rounded-md transition-colors cursor-pointer')
        )

class ExtendedProfileForm(forms.ModelForm):
    """Form for extended profile information with Tailwind styling."""
    
    class Meta:
        model = UserProfile
        fields = [
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship',
            'passport_number', 'passport_expiry', 'passport_issuing_country',
            'medical_conditions', 'medications', 'allergies',
            'has_travel_insurance', 'insurance_provider', 'insurance_policy_number'
        ]
        widgets = {
            'emergency_contact_name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]'
            }),
            'emergency_contact_phone': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]'
            }),
            'emergency_contact_relationship': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]'
            }),
            'passport_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]'
            }),
            'passport_expiry': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]'
            }),
            'passport_issuing_country': CountrySelectWidget(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]'
            }),
            'medical_conditions': forms.Textarea(attrs={
                'rows': 3, 
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]'
            }),
            'medications': forms.Textarea(attrs={
                'rows': 3, 
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]'
            }),
            'allergies': forms.Textarea(attrs={
                'rows': 3, 
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]'
            }),
            'has_travel_insurance': forms.CheckboxInput(attrs={
                'class': 'rounded text-[#C18D45] focus:ring-[#C18D45]'
            }),
            'insurance_provider': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]'
            }),
            'insurance_policy_number': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h6 class="text-xl font-semibold mb-4 text-[#C18D45]">Emergency Contact</h6>'),
            Row(
                Column('emergency_contact_name', css_class='w-full md:w-1/2 px-2 mb-4'),
                Column('emergency_contact_relationship', css_class='w-full md:w-1/2 px-2 mb-4'),
                css_class='flex flex-wrap -mx-2'
            ),
            'emergency_contact_phone',
            HTML('<hr class="my-6 border-gray-300"><h6 class="text-xl font-semibold mb-4 text-[#C18D45]">Travel Documents</h6>'),
            Row(
                Column('passport_number', css_class='w-full md:w-1/2 px-2 mb-4'),
                Column('passport_expiry', css_class='w-full md:w-1/2 px-2 mb-4'),
                css_class='flex flex-wrap -mx-2'
            ),
            'passport_issuing_country',
            HTML('<hr class="my-6 border-gray-300"><h6 class="text-xl font-semibold mb-4 text-[#C18D45]">Medical Information</h6>'),
            'medical_conditions',
            'medications',
            'allergies',
            HTML('<hr class="my-6 border-gray-300"><h6 class="text-xl font-semibold mb-4 text-[#C18D45]">Travel Insurance</h6>'),
            Row(
                Column('has_travel_insurance', css_class='w-full px-2 mb-4'),
            ),
            Row(
                Column('insurance_provider', css_class='w-full md:w-1/2 px-2 mb-4'),
                Column('insurance_policy_number', css_class='w-full md:w-1/2 px-2 mb-4'),
                css_class='flex flex-wrap -mx-2'
            ),
            Submit('submit', 'Update Extended Profile', 
                   css_class='w-full md:w-auto bg-[#C18D45] hover:bg-[#a6783a] text-white font-bold py-2 px-6 rounded-md transition-colors cursor-pointer')
        )