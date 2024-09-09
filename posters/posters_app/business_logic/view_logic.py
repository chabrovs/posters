# Import logic function for views from this file.

from dataclasses import Field
from typing import Any
from django.db.models import F, Func, DecimalField, DateTimeField


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


class SearchEngine:
    ...