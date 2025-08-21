from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column, Submit, HTML
from .models import Review, ReviewImage


class ReviewForm(forms.ModelForm):
    """Form for creating reviews (Tailwind + dark mode styling)."""

    class Meta:
        model = Review
        fields = [
            'title', 'content', 'rating', 'value_for_money', 'service_quality',
            'cleanliness', 'travel_date', 'travel_type'
        ]
        widgets = {
            'content': forms.Textarea(attrs={'rows': 5}),
            'travel_date': forms.DateInput(attrs={'type': 'date'}),
            # rating/select widgets remain as Select but classes will be applied in __init__
            'rating': forms.Select(choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)]),
            'value_for_money': forms.Select(choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)]),
            'service_quality': forms.Select(choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)]),
            'cleanliness': forms.Select(choices=[(i, f'{i} Star{"s" if i != 1 else ""}') for i in range(1, 6)]),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # Tailwind class tokens (dark-mode aware) — kept from your original
        COMMON_INPUT_CLASSES = (
            'w-full px-4 py-2 border rounded-md focus:outline-none focus:ring-2 '
            'focus:ring-[#C18D45] bg-white text-gray-800 placeholder-gray-500 border-gray-300 '
            'dark:bg-gray-700 dark:text-gray-200 dark:placeholder-gray-400 dark:border-gray-600'
        )
        COMMON_TEXTAREA_CLASSES = COMMON_INPUT_CLASSES + ' h-28'
        COMMON_SELECT_CLASSES = COMMON_INPUT_CLASSES
        SUBMIT_CLASSES = (
            'w-full md:w-auto bg-[#C18D45] hover:bg-[#a6783a] text-white font-medium py-2 px-4 rounded-md '
            'transition-colors'
        )

        # Error classes to append when a field has server-side validation errors
        ERROR_CLASSES = ' border-red-500 ring-1 ring-red-500 dark:border-red-400 dark:ring-red-400'

        # Layout using crispy with Tailwind-friendly classes for columns (kept same structure you used)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'title',
            'content',
            HTML('<h6 class="mb-3 text-gray-800 dark:text-gray-100">Ratings</h6>'),
            Row(
                Column('rating', css_class='w-full md:w-1/2 px-2 mb-3'),
                Column('value_for_money', css_class='w-full md:w-1/2 px-2 mb-3'),
            ),
            Row(
                Column('service_quality', css_class='w-full md:w-1/2 px-2 mb-3'),
                Column('cleanliness', css_class='w-full md:w-1/2 px-2 mb-3'),
            ),
            HTML('<h6 class="mb-3 text-gray-800 dark:text-gray-100">Travel Information</h6>'),
            Row(
                Column('travel_date', css_class='w-full md:w-1/2 px-2 mb-3'),
                Column('travel_type', css_class='w-full md:w-1/2 px-2 mb-3'),
            ),
            Submit('submit', 'Submit Review', css_class=SUBMIT_CLASSES)
        )

        # Apply Tailwind classes to widgets (keeps choices and widget types intact)
        for field_name, field in self.fields.items():
            widget = field.widget

            if isinstance(widget, forms.Textarea):
                classes = COMMON_TEXTAREA_CLASSES
                widget.attrs.update({'class': classes, 'placeholder': field.label})
            elif isinstance(widget, forms.Select):
                classes = COMMON_SELECT_CLASSES
                widget.attrs.update({'class': classes})
            else:
                classes = COMMON_INPUT_CLASSES
                widget.attrs.update({'class': classes, 'placeholder': field.label})

            # If the form is bound (submitted) and this field has errors -> append error classes
            if self.is_bound and field_name in self.errors:
                # append error classes (preserve existing)
                widget.attrs['class'] = widget.attrs.get('class', '') + ERROR_CLASSES
                widget.attrs['aria-invalid'] = 'true'
            else:
                widget.attrs['aria-invalid'] = 'false'

        # Make some fields optional (unchanged)
        self.fields['value_for_money'].required = False
        self.fields['service_quality'].required = False
        self.fields['cleanliness'].required = False
        self.fields['travel_date'].required = False
        self.fields['travel_type'].required = False
