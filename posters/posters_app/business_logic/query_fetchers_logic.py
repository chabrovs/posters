from dataclasses import Field
from typing_extensions import Any, Callable
from django.db.models import F, Func, DecimalField, DateTimeField, Q, Count
from django.db.models.query import QuerySet
from ..models import Poster, PosterCategories
from django.contrib.postgres.aggregates import ArrayAgg
from django.core.cache import cache


# region: SQL functions
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
# endregion


class QueryFetchers:
    """
    This class contains Django ORM query fetch methods.
    Each method in this class constructs and returns a required QuerySet.
    """

    @classmethod
    def list_available_queries(cls) -> None:
        """Prints all available query methods in the class."""
        query_methods = [method for method in dir(cls) if callable(
            getattr(cls, method)) and not method.startswith("__")]
        print(f"Available query methods in {cls.__name__}:")
        for method in query_methods:
            print(f" - {method}")

    @staticmethod
    def fetch_posters() -> QuerySet:
        """Helper function to fetch recommended posters."""
        return Poster.objects.annotate(
            image_ids=ArrayAgg('poster_images__id'),
            formatted_created=FormatTimestamp(
                'created', format_style='YYYY-MM-DD HH24:MI'),
            price_rounded=RoundDecimal('price', decimal_places=2)
        )

    @staticmethod
    def fetch_poster_by_id(poster_id) -> QuerySet:
        return Poster.objects.filter(id=poster_id, status=True).annotate(
            image_ids=ArrayAgg('poster_images__id'),
            formatted_created=FormatTimestamp(
                'created', format_style='YYYY-MM-DD HH24:MI'),
            price_rounded=RoundDecimal('price', decimal_places=2),
            category_name=F('category__name')
        ).first()

    @staticmethod
    def fetch_posters_by_category(category_name) -> QuerySet:
        """Retrieve a Queryset of posters filtered by category."""
        return Poster.objects.filter(category__name=category_name).annotate(
            image_ids=ArrayAgg('poster_images__id'),
            formatted_created=FormatTimestamp(
                'created', format_style='YYYY-MM-DD HH24:MI'),
            price_rounded=RoundDecimal('price', decimal_places=2)
        )

    @staticmethod
    def fetch_categories_and_count_posters() -> QuerySet:
        """Retrieve categories and count number of posters in each category."""
        return PosterCategories.objects.annotate(
            posters_in_category=(Count('poster')))
    
    @staticmethod
    def fetch_users_posters(user_id: int) -> QuerySet:
        """Fetch posters filtered by user id."""
        return Poster.objects.filter(owner=user_id)


def get_from_cache_or_query(
        fetch_func: Callable,
        cache_key: str | None = None,
        cache_enabled: bool = True,
        cache_timeout: int = 60) -> QuerySet:
    """
    Handles retrieving from cache or querying the database if not cached.
    :param fetch_func: Function to fetch data if cache is empty.
    :param cache_key: Cache key for the query result [default=None].
    :param cache_enabled: Whether caching is enabled or not [default=True].
    :param cache_timeout: Timeout for the cache entry (in seconds) [default=60].
    :return: QuerySet with the result of the fetch_func.
    """

    if not cache_enabled:
        return fetch_func()

    cached_data = cache.get(cache_key)

    if not cached_data:
        cached_data = fetch_func()
        cache.set(cache_key, cached_data, cache_timeout)

    return cached_data
