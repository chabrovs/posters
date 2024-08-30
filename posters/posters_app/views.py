from typing_extensions import Any, Generator
from django.db.models.query import QuerySet
from django.db.models import Count
from django.shortcuts import render
from django.http import FileResponse, Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView, CreateView, ListView
from .models import Poster, PosterImages, User, PosterCategories
from django.contrib.postgres.aggregates import ArrayAgg
from .business_logic.view_logic import FormatTimestamp, RoundDecimal, F
from django.urls import reverse, reverse_lazy
from .forms import CreatePosterForm, PosterImageFormSet, EditPosterForm, EditPosterImageFormSet, SearchForm
from django.core.cache import cache
from django.views.decorators.cache import never_cache
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, Page
from django.core.cache import cache
import io

# Create your views here.


class HomePageView(TemplateView):
    template_name = 'posters_app/index.html'
    def __init__(self, **kwargs: Any) -> None:
        self.recommended_posters_cache_key = 'recommended_posters'

        self.recommended_posters = cache.get(self.recommended_posters_cache_key)

        if not self.recommended_posters:
            self.recommended_posters = self.recommended_posters = Poster.objects.annotate(
                image_ids=ArrayAgg('porter_images__id'), 
                formatted_created=FormatTimestamp('created', format_style='YYYY-MM-DD HH24:MI'),
                price_rounded=RoundDecimal('price', decimal_places=2)
            )
            cache.set(self.recommended_posters_cache_key, self.recommended_posters, timeout=1000)
        

        super().__init__(**kwargs)
    
    def get_page(self, queryset: QuerySet, chunk_size: int, page_number: int) -> Page:
        """
        Makes a page for displaying QuerySet elements by chunks 
        in pages using Django built-in pagination tool.
        :Param queryset: Set of posters.
        :Param chunk_size: Number of element (posters) on the page.
        :Param page number: Page number. E.g. '?page=1'.
        """
        paginator = Paginator(queryset, chunk_size)
        page_obj = paginator.get_page(page_number)

        return page_obj
    
    def get_search_results(self, queryset: QuerySet | None) -> QuerySet | None:
        """
        Search records in the `posters_app_poster` by headers.
        :Param queryset: Keyword to look for in posters headers. In URL `/?query=something`.
        """
        if not queryset:
            return None

        return self.recommended_posters.filter(header__icontains=queryset) | self.recommended_posters.filter(description__icontains=queryset)
    
    def smart_pagination(self, page_number: int, chunk_size: int, search: QuerySet | None) -> Page:
        """
        Paginate home page with the default QuerySet, when search is used, paginate the
        filtered default QuerySey (search results).
        :Param page_number: Chosen page number (required for pagination).
        :Param chuck_size: Number of items per page (required for pagination).
        :Param search: A QuerySet of keywords (required for searching (filtering)). 
        """
        if search:
            search_result = self.get_search_results(search)
            return self.get_page(search_result, chunk_size, page_number)
        
        return self.get_page(self.recommended_posters, chunk_size, page_number)

    def chucked(self, queryset: QuerySet, chuck_size: int) -> Generator[QuerySet]:
        for i in range(0, len(queryset), chuck_size):
            yield queryset[i:i + chuck_size]

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        #TODO: Make AJAX request support for fetching data. Update: might be not needed.
        context = super().get_context_data(**kwargs)
        context['recommended_posters_row'] = self.chucked(self.recommended_posters, 3)
        context['page_obj'] = self.smart_pagination(self.request.GET.get('page'), 9, self.request.GET.get('query'))
        # context['page_obj'] = self.get_page(self.recommended_posters, 9, self.request.GET.get('page'))
        # context['search_results'] = self.get_page(
        #     self.get_search_results(self.request.GET.get('query')), 9, self.request.GET.get('page')
        # ) 
        context['form'] = SearchForm()
        # context["images"] = PosterImages.objects.all()

        return context 
    

class PosterCategoriesView(TemplateView):
    template_name = 'posters_app/categories.html'
    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        categories = PosterCategories.objects.annotate(
            posters_in_category = (Count('poster'))
        )
        context['categories'] = categories
        return context 


class CategoryView(ListView):
    """View all posters in category <int:category_id>"""

    template_name = 'posters_app/category.html'
    context_object_name = 'posters'
    def get_queryset(self) -> QuerySet[Any]:
        category_name = self.kwargs.get('category_name')
        return Poster.objects.filter(category__name=category_name).annotate(
            image_ids=ArrayAgg('porter_images__id'), 
            formatted_created=FormatTimestamp('created', format_style='YYYY-MM-DD HH24:MI'),
            price_rounded=RoundDecimal('price', decimal_places=2)
        )


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
        context['user'] = self.request.user
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
@login_required
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
@login_required
def delete_poster_by_id(request, poster_id: int):
    poster = get_object_or_404(Poster, id=poster_id)

    if poster.owner != request.user:
        return HttpResponse(f"Not your poster")
    
    poster_images = PosterImages.objects.filter(poster_id=poster_id)

    for poster_image in poster_images:
        poster_image.delete()

    poster.delete()
    # cache.clear()
    return redirect('posters_app:home')


#NOTE: Only owner can edit its post.
@login_required
def edit_poster(request, poster_id: int):
    success_url = reverse('posters_app:poster_view', args=(poster_id,))
    poster = get_object_or_404(Poster, id=poster_id)

    if poster.owner != request.user:
        return HttpResponse("Cannot edit someone elses poster!")
    
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
        image_file_cache_key = f'image_by_id={image_path}'

        # Caching
        image_file_data = cache.get(image_file_cache_key)
        if not image_file_data:
            with open(image_path, 'rb') as image_file:
                image_file_data = image_file.read()
            cache.set(image_file_cache_key, image_file_data, 60)

        return FileResponse(io.BytesIO(image_file_data), content_type='image/jpeg')
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
