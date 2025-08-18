from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit, Div
from .models import ContactMessage, Newsletter


class ContactForm(forms.ModelForm):
    """Form for users to send contact messages."""

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={
                'rows': 5,
                'placeholder': 'Your Message',
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'space-y-6'
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
            ),
            Submit('submit', 'Send Message', 
                   css_class='w-full px-4 py-3 bg-[#C18D45] hover:bg-[#a6793a] text-white font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#C18D45] transition duration-300')
        )
        
        # Remove auto-focus and update focus styling
        for name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:border-[#C18D45] focus:ring-2 focus:ring-[#C18D45]/50',
                'placeholder': field.label,
                # Disable auto-focus on the first field
                'autofocus': False if name == 'name' else None,
            })


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
            ),
            Submit('subscribe', 'Subscribe', 
                   css_class='w-full px-4 py-3 bg-[#C18D45] hover:bg-[#a6793a] text-white font-medium rounded-md focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-[#C18D45] transition duration-300')
        )
        
        # Remove auto-focus and update focus styling
        self.fields['name'].widget.attrs.update({
            'class': 'w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:border-[#C18D45] focus:ring-2 focus:ring-[#C18D45]/50',
            'placeholder': 'Your Name (optional)',
            'autofocus': False,  # Explicitly disable auto-focus
        })
        self.fields['email'].widget.attrs.update({
            'class': 'w-full p-3 border border-gray-300 rounded-md focus:outline-none focus:border-[#C18D45] focus:ring-2 focus:ring-[#C18D45]/50',
            'placeholder': 'Your Email',
        })