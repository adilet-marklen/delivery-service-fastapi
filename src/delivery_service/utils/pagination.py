from math import ceil
from typing import Generic, Iterable, Sequence, TypeVar

from pydantic import BaseModel

T = TypeVar("T")


class Page(BaseModel, Generic[T]):
    items: Sequence[T]
    total: int
    page: int
    size: int
    pages: int


def paginate(items: Sequence[T], *, page: int, size: int) -> Page[T]:
    start = (page - 1) * size
    end = start + size
    total = len(items)
    pages = ceil(total / size) if size else 1
    return Page(items=list(items[start:end]), total=total, page=page, size=size, pages=pages)

