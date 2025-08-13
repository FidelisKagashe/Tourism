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
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'First Name'}))
    last_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'placeholder': 'Last Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'placeholder': 'Email Address'}))

    # Plain text input for JS widget. id must be id_phone_input.
    phone_number = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'id': 'id_phone_input',
            'placeholder': 'Phone Number',  # displayed while user types local number
            'autocomplete': 'tel'
        })
    )

    # Explicitly define nationality to ensure choices populate
    nationality = forms.ChoiceField(
        choices=countries,
        required=False,
        widget=CountrySelectWidget(attrs={'id': 'id_nationality', 'class': 'form-control'})
    )

    class Meta:
        model = CustomUser
        fields = ('username', 'first_name', 'last_name', 'email', 'phone_number', 'nationality', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Crispy helper (keeps your layout)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-3'),
                Column('last_name', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('username', css_class='form-group col-md-6 mb-3'),
                Column('email', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('phone_number', css_class='form-group col-md-6 mb-3'),
                Column('nationality', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Row(
                Column('password1', css_class='form-group col-md-6 mb-3'),
                Column('password2', css_class='form-group col-md-6 mb-3'),
                css_class='form-row'
            ),
            Submit('submit', 'Register', css_class='btn btn-primary btn-lg w-100')
        )

        # Add bootstrap classes to widgets except the phone which already has attrs
        for name, field in self.fields.items():
            existing = field.widget.attrs.get('class', '')
            if 'form-control' not in existing:
                field.widget.attrs['class'] = (existing + ' form-control').strip()

    @transaction.atomic
    def save(self, commit=True):
        user = super().save(commit=False)

        phone = self.cleaned_data.get('phone_number')
        nationality = self.cleaned_data.get('nationality')

        if phone:
            # phone should be E.164 string from JS (e.g. "+255712345678")
            user.phone_number = phone
        if nationality:
            user.nationality = nationality

        if commit:
            user.save()
            # create profile if you use it
            try:
                UserProfile.objects.get_or_create(user=user)
            except Exception:
                pass

        return user

class CustomAuthenticationForm(AuthenticationForm):
    """Custom login form."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'username',
            'password',
            HTML('<div class="form-check mb-3">'
                 '<input class="form-check-input" type="checkbox" name="remember_me" id="remember_me">'
                 '<label class="form-check-label" for="remember_me">Remember me</label>'
                 '</div>'),
            Submit('submit', 'Login', css_class='btn btn-primary btn-lg w-100')
        )
        
        # Add Bootstrap classes
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Username or Email'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })

class UserProfileForm(forms.ModelForm):
    """Form for editing user profile."""
    
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
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'dietary_requirements': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'accessibility_needs': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h6 class="mb-3">Basic Information</h6>'),
            Row(
                Column('first_name', css_class='form-group col-md-6 mb-3'),
                Column('last_name', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('email', css_class='form-group col-md-6 mb-3'),
                Column('phone_number', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('date_of_birth', css_class='form-group col-md-4 mb-3'),
                Column('gender', css_class='form-group col-md-4 mb-3'),
                Column('nationality', css_class='form-group col-md-4 mb-3'),
            ),
            'bio',
            HTML('<hr><h6 class="mb-3">Travel Preferences</h6>'),
            Row(
                Column('travel_experience_level', css_class='form-group col-md-6 mb-3'),
                Column('preferred_accommodation_type', css_class='form-group col-md-6 mb-3'),
            ),
            'dietary_requirements',
            'accessibility_needs',
            HTML('<hr><h6 class="mb-3">Communication Preferences</h6>'),
            'newsletter_subscription',
            'marketing_emails',
            Submit('submit', 'Update Profile', css_class='btn btn-primary')
        )
        
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            if field_name not in ['newsletter_subscription', 'marketing_emails']:
                field.widget.attrs.update({'class': 'form-control'})

class ExtendedProfileForm(forms.ModelForm):
    """Form for extended profile information."""
    
    class Meta:
        model = UserProfile
        fields = [
            'emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relationship',
            'passport_number', 'passport_expiry', 'passport_issuing_country',
            'medical_conditions', 'medications', 'allergies',
            'has_travel_insurance', 'insurance_provider', 'insurance_policy_number'
        ]
        widgets = {
            'passport_expiry': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'medical_conditions': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'medications': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'allergies': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            HTML('<h6 class="mb-3">Emergency Contact</h6>'),
            Row(
                Column('emergency_contact_name', css_class='form-group col-md-6 mb-3'),
                Column('emergency_contact_relationship', css_class='form-group col-md-6 mb-3'),
            ),
            'emergency_contact_phone',
            HTML('<hr><h6 class="mb-3">Travel Documents</h6>'),
            Row(
                Column('passport_number', css_class='form-group col-md-6 mb-3'),
                Column('passport_expiry', css_class='form-group col-md-6 mb-3'),
            ),
            'passport_issuing_country',
            HTML('<hr><h6 class="mb-3">Medical Information</h6>'),
            'medical_conditions',
            'medications',
            'allergies',
            HTML('<hr><h6 class="mb-3">Travel Insurance</h6>'),
            'has_travel_insurance',
            Row(
                Column('insurance_provider', css_class='form-group col-md-6 mb-3'),
                Column('insurance_policy_number', css_class='form-group col-md-6 mb-3'),
            ),
            Submit('submit', 'Update Extended Profile', css_class='btn btn-primary')
        )
        
        # Add Bootstrap classes to all fields
        for field_name, field in self.fields.items():
            if field_name not in ['has_travel_insurance']:
                field.widget.attrs.update({'class': 'form-control'})