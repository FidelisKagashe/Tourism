from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Fieldset, Submit
from .models import ContactMessage, Newsletter


class ContactForm(forms.ModelForm):
    """Form for users to send contact messages."""

    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'message': forms.Textarea(attrs={'rows': 5, 'placeholder': 'Your Message'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Fieldset(
                'Send Us a Message',
                'name',
                'email',
                'subject',
                'message',
            ),
            Submit('submit', 'Send Message', css_class='btn btn-primary')
        )
        for name, field in self.fields.items():
            field.widget.attrs.update({
                'class': 'form-control',
                'placeholder': field.label
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
        self.helper.layout = Layout(
            Fieldset(
                'Subscribe to Our Newsletter',
                'name',
                'email',
            ),
            Submit('subscribe', 'Subscribe', css_class='btn btn-secondary')
        )
        self.fields['name'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Your Name (optional)'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Your Email'
        })
