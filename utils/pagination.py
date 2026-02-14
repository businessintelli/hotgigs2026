from typing import TypeVar, Generic, List
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from schemas.common import PaginatedResponse, PaginationParams

T = TypeVar("T")


async def paginate(
    session: AsyncSession,
    query,
    skip: int = 0,
    limit: int = 20,
) -> tuple[List, int]:
    """Paginate query results.

    Args:
        session: Database session
        query: SQLAlchemy query
        skip: Number of records to skip
        limit: Number of records to return

    Returns:
        Tuple of (items, total_count)
    """
    # Get total count
    count_query = select(func.count()).select_from(query.froms[0])
    total = await session.scalar(count_query)

    # Get paginated results
    query = query.offset(skip).limit(limit)
    result = await session.execute(query)
    items = result.scalars().all()

    return items, total


def create_paginated_response(
    items: List[T],
    total: int,
    skip: int,
    limit: int,
) -> PaginatedResponse[T]:
    """Create a paginated response.

    Args:
        items: List of items
        total: Total count of items
        skip: Number of items skipped
        limit: Number of items in response

    Returns:
        PaginatedResponse object
    """
    return PaginatedResponse(
        total=total,
        skip=skip,
        limit=limit,
        items=items,
    )
