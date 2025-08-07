from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML
from .models import Review, ReviewImage

class ReviewForm(forms.ModelForm):
    """Form for creating reviews."""
    
    class Meta:
        model = Review
        fields = [
            'title', 'content', 'rating', 'value_for_money', 'service_quality',
            'cleanliness', 'travel_date', 'travel_type'
        ]
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
            'travel_date': forms.DateInput(attrs={'type': 'date'}),
            'rating': forms.Select(choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)]),
            'value_for_money': forms.Select(choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)]),
            'service_quality': forms.Select(choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)]),
            'cleanliness': forms.Select(choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)]),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'title',
            'content',
            HTML('<h6 class="mb-3">Ratings</h6>'),
            Row(
                Column('rating', css_class='form-group col-md-6 mb-3'),
                Column('value_for_money', css_class='form-group col-md-6 mb-3'),
            ),
            Row(
                Column('service_quality', css_class='form-group col-md-6 mb-3'),
                Column('cleanliness', css_class='form-group col-md-6 mb-3'),
            ),
            HTML('<h6 class="mb-3">Travel Information</h6>'),
            Row(
                Column('travel_date', css_class='form-group col-md-6 mb-3'),
                Column('travel_type', css_class='form-group col-md-6 mb-3'),
            ),
            Submit('submit', 'Submit Review', css_class='btn btn-primary')
        )
        
        # Add Bootstrap classes
        for field_name, field in self.fields.items():
            field.widget.attrs.update({'class': 'form-control'})
        
        # Make some fields optional
        self.fields['value_for_money'].required = False
        self.fields['service_quality'].required = False
        self.fields['cleanliness'].required = False
        self.fields['travel_date'].required = False
        self.fields['travel_type'].required = False