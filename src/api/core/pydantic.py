from typing import Optional

from fastapi import Query


class List_QueryParams:
    dateRange: Optional[str] = (
        None,
    )  # JSON string like '["created_at", "01-01-2025", "01-12-2025"]'
    numberRange: Optional[str] = (None,)  # JSON string like '["amount", "0", "100000"]'
    searchTerm: str = (None,)
    columnFilters: Optional[str] = (
        Query(None),
    )  # e.g. '[["name","car"],["description","product"]]'
    page: int = (None,)
    skip: int = (0,)
    limit: int = (Query(10, ge=1, le=100),)
