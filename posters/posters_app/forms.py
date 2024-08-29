from django import forms
from django.forms import inlineformset_factory, modelformset_factory
from .models import Poster, PosterImages

class CreatePosterForm(forms.ModelForm):
    #BUG: price requires 9 digits in total and 4 digits before point ???
    class Meta:
        model = Poster
        fields = ['header', 'description', 'phone_number', 'email', 'category', 'price', 'currency']


class PosterImagesForm(forms.ModelForm):
    class Meta:
        fields = ['id', 'image_path',]


PosterImageFormSet = inlineformset_factory(
    Poster, PosterImages,
    fields=('image_path', ),
    #BUG: When extra variable is set and multiple forms managed by JS are used. Forms upload only one picture.
    # extra=1, # Num of forms to display #NOTE: (disable when use multiple forms manages by JS).
    can_delete=True # Allow users delete images.
)

# EditPosterImageFormSet = inlineformset_factory(
#     Poster,  # Parent model
#     PosterImages,  # Child model
#     # form=PosterImagesForm,  # Form to use for the child model
#     fields=('id', 'image_path'),  # Fields to include in the form
#     can_delete=True,  # Allow users to delete images
#     extra=0
# )
EditPosterImageFormSet = modelformset_factory(
    PosterImages,
    form = PosterImagesForm,
    extra = 0, # Show only existing images by default
    can_delete=True
)

class EditPosterForm(forms.ModelForm):
    class Meta:
        model = Poster
        fields = ['header', 'description', 'phone_number', 'email', 'category', 'price', 'currency']


class SearchForm(forms.Form):
    query = forms.CharField(label='Search', max_length=255)