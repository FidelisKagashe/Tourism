# forms.py (Tailwind-ready)
from django import forms
from django.forms import inlineformset_factory
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML
from .models import Booking, BookingParticipant

# common Tailwind classes for inputs
BASE_INPUT_CLASSES = (
    "w-full px-3 py-2 border border-gray-300 rounded-md "
    "focus:outline-none focus:ring-2 focus:ring-[#C18D45]"
)

BASE_TEXTAREA_CLASSES = (
    "w-full px-3 py-2 border border-gray-300 rounded-md "
    "focus:outline-none focus:ring-2 focus:ring-[#C18D45] resize-none"
)

BASE_SELECT_CLASSES = BASE_INPUT_CLASSES

class QuickBookingForm(forms.ModelForm):
    """
    Minimal booking form for fast bookings.
    Contact name/email are prefilled from request.user in the view.
    """
    class Meta:
        model = Booking
        fields = [
            'tour_availability',
            'number_of_participants',
            'accommodation_type',
            'contact_phone',
            # special_requirements removed from strict requirement; keep short if needed
        ]
        widgets = {
            'tour_availability': forms.Select(attrs={
                'class': BASE_SELECT_CLASSES,
            }),
            'number_of_participants': forms.NumberInput(attrs={
                'min': 1,
                'class': BASE_INPUT_CLASSES,
            }),
            'accommodation_type': forms.Select(attrs={
                'class': BASE_SELECT_CLASSES,
            }),
            'contact_phone': forms.TextInput(attrs={
                'placeholder': '+2557...',
                'class': BASE_INPUT_CLASSES,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Ensure no widget has autofocus enabled
        for f in self.fields.values():
            if 'autofocus' in f.widget.attrs:
                f.widget.attrs.pop('autofocus', None)

        # Ensure Tailwind classes exist for all fields (merge if template/field already set classes)
        for name, field in self.fields.items():
            default = BASE_INPUT_CLASSES
            if isinstance(field.widget, forms.Textarea):
                default = BASE_TEXTAREA_CLASSES
            if isinstance(field.widget, (forms.Select, forms.NullBooleanSelect,
                                         forms.SelectMultiple)):
                default = BASE_SELECT_CLASSES

            existing = field.widget.attrs.get('class', '')
            # avoid duplicating classes
            classes = (existing + ' ' + default).strip() if existing else default
            field.widget.attrs['class'] = classes

            # make sure autofocus is not present
            field.widget.attrs['autofocus'] = False

        # Simple Crispy layout for compact UI using Tailwind utility classes
        self.helper = FormHelper()
        self.helper.form_tag = False  # we will render the form tag in template
        self.helper.layout = Layout(
            Row(
                Column('tour_availability', css_class='w-full md:w-1/2 px-2 mb-2'),
                Column('number_of_participants', css_class='w-full md:w-1/2 px-2 mb-2'),
                css_class='flex flex-wrap -mx-2'
            ),
            Row(
                Column('accommodation_type', css_class='w-full md:w-1/2 px-2 mb-2'),
                Column('contact_phone', css_class='w-full md:w-1/2 px-2 mb-2'),
            ),
        )


class SimpleParticipantForm(forms.ModelForm):
    """Only first_name, last_name and optional date_of_birth for speed."""
    class Meta:
        model = BookingParticipant
        fields = ['first_name', 'last_name', 'date_of_birth']
        widgets = {
            'first_name': forms.TextInput(attrs={'class': BASE_INPUT_CLASSES}),
            'last_name': forms.TextInput(attrs={'class': BASE_INPUT_CLASSES}),
            'date_of_birth': forms.DateInput(attrs={
                'type': 'date',
                'class': BASE_INPUT_CLASSES,
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Add Tailwind classes to all fields, merging with any existing classes
        for field_name, field in self.fields.items():
            existing = field.widget.attrs.get('class', '')
            default = BASE_INPUT_CLASSES
            if isinstance(field.widget, forms.Textarea):
                default = BASE_TEXTAREA_CLASSES
            classes = (existing + ' ' + default).strip() if existing else default
            field.widget.attrs['class'] = classes

            # Remove autofocus if present
            if 'autofocus' in field.widget.attrs:
                field.widget.attrs.pop('autofocus')
            field.widget.attrs['autofocus'] = False


# Participant formset: optional (extra 0 default)
SimpleParticipantFormSet = inlineformset_factory(
    Booking,
    BookingParticipant,
    form=SimpleParticipantForm,
    extra=0,
    can_delete=True,
    min_num=0,
    validate_min=False
)
