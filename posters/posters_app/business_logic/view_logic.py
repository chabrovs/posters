# Import logic function for views from this file.

from dataclasses import Field
from typing import Any
from django.db.models import F, Func, DecimalField, DateTimeField, Q, Count
from django.db.models.query import QuerySet
from django.core.cache import cache
from ..models import Poster, PosterCategories
from django.contrib.postgres.aggregates import ArrayAgg
from ..constants import (
    CATEGORIES_CACHE_KEY,
    RECOMMENDED_POSTERS_CACHE_KEY,
    POSTER_VIEW_CACHE_KEY,
    POSTERS_IN_CAT_QUERY_CACHE_KEY
)


class FormatTimestamp(Func):
    function = 'TO_CHAR'

    def __init__(self, *expressions: Any, format_style: str = 'YYYY-MM-DD HH24:MI:SS', output_field: Field[Any] | str | None = None, **extra: Any) -> None:
        if output_field is None:
            output_field = DateTimeField()
        super().__init__(*expressions, output_field=output_field, **extra)
        self.template = f"%(function)s(%(expressions)s, '{format_style}')"


class RoundDecimal(Func):
    function = 'ROUND'

    def __init__(self, *expressions: Any, decimal_places: int = 2, output_field: Field[Any] | str | None = None,  **extra: Any) -> None:
        if output_field is None:
            output_field = DecimalField()
        super().__init__(*expressions, output_field=output_field, **extra)
        self.template = f"%(function)s(%(expressions)s, {decimal_places})"


class SearchQueryEngine:
    def apply_search_filter(queryset: QuerySet, query: str | None) -> QuerySet:
        """
        Filter posters by search query (if provided).
        :Param queryset: A queryset filters are applied on.
        :Param query: A string containing words that are used as filter for the queryset param.
        """
        if query:
            return queryset.filter(
                Q(header__icontains=query) | Q(description__icontains=query)
            )
        return queryset


class FrequentQueries:
    """
    This class is a placeholder for app frequent ORM queries across the posters_app.
    The CACHE validation is NOT automated (manually validate cache!).
    """

    def get_recommended_posters(cache_enabled: bool = True, cache_timeout: int = 60) -> QuerySet:
        """
        Get a Queryset with recommended posters. This method supports cache.
        :Param cache_enabled: Enable caching for ORM query.
        :Param cache_timeout: Set cache timeout for the query. Default 60 seconds.
        """

        def fetch_posters() -> QuerySet:
            """Helper function to fetch recommended posters."""
            return Poster.objects.annotate(
                image_ids=ArrayAgg('poster_images__id'),
                formatted_created=FormatTimestamp(
                    'created', format_style='YYYY-MM-DD HH24:MI'),
                price_rounded=RoundDecimal('price', decimal_places=2)
            )

        if not cache_enabled:
            return fetch_posters()

        posters = cache.get(RECOMMENDED_POSTERS_CACHE_KEY)

        if not posters:
            posters = fetch_posters()
            # Set cache as RECOMMENDED_POSTERS_CACHE_KEY
            cache.set(RECOMMENDED_POSTERS_CACHE_KEY,
                      posters, timeout=cache_timeout)

        return posters

    def get_active_poster(poster_id: int, cache_enabled: bool = True, cache_timeout: int = 60) -> QuerySet:
        """
        Active poster. User in posters_app:poster_view.
        :Param cache_enabled: Enable caching for ORM query.
        :Param cache_timeout: Set cache timeout for the query. Default 60 seconds.
        """

        def fetch_poster(poster_id=poster_id) -> QuerySet:
            return Poster.objects.filter(id=poster_id, status=True).annotate(
                image_ids=ArrayAgg('poster_images__id'),
                formatted_created=FormatTimestamp(
                    'created', format_style='YYYY-MM-DD HH24:MI'),
                price_rounded=RoundDecimal('price', decimal_places=2),
                category_name=F('category__name')
            ).first()

        if not cache_enabled:
            return fetch_poster(poster_id)

        poster = cache.get(POSTER_VIEW_CACHE_KEY)

        if not poster:
            poster = fetch_poster(poster_id)
            # Cache poster as POSTER_VIEW_CACHE_KEY
            cache.set(POSTER_VIEW_CACHE_KEY, poster, timeout=cache_timeout)

        return poster

    def get_posters_in_category(category_name: str, cache_enabled: bool = True, cache_timeout: int = 60) -> QuerySet:
        """
        Retrieve a Queryset of posters filtered by category.
        :Param cache_enabled: Enable caching for ORM query.
        :Param cache_timeout: Set cache timeout for the query. Default 60 seconds.
        """

        def fetch(category_name=category_name) -> QuerySet:
            return Poster.objects.filter(category__name=category_name).annotate(
                image_ids=ArrayAgg('poster_images__id'),
                formatted_created=FormatTimestamp(
                    'created', format_style='YYYY-MM-DD HH24:MI'),
                price_rounded=RoundDecimal('price', decimal_places=2)
            )
        
        if not cache_enabled:
            return fetch(category_name)
        
        queryset = cache.get(POSTERS_IN_CAT_QUERY_CACHE_KEY)

        if not queryset:
            queryset = fetch(category_name)
            cache.set(POSTERS_IN_CAT_QUERY_CACHE_KEY, queryset, cache_timeout)
        
        return queryset
    
    def get_poster_categories_w_count(cache_enabled: bool = True, cache_timeout: int = 60) -> QuerySet:
        """
        Retrieve categories and count number of posters in each category.
        :Param cache_enabled: Enable caching for ORM query.
        :Param cache_timeout: Set cache timeout for the query. Default 60 seconds.
        """

        def fetch() -> QuerySet:
            return PosterCategories.objects.annotate(
                posters_in_category=(Count('poster')))
        
        if not cache_enabled:
            return fetch()
        
        query = cache.get(CATEGORIES_CACHE_KEY)

        if not query:
            query = fetch()
            cache.set(CATEGORIES_CACHE_KEY, query, timeout=cache_timeout)
        
        return query


    @classmethod
    def list_available_queries(cls) -> None:
        """
        Prints all available query methods in the class.
        """
        query_methods = [method for method in dir(cls) if callable(
            getattr(cls, method)) and not method.startswith("__")]
        print(f"Available query methods in {cls.__name__}:")
        for method in query_methods:
            print(f" - {method}")
