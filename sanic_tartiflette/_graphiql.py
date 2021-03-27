import os
from string import Template
from typing import Any, Dict

from sanic import response

try:
    _TTFTT_BASE_DIR = os.path.dirname(__file__)

    with open(os.path.join(_TTFTT_BASE_DIR, 'templates/graphiql.html')) as template_file:
        _GRAPHQL_TEMPLATE = template_file.read()
except Exception:
    _GRAPHQL_TEMPLATE = ''


async def graphiql_handler(request, graphiql_options: Dict[str, Any]):
    return response.html(
        body=_render_graphiql(graphiql_options),
        headers={'Content-Type': 'text/html'},
    )


def _render_graphiql(graphiql_options: Dict[str, Any]) -> str:
    return Template(_GRAPHQL_TEMPLATE).substitute(
        endpoint=graphiql_options['endpoint'],
        http_method=graphiql_options['http_method'],
        default_query=graphiql_options['query'],
        default_variables=graphiql_options['variables'],
        default_headers=graphiql_options['headers'],
    )
