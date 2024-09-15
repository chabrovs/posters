from typing_extensions import Any, Generator
from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404, redirect, render, HttpResponse
from django.views.generic import TemplateView, ListView

from django.urls import reverse
from django.core.cache import cache
from django.views.decorators.cache import never_cache, cache_control
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator, Page
from django.core.cache import cache
from django.utils.translation import gettext as _

from .models import Poster, PosterImages
from .forms import CreatePosterForm, PosterImageFormSet, EditPosterForm, SearchForm, EditPosterImageFormSet
from .business_logic.view_logic import FrequentQueries, SearchQueryEngine
from .business_logic.process_images_logic import (
    get_image_by_image_id_response,
    get_image_by_image_path_response,
    process_formset_with_images_for_model)
# CACHE VARIABLES
from .constants import (
    RECOMMENDED_POSTERS_CACHE_KEY,
    CATEGORIES_CACHE_KEY
)


class HomePageView(TemplateView):
    template_name = 'posters_app/index.html'

    def __init__(self, **kwargs: Any) -> None:
        self.recommended_posters = FrequentQueries.get_recommended_posters(
            cache_timeout=60 * 3
        )
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

    def smart_pagination(self, page_number: int, chunk_size: int, search: QuerySet | None) -> Page:
        """
        Paginate home page with the default QuerySet, when search is used, paginate the
        filtered default QuerySey (search results).
        :Param page_number: Chosen page number (required for pagination).
        :Param chuck_size: Number of items per page (required for pagination).
        :Param search: A QuerySet of keywords (required for searching (filtering)). 
        """
        if search:
            search_result = SearchQueryEngine.apply_search_filter(self.recommended_posters, search)
            return self.get_page(search_result, chunk_size, page_number)

        return self.get_page(self.recommended_posters, chunk_size, page_number)

    def chucked(self, queryset: QuerySet, chuck_size: int) -> Generator[QuerySet]:
        for i in range(0, len(queryset), chuck_size):
            yield queryset[i:i + chuck_size]

    def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
        context = super().get_context_data(**kwargs)
        context['recommended_posters_row'] = self.chucked(
            self.recommended_posters, 3)
        context['page_obj'] = self.smart_pagination(
            self.request.GET.get('page'), 9,
            self.request.GET.get('query')
        )
        context['form'] = SearchForm()

        return context


class PosterCategoriesView(TemplateView):
    template_name = 'posters_app/categories.html'

    def get_queryset(self):
        # Cache
        # NOTE: Invalidate when a new category or poster is created.
        return FrequentQueries.get_poster_categories_w_count()

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
        #NOTE: DO not use cache or write validation for it.
        queryset = FrequentQueries.get_posters_in_category(category_name=category_name, cache_enabled=False)
        # Apply search filter if a search query is present
        search_query = self.request.GET.get('query')
        return SearchQueryEngine.apply_search_filter(queryset, search_query)


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
        poster = FrequentQueries.get_active_poster(
            poster_id=poster_id,
            cache_enabled=False
        )
        context['poster'] = poster
        context['user'] = self.request.user
        return context


# NOTE: Not implemented (25.28.24) <devbackend_24_08_views>\
# Login required.
class UserPostersView(TemplateView):
    template_name = 'posters_app/user_posters.html'

    # def get_context_data(self, **kwargs: Any) -> dict[str, Any]:
    #     context = super().get_context_data(**kwargs)
    #     poster_id = kwargs.get('poster_id')
    #     user_id = kwargs.get('user_id')
    #     user_poster = Poster.objects.filter(id=poster_id, status=True, user_id=user_id).annotate(
    #         image_ids=ArrayAgg('poster_images__id'),
    #         formatted_created=FormatTimestamp(
    #             'created', format_style='YYYY-MM-DD HH24:MI'),
    #         price_rounded=RoundDecimal('price', decimal_places=2),
    #         category_name=F('category__name')
    #     )
    #     context['user_posters'] = user_poster
    #     return context


@login_required
def create_poster(request):
    success_url = reverse('posters_app:home')
    if request.method == "POST":
        form = CreatePosterForm(request.POST)
        formset = PosterImageFormSet(request.POST, request.FILES)
        if form.is_valid() and formset.is_valid():
            poster = form.save(commit=False)
            poster.owner = request.user
            poster.save()

            process_formset_with_images_for_model(
                formset=formset,
                instance=poster,
                related_field='poster_images',
                image_model=PosterImages
            )

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
        return HttpResponse("Cannot edit someone else's poster!")

    if request.method == 'POST':
        form = EditPosterForm(request.POST, instance=poster)
        formset = EditPosterImageFormSet(
            request.POST, request.FILES, queryset=poster_images)

        if formset.total_form_count() > 10:
            formset._non_form_errors = formset.error_class(
                _['You can upload a maximum of 10 images.'])

        if form.is_valid() and formset.is_valid():
            form.save()

            process_formset_with_images_for_model(
                formset=formset,
                instance=poster,
                related_field='poster_images',
                image_model=PosterImages
            )

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
    return get_image_by_image_id_response(image_id)


def get_image_by_image_path(request, image_path):
    return get_image_by_image_path_response(image_path)
