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
            'special_requirements': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]',
                'autofocus': False
            }),
            'dietary_requirements': forms.Textarea(attrs={
                'rows': 3,
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]',
                'autofocus': False
            }),
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
                Column('tour_availability', css_class='w-full md:w-1/2 px-2 mb-4'),
                Column('number_of_participants', css_class='w-full md:w-1/2 px-2 mb-4'),
                css_class='flex flex-wrap -mx-2'
            ),
            Row(
                Column('accommodation_type', css_class='w-full px-2 mb-4'),
            ),
            Row(
                Column('special_requirements', css_class='w-full px-2 mb-4'),
            ),
            Row(
                Column('dietary_requirements', css_class='w-full px-2 mb-4'),
            ),
            Submit('submit', 'Submit Booking Request', css_class='w-full bg-[#C18D45] hover:bg-[#a5793a] text-white font-bold py-3 px-4 rounded-md shadow-md transition duration-300 cursor-pointer')
        )
        
        # Add Tailwind classes to all fields
        for field_name, field in self.fields.items():
            base_classes = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]'
            if field.widget.attrs.get('class'):
                field.widget.attrs['class'] += ' ' + base_classes
            else:
                field.widget.attrs['class'] = base_classes
            
            # Remove autofocus
            if 'autofocus' in field.widget.attrs:
                field.widget.attrs.pop('autofocus')
            field.widget.attrs['autofocus'] = False

class BookingParticipantForm(forms.ModelForm):
    """Form for booking participants."""
    
    class Meta:
        model = BookingParticipant
        fields = [
            'first_name', 'last_name', 'date_of_birth', 'nationality',
            'passport_number', 'dietary_requirements', 'medical_conditions'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]',
                'autofocus': False
            }),
            'dietary_requirements': forms.Textarea(attrs={
                'rows': 2,
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]',
                'autofocus': False
            }),
            'medical_conditions': forms.Textarea(attrs={
                'rows': 2,
                'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]',
                'autofocus': False
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add Tailwind classes to all fields
        for field_name, field in self.fields.items():
            base_classes = 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]'
            if field.widget.attrs.get('class'):
                field.widget.attrs['class'] += ' ' + base_classes
            else:
                field.widget.attrs['class'] = base_classes
            
            # Remove autofocus
            if 'autofocus' in field.widget.attrs:
                field.widget.attrs.pop('autofocus')
            field.widget.attrs['autofocus'] = False

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
            HTML('<div class="mt-4 p-4 bg-green-100 border border-green-300 rounded-md text-green-700">'
                 '<strong>Note:</strong> This is a demo payment system. '
                 'No actual charges will be made.'
                 '</div>'),
            Submit('submit', 'Process Payment', css_class='w-full mt-4 bg-[#C18D45] hover:bg-[#a5793a] text-white font-bold py-3 px-4 rounded-md shadow-md transition duration-300 cursor-pointer')
        )
        
        # Add Tailwind classes to payment method field
        self.fields['payment_method'].widget.attrs.update({
            'class': 'w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-[#C18D45]',
            'autofocus': False
        })