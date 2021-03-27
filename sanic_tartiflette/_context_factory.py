from contextlib import asynccontextmanager
from typing import Any, Dict

__all__ = ('default_context_factory',)


@asynccontextmanager
async def default_context_factory(context: Dict[str, Any], req) -> Dict[str, Any]:
    yield {**context, 'req': req}
