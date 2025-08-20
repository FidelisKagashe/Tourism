from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Div, HTML
from .models import ContactMessage, Newsletter

# Shared class constants for consistent dark-mode styling
COMMON_INPUT_CLASSES = (
    'w-full p-3 border rounded-md focus:outline-none focus:border-[#C18D45] focus:ring-2 focus:ring-[#C18D45]/50 '
    'bg-white text-gray-800 placeholder-gray-500 border-gray-300 '
    'dark:bg-gray-700 dark:text-gray-200 dark:placeholder-gray-400 dark:border-gray-600'
)
COMMON_TEXTAREA_CLASSES = (
    'w-full p-3 border rounded-md focus:outline-none focus:border-[#C18D45] focus:ring-2 focus:ring-[#C18D45]/50 '
    'bg-white text-gray-800 border-gray-300 '
    'dark:bg-gray-700 dark:text-gray-200 dark:border-gray-600'
)
SUBMIT_CLASSES = (
    'w-full px-4 py-3 bg-[#C18D45] hover:bg-[#a6793a] text-white font-medium rounded-md '
    'focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#C18D45] transition duration-300'
)


class ContactForm(forms.ModelForm):
    """Form for users to send contact messages."""

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Your Message',
                'class': COMMON_TEXTAREA_CLASSES
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'space-y-6'
        # style the fieldset container so it matches site cards and supports dark mode
        self.helper.layout = Layout(
            Fieldset(
                'Send Us a Message',
                Div(
                    'name',
                    css_class='space-y-2'
                ),
                Div(
                    'email',
                    css_class='space-y-2'
                ),
                Div(
                    'subject',
                    css_class='space-y-2'
                ),
                Div(
                    'message',
                    css_class='space-y-2'
                ),
                css_class='bg-white dark:bg-gray-800 p-6 rounded-xl shadow-md'
            ),
            Submit('submit', 'Send Message', css_class=SUBMIT_CLASSES)
        )
        
        # Remove auto-focus and update focus styling
        for name, field in self.fields.items():
            # preserve user's placeholder (label) but ensure dark-mode classes applied
            attrs = {
                'class': COMMON_INPUT_CLASSES,
                'placeholder': field.label,
            }
            # explicitly remove autofocus by not adding it; if you prefer to set attribute, adjust here
            field.widget.attrs.update(attrs)


class NewsletterForm(forms.ModelForm):
    """Form for newsletter subscription."""

    class Meta:
        model = Newsletter
        fields = ['name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'space-y-4'
        self.helper.layout = Layout(
            Fieldset(
                'Subscribe to Our Newsletter',
                Div(
                    'name',
                    css_class='space-y-2'
                ),
                Div(
                    'email',
                    css_class='space-y-2'
                ),
                css_class='bg-white dark:bg-gray-800 p-6 rounded-xl shadow-md'
            ),
            Submit('subscribe', 'Subscribe', css_class=SUBMIT_CLASSES)
        )
        
        # Remove auto-focus and update focus styling
        self.fields['name'].widget.attrs.update({
            'class': COMMON_INPUT_CLASSES,
            'placeholder': 'Your Name (optional)',
            # explicitly disable autofocus by not setting it; left out for predictable behavior
        })
        self.fields['email'].widget.attrs.update({
            'class': COMMON_INPUT_CLASSES,
            'placeholder': 'Your Email',
        })
