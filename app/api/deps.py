"""
Dependencias comunes para endpoints de la API.

Este módulo puede contener dependencias compartidas entre endpoints,
aunque la mayoría de las dependencias de autenticación ya están
en app.core.dependencies.

Ejemplos de uso:
- Paginación común
- Rate limiting
- Validaciones comunes
- Logging de requests
"""

from typing import Optional
from fastapi import Query


def get_pagination_params(
    skip: int = Query(0, ge=0, description="Número de registros a saltar"),
    limit: int = Query(100, ge=1, le=100, description="Número máximo de registros a retornar")
) -> dict:
    """
    Dependency para parámetros de paginación comunes.

    Args:
        skip: Número de registros a saltar (offset)
        limit: Número máximo de registros a retornar

    Returns:
        Dict con skip y limit

    Example:
        @app.get("/items")
        def get_items(pagination: dict = Depends(get_pagination_params)):
            skip = pagination["skip"]
            limit = pagination["limit"]
            return get_items_from_db(skip, limit)
    """
    return {"skip": skip, "limit": limit}


def get_search_params(
    q: Optional[str] = Query(None, min_length=1, max_length=100, description="Búsqueda por texto")
) -> Optional[str]:
    """
    Dependency para parámetros de búsqueda.

    Args:
        q: Query string para búsqueda

    Returns:
        Query string sanitizado o None

    Example:
        @app.get("/search")
        def search(query: Optional[str] = Depends(get_search_params)):
            if query:
                return search_in_db(query)
            return []
    """
    if q:
        return q.strip()
    return None
