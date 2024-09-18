# Import logic function for views from this file.

from django.db.models import Q
from django.db.models.query import QuerySet
from .query_fetchers_logic import QueryFetchers, get_from_cache_or_query

from ..constants import (
    CATEGORIES_CACHE_KEY,
    RECOMMENDED_POSTERS_CACHE_KEY,
)


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
    This class manages frequent ORM queries with caching.
    It delegates query construction to QueryFetchers.
    """

    def get_recommended_posters() -> QuerySet:
        """Get posters for main page."""
        return get_from_cache_or_query(
            fetch_func=QueryFetchers.fetch_posters,
            cache_key=RECOMMENDED_POSTERS_CACHE_KEY,
            cache_enabled=True,
            cache_timeout=60 * 3
        )

    def get_active_poster(poster_id: int) -> QuerySet:
        """Get poster data for posters_app:view_poster."""
        return get_from_cache_or_query(
            fetch_func=lambda: QueryFetchers.fetch_poster_by_id(
                poster_id=poster_id),
            cache_enabled=False
        )

    def get_posters_in_category(category_name: str) -> QuerySet:
        """Get posters in a category by category name."""
        return get_from_cache_or_query(
            fetch_func=lambda: QueryFetchers.fetch_posters_by_category(
                category_name=category_name),
            cache_enabled=False
        )

    def get_poster_categories_w_count() -> QuerySet:
        """Get poster categories and count the number of posters in each category."""
        return get_from_cache_or_query(
            fetch_func=QueryFetchers.fetch_categories_and_count_posters,
            cache_enabled=True,
            cache_key=CATEGORIES_CACHE_KEY,
            cache_timeout=60
        )

    def get_users_posters(user_id: int) -> QuerySet:
        """Get users posters."""
        return get_from_cache_or_query(
            fetch_func=lambda: QueryFetchers.fetch_users_posters(
                user_id=user_id),
            cache_enabled=False
        )
