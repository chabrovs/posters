from typing_extensions import Any, Generator
from django.db.models.query import QuerySet
from django.db.models import Count, Q
from django.shortcuts import render
from django.http import FileResponse, Http404, HttpRequest, HttpResponse, HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect
from django.views.generic import TemplateView, CreateView, ListView
from .models import Poster, PosterImages, User, PosterCategories
from django.contrib.postgres.aggregates import ArrayAgg
from .business_logic.view_logic import FormatTimestamp, RoundDecimal, F
from .business_logic.poster_image_name_logic import DEFAULT_IMAGE, DEFAULT_IMAGE_FULL_PATH
from django.urls import reverse, reverse_lazy
from .forms import CreatePosterForm, PosterImageFormSet, EditPosterForm, SearchForm, EditPosterImageFormSet
from django.core.cache import cache
from django.views.decorators.cache import never_cache, cache_control
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator, Page
from django.core.cache import cache
import io
from django.utils.translation import gettext as _

# Create your views here.
# CACHE VARIABLES
RECOMMENDED_POSTERS_CACHE_KEY = 'recommended_posters_cached'
CATEGORIES_CACHE_KEY = 'categories_cached'


class HomePageView(TemplateView):
    template_name = 'posters_app/index.html'

    def __init__(self, **kwargs: Any) -> None:

        # Cache
        self.recommended_posters = cache.get(RECOMMENDED_POSTERS_CACHE_KEY)

        if not self.recommended_posters:
            self.recommended_posters = self.recommended_posters = Poster.objects.annotate(
                image_ids=ArrayAgg('porter_images__id'),
                formatted_created=FormatTimestamp(
                    'created', format_style='YYYY-MM-DD HH24:MI'),
                price_rounded=RoundDecimal('price', decimal_places=2)
            )
            cache.set(RECOMMENDED_POSTERS_CACHE_KEY,
                      self.recommended_posters, timeout=60*3)

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
        # TODO: Make AJAX request support for fetching data. Update: might be not needed.
        context = super().get_context_data(**kwargs)
        context['recommended_posters_row'] = self.chucked(
            self.recommended_posters, 3)
        context['page_obj'] = self.smart_pagination(
            self.request.GET.get('page'), 9, self.request.GET.get('query'))
        # context['page_obj'] = self.get_page(self.recommended_posters, 9, self.request.GET.get('page'))
        # context['search_results'] = self.get_page(
        #     self.get_search_results(self.request.GET.get('query')), 9, self.request.GET.get('page')
        # )
        context['form'] = SearchForm()

        return context


class PosterCategoriesView(TemplateView):
    template_name = 'posters_app/categories.html'

    def get_queryset(self):
        # Cache
        # NOTE: Invalidate when a new category or poster is created.
        categories = cache.get(CATEGORIES_CACHE_KEY)

        if not categories:
            categories = PosterCategories.objects.annotate(
                posters_in_category=(Count('poster'))
            )
            cache.set(CATEGORIES_CACHE_KEY, categories, 30)

        return categories

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['categories'] = self.get_queryset()
        return context


class CategoryView(ListView):
    """View all posters in category <str:category_name> with optional search."""

    template_name = 'posters_app/category.html'
    context_object_name = 'posters'
    model = Poster
    paginate_by = 10

    def get_queryset(self) -> QuerySet[Any]:
        """Retrieve posters by category, with optional search filtering."""

        category_name = self.kwargs.get('category_name')
        queryset = Poster.objects.filter(category__name=category_name).annotate(
            image_ids=ArrayAgg('porter_images__id'),
            formatted_created=FormatTimestamp(
                'created', format_style='YYYY-MM-DD HH24:MI'),
            price_rounded=RoundDecimal('price', decimal_places=2)
        )

        # Apply search filter if a search query is present
        search_query = self.request.GET.get('query')
        return self.apply_search_filter(queryset, search_query)

    def apply_search_filter(self, queryset: QuerySet, query: str | None) -> QuerySet:
        """Filter posters by search query (if provided)."""

        if query:
            return queryset.filter(
                Q(header__icontains=query) | Q(description__icontains=query)
            )
        return queryset

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        """Add extra context data for the category and search form."""

        context = super().get_context_data(**kwargs)
        context['form'] = SearchForm()
        context['category_name'] = self.kwargs.get('category_name')
        return context


class PosterView(TemplateView):
    template_name = 'posters_app/poster.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        poster_id = kwargs.get('poster_id')
        poster = Poster.objects.filter(id=poster_id, status=True).annotate(
            image_ids=ArrayAgg('porter_images__id'),
            formatted_created=FormatTimestamp(
                'created', format_style='YYYY-MM-DD HH24:MI'),
            price_rounded=RoundDecimal('price', decimal_places=2),
            category_name=F('category__name')
        ).first()
        context['poster'] = poster
        context['user'] = self.request.user
        return context


# NOTE: Not implemented (25.28.24) <devbackend_24_08_views>\
# Login required.
class UserPostersView(TemplateView):
    template_name = 'posters_app/user_posters.html'

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        poster_id = kwargs.get('poster_id')
        user_id = kwargs.get('user_id')
        user_poster = Poster.objects.filter(id=poster_id, status=True, user_id=user_id).annotate(
            image_ids=ArrayAgg('porter_images__id'),
            formatted_created=FormatTimestamp(
                'created', format_style='YYYY-MM-DD HH24:MI'),
            price_rounded=RoundDecimal('price', decimal_places=2),
            category_name=F('category__name')
        )
        context['user_posters'] = user_poster
        return context


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
                    image = PosterImages.objects.create(poster_id=poster)
                    image.save()

            # Cache validation
            cache.delete(RECOMMENDED_POSTERS_CACHE_KEY)
            cache.delete(CATEGORIES_CACHE_KEY)

            return redirect(success_url)
        else:
            print(f'[DEBUG] FORMSET ERRORS: {formset.errors}')
            print(f'[DEBUG] FORM ERRORS: {form.errors}')
    else:
        form = CreatePosterForm()
        formset = PosterImageFormSet()

    return render(request, 'posters_app/create_poster.html', {'form': form, 'formset': formset})


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
    # Cache validation
    cache.delete(RECOMMENDED_POSTERS_CACHE_KEY)
    cache.delete(CATEGORIES_CACHE_KEY)

    return redirect('posters_app:home')


# NOTE: Only owner can edit its post.
@login_required
def edit_poster(request, poster_id: int):
    success_url = reverse('posters_app:poster_view', args=(poster_id,))
    poster = get_object_or_404(Poster, id=poster_id)
    poster_images = PosterImages.objects.filter(poster_id=poster)

    if poster.owner != request.user:
        return HttpResponse("Cannot edit someone elses poster!")

    if request.method == 'POST':
        form = EditPosterForm(request.POST, instance=poster)
        formset = EditPosterImageFormSet(
            request.POST, request.FILES, queryset=poster_images)

        if formset.total_form_count() > 10:
            formset._non_form_errors = formset.error_class(
                _['You can upload a maximum of 10 images.'])

        if form.is_valid() and formset.is_valid():
            form.save()
            images = formset.save(commit=False)
            for image in images:
                image.poster_id = poster
                image.save()

            # Cache validation
            cache.delete(RECOMMENDED_POSTERS_CACHE_KEY)

            # In case user deletes all images, upload the default one.
            if not poster.porter_images.exists():
                PosterImages.objects.create(
                    poster_id=poster, image_path=DEFAULT_IMAGE_FULL_PATH)

            return redirect(success_url)
        else:
            print(f'[DEBUG] FORMSET ERRORS: {formset.errors}')
            print(f'[DEBUG] FORM ERRORS: {form.errors}')
    else:
        form = EditPosterForm(instance=poster)
        formset = EditPosterImageFormSet(queryset=poster_images)

    return render(request, 'posters_app/edit_poster.html', {'form': form, 'formset': formset})


@cache_control(max_age=15)
def get_image_by_image_id(request, image_id: int | None):
    try:
        if image_id is None:
            image_path = DEFAULT_IMAGE
        else:
            image = get_object_or_404(PosterImages, id=image_id)
            image_path = image.image_path.path
        image_file_cache_key = f'image_by_id={image_path}'

        # Caching
        image_file_data = cache.get(image_file_cache_key)
        if not image_file_data:
            with open(image_path, 'rb') as image_file:
                image_file_data = image_file.read()
            cache.set(image_file_cache_key, image_file_data, 60*3)

        return FileResponse(io.BytesIO(image_file_data), content_type='image/jpeg')
    except PosterImages.DoesNotExist:
        with open(DEFAULT_IMAGE_FULL_PATH, 'rb') as default_image_file:
            image_file_data = default_image_file.read()
        return FileResponse(io.BytesIO(image_file_data), content_type='image/jpeg')
    except Exception as e:
        with open(DEFAULT_IMAGE_FULL_PATH, 'rb') as default_image_file:
            image_file_data = default_image_file.read()
        return FileResponse(io.BytesIO(image_file_data), content_type='image/jpeg')
        # raise Http404(f"Error loading Image {str(e)}")


def get_image_by_image_path(request, image_path):
    try:
        image = get_object_or_404(PosterImages, image_path=image_path)
        file_path = image.image_path.path
        return FileResponse(open(file_path, 'rb'))
    except PosterImages.DoesNotExist:
        return Http404("Image does not exist!")
    except Exception as e:
        raise Http404(f"Error loading Image {str(e)}")
