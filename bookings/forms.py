from django import forms
from django.forms import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML
from .models import Booking, BookingParticipant, BookingPayment

class BookingForm(forms.ModelForm):
    """Form for creating bookings."""
    
    class Meta:
        model = Booking
        fields = [
            'tour_availability', 'number_of_participants', 'accommodation_type',
            'special_requirements', 'dietary_requirements'
        ]
        widgets = {
            'special_requirements': forms.Textarea(attrs={'rows': 3}),
            'dietary_requirements': forms.Textarea(attrs={'rows': 3}),
        }
    
    def __init__(self, *args, **kwargs):
        tour_package = kwargs.pop('tour_package', None)
        super().__init__(*args, **kwargs)
        
        if tour_package:
            self.fields['tour_availability'].queryset = tour_package.availability.filter(
                is_available=True,
                available_spots__gt=0
            )
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('tour_availability', css_class='form-group col-md-6 mb-3'),
                Column('number_of_participants', css_class='form-group col-md-6 mb-3'),
            ),
            'accommodation_type',
            'special_requirements',
            'dietary_requirements',
        )
        
        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

class BookingParticipantForm(forms.ModelForm):
    """Form for booking participants."""
    
    class Meta:
        model = BookingParticipant
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'nationality',
            'passport_number', 'dietary_requirements', 'medical_conditions'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'dietary_requirements': forms.Textarea(attrs={'rows': 2}),
            'medical_conditions': forms.Textarea(attrs={'rows': 2}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})

# Create formset for participants
BookingParticipantFormSet = inlineformset_factory(
    Booking,
    BookingParticipant,
    form=BookingParticipantForm,
    extra=1,
    can_delete=True,
    min_num=1,
    validate_min=True
)

class PaymentForm(forms.ModelForm):
    """Form for processing payments."""
    
    class Meta:
        model = BookingPayment
        fields = ['payment_method']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'payment_method',
            HTML('<div class="alert alert-info mt-3">'
                 '<strong>Note:</strong> This is a demo payment system. '
                 'No actual charges will be made.'
                 '</div>'),
            Submit('submit', 'Process Payment', css_class='btn btn-primary btn-lg')
        )
        
        self.fields['payment_method'].widget.attrs.update({'class': 'form-control'})