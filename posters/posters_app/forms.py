from django import forms
from django.forms import inlineformset_factory
from .models import Poster, PosterImages

class CreatePosterForm(forms.ModelForm):
    class Meta:
        model = Poster
        fields = ['header', 'description', 'phone_number', 'email', 'category', 'price', 'currency']

PosterImageFormSet = inlineformset_factory(
    Poster, PosterImages,
    fields=('image_path', ),
    #BUG: When extra variable is set and multiple forms managed by JS are used. Forms upload only one picture.
    # extra=1, # Num of forms to display #NOTE: (disable when use multiple forms manages by JS).
    can_delete=True # Allow users delete images.
)