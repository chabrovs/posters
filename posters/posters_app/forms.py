from django import forms
from django.forms import inlineformset_factory, modelformset_factory
from .models import Poster, PosterImages


class CreatePosterForm(forms.ModelForm):
    class Meta:
        model = Poster
        fields = ['header', 'description', 'phone_number',
                  'email', 'category', 'price', 'currency']


# Creating a poster add images.
PosterImageFormSet = inlineformset_factory(
    Poster, PosterImages,
    fields=('image_path', ),
    # BUG: When extra variable is set and multiple forms managed by JS are used. Forms upload only one picture.
    # extra=1, # Num of forms to display #NOTE: (disable when use multiple forms manages by JS).
    can_delete=True  # Allow users delete images.
)


class PosterImageForm(forms.ModelForm):
    class Meta:
        model = PosterImages
        fields = ['image_path']


EditPosterImageFormSet = modelformset_factory(
    PosterImages,
    form=PosterImageForm,
    extra=0,  # Number of empty forms to display for new images
    can_delete=True  # This allows users to delete images
)


class EditPosterForm(forms.ModelForm):
    class Meta:
        model = Poster
        fields = ['header', 'description', 'phone_number',
                  'email', 'category', 'price', 'currency']


class SearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=255)
