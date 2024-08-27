from typing import Any
from django.db.models.query import QuerySet
from django.shortcuts import render
from django.http import FileResponse, Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView, CreateView, ListView
from .models import Poster, PosterImages, User, PosterCategories
from django.contrib.postgres.aggregates import ArrayAgg
from .business_logic.view_logic import FormatTimestamp, RoundDecimal, F
from django.urls import reverse, reverse_lazy
from .forms import CreatePosterForm, PosterImageFormSet, EditPosterForm, EditPosterImageFormSet
from django.core.cache import cache
from django.views.decorators.cache import never_cache
# Create your views here.


class HomePageView(TemplateView):
    template_name = 'posters_app/index.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        #TODO: Make AJAX request support for fetching data.
        context = super().get_context_data(**kwargs)
        recommended_posters = Poster.objects.annotate(
        image_ids=ArrayAgg('porter_images__id'), 
        formatted_created=FormatTimestamp('created', format_style='YYYY-MM-DD HH24:MI'),
        price_rounded=RoundDecimal('price', decimal_places=2)
        )
        context['recommended_posters'] = recommended_posters
        context["images"] = PosterImages.objects.all()
        return context 
    

class PosterCategoriesView(TemplateView):
    template_name = 'posters_app/categories.html'
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        categories = PosterCategories.objects.all()
        context['categories'] = categories
        return context 


class CategoryView(ListView):
    """View all posters in category <int:category_id>"""

    template_name = 'posters_app/category.html'
    context_object_name = 'posters'
    def get_queryset(self) -> QuerySet[Any]:
        category_name = self.kwargs.get('category_name')
        return Poster.objects.filter(category__name=category_name)

class PosterView(TemplateView):
    template_name = 'posters_app/poster.html'
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        poster_id = kwargs.get('poster_id')
        poster = Poster.objects.filter(id=poster_id, status=True).annotate(
            image_ids=ArrayAgg('porter_images__id'), 
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
            image_ids=ArrayAgg('porter_images__id'), 
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

            for image_form in formset:
                # Only save forms that have data (i.e., an image was uploaded)
                if image_form.cleaned_data:
                    # Create an instance but don't save to the database yet
                    image = image_form.save(commit=False)
                    # Assign the poster instance to the image
                    image.poster_id = poster
                    # Now save the image instance to the database
                    image.save()
                else:
                    print(f'[DEBUG]: Default images were saved ')
                    image = PosterImages.objects.create(poster_id=poster)
                    image.save()

            return redirect(success_url)
        else:
            print(f'[DEBUG] FORMSET ERRORS: {formset.errors}')
            print(f'[DEBUG] FORM ERRORS: {form.errors}')
    else:
        form = CreatePosterForm()
        formset = PosterImageFormSet()    

    return render(request, 'posters_app/create_poster.html', {'form': form, 'formset': formset})

#NOTE: Not implemented (25.28.24) <devbackend_24_08_views>'\
# Login required.

@never_cache
def delete_poster_by_id(request, poster_id: int):
    poster = get_object_or_404(Poster, id=poster_id)
    if poster.owner != User.objects.get(username='sergei'):
        return HttpResponse(f"Not your poster")
    poster_images = PosterImages.objects.filter(poster_id=poster_id)

    for poster_image in poster_images:
        poster_image.delete()

    poster.delete()
    # cache.clear()
    return redirect('posters_app:home')


#NOTE: Only owner can edit its post.
def edit_poster(request, poster_id: int):
    poster = get_object_or_404(Poster, id=poster_id)
    success_url = reverse('posters_app:poster_view', args=(poster_id,))
    if request.method == 'POST':
        form = EditPosterForm(request.POST, instance=poster)
        # formset = EditPosterImageFormSet(request.POST, request.FILES, 
        # queryset=PosterImages.objects.filter(poster_id=poster_id))

        # NOTE: If an Image id is not found in the formset,\ 
        # you can pass this id using ` name="image_id" value={{ image.instance.pk }}` in HTML post request. As long as, \
        # each picture has its owen PrimaryKey avail inside of the HTML via DTL. Therefore, you can just fetch \
        # the image_id from that post form. `request.POST.get(image_id)`.

        #TODO: Implement Poster Images editing.
        if form.is_valid() and form.has_changed():
            form.save()

            return redirect(success_url)
        else:
            # print(f'[DEBUG] FORMSET ERRORS: {formset.errors}')
            print(f'[DEBUG] FORM ERRORS: {form.errors}')
    else:
        form = EditPosterForm(instance=poster)

    return render(request, 'posters_app/edit_poster.html', {'form': form})


def get_image_by_image_id(request, image_id: int | None):
    try:
        image = get_object_or_404(PosterImages, id=image_id)
        image_path = image.image_path.path
        return FileResponse(open(image_path, 'rb'))
    except PosterImages.DoesNotExist:
        return Http404("Image does not exist!")
    except Exception as e:
        raise Http404(f"Error loading Image {str(e)}")
    

def get_image_by_image_path(request, image_path):
    try:
        image = get_object_or_404(PosterImages, image_path=image_path)
        file_path = image.image_path.path
        return FileResponse(open(file_path, 'rb'))
    except PosterImages.DoesNotExist:
        return Http404("Image does not exist!")
    except Exception as e:
        raise Http404(f"Error loading Image {str(e)}")
