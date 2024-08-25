from typing import Any
from django.shortcuts import render
from django.http import FileResponse, Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView, CreateView
from .models import Poster, PosterImages, User
from django.contrib.postgres.aggregates import ArrayAgg
from .business_logic.view_logic import FormatTimestamp, RoundDecimal, F
from django.urls import reverse, reverse_lazy
from .forms import CreatePosterForm, PosterImageFormSet
# Create your views here.


class HomePageView(TemplateView):
    template_name = 'posters_app/index.html'
    extra_context = {
        "recommended_posters": Poster.objects.annotate(
            image_paths=ArrayAgg('porter_images__image_path'), 
            formatted_created=FormatTimestamp('created', format_style='YYYY-MM-DD HH24:MI'),
            price_rounded=RoundDecimal('price', decimal_places=2)
            ), 
        "images": PosterImages.objects.all(),
    }
    

class PosterView(TemplateView):
    template_name = 'posters_app/poster.html'
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        poster_id = kwargs.get('poster_id')
        poster = Poster.objects.filter(id=poster_id, status=True).annotate(
            image_paths=ArrayAgg('porter_images__id'), 
            formatted_created=FormatTimestamp('created', format_style='YYYY-MM-DD HH24:MI'),
            price_rounded=RoundDecimal('price', decimal_places=2),
            category_name=F('category__name')
            ).first()
        context['poster'] = poster
        return context 
    

#NOTE: Not implemented (25.28.24) <devbackend_24_08_views>\
# Login required.
class UserPostersView(TemplateView):
    template_name = 'posters_app/user_posters.html'
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        poster_id = kwargs.get('poster_id')
        user_id = kwargs.get('user_id')
        user_poster = Poster.objects.filter(id=poster_id, status=True, user_id=user_id).annotate(
            image_paths=ArrayAgg('porter_images__id'), 
            formatted_created=FormatTimestamp('created', format_style='YYYY-MM-DD HH24:MI'),
            price_rounded=RoundDecimal('price', decimal_places=2),
            category_name=F('category__name')
            )
        context['user_posters'] = user_poster
        return context 


#NOTE: Not implemented (25.28.24) <devbackend_24_08_views>'\
# Login required.
def create_poster(request):
    success_url = reverse('posters_app:home')
    if request.method == "POST":
        form = CreatePosterForm(request.POST)
        formset = PosterImageFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            poster = form.save(commit=False)  # Do not save to the database yet
            poster.owner = request.user       # Set the owner to the currently logged-in user
            poster.save()

            # images = formset.save(commit=False)  # Get the PosterImage instances, but don't save yet
            # for image in images:
            #     image.poster_id = poster  # Associate each image with the saved Poster instance
            #     image.save() 

            for image_form in formset:
                # Only save forms that have data (i.e., an image was uploaded)
                if image_form.cleaned_data:
                    # Create an instance but don't save to the database yet
                    image = image_form.save(commit=False)
                    # Assign the poster instance to the image
                    image.poster_id = poster
                    # Now save the image instance to the database
                    image.save()

            return redirect(success_url)
        else:
            print(f'[DEBUG] FORMSET ERRORS: {formset.errors}')
    else:
        form = CreatePosterForm()
        formset = PosterImageFormSet()    

    return render(request, 'posters_app/create_poster.html', {'form': form, 'formset': formset})


#NOTE: Can replace create_poster function. If you know how this generic Class works.
# class CreatePoster(CreateView):
#
#     model = Poster
#     fields = ['header', 'description']
#     template_name = 'posters_app/create_poster.html'
#     def __init__(self, **kwargs: Any) -> None:
#         self.path = reverse('posters_app:home')
#         self.success_url = self.path
#         print(self.success_url)
#         super().__init__(**kwargs)
    

def get_image_by_image_id(request, image_id: int):
    try:
        image = PosterImages.objects.get(id=image_id)
        image_path = image.image_path.path
        return FileResponse(open(image_path, 'rb'))
    except PosterImages.DoesNotExist:
        return Http404("Image does not exist!")
    except Exception as e:
        raise Http404(f"Error loading Image {str(e)}")
    

def get_image_by_image_path(request, image_path):
    try:
        # image_path = 'poster_images/' + image_path
        image = get_object_or_404(PosterImages, image_path=image_path)
        file_path = image.image_path.path
        return FileResponse(open(file_path, 'rb'))
    except PosterImages.DoesNotExist:
        return Http404("Image does not exist!")
    except Exception as e:
        raise Http404(f"Error loading Image {str(e)}")
