import json
from typing import Any, AsyncContextManager, Dict, List, Optional

from sanic import Sanic
from tartiflette import Engine

from ._context_factory import default_context_factory
from ._graphiql import graphiql_handler
from ._handler import Handlers
from ._utils import prepare_response, wrapped_partial


class Application(Sanic):
    def __init__(
        self,
        service_name: str,
        *,
        engine_sdl: str = None,
        engine_schema_name: str = 'default',
        executor_context: Optional[Dict[str, Any]] = None,
        executor_http_endpoint: str = '/graphql',
        executor_http_methods: List[str] = None,
        graphiql_enabled: bool = False,
        graphiql_options: Optional[Dict[str, Any]] = None,
        engine_modules=None,
        context_factory: Optional[AsyncContextManager] = None,
        response_formatter=None,
        debug=None,
        sentry_dsn=None,
    ):
        super().__init__(name=service_name)
        self.engine_sdl = engine_sdl
        self.engine_schema_name = engine_schema_name
        self.executor_http_methods = executor_http_methods or ['GET', 'POST']
        self.response_formatter = response_formatter or prepare_response
        executor_context = executor_context or {}
        executor_context['app'] = self
        self.context_factory = wrapped_partial(
            context_factory or default_context_factory,
            executor_context,
        )
        self.engine = Engine()
        self._add_listeners(engine_sdl, engine_schema_name, engine_modules)
        self._add_routes(executor_http_endpoint)
        if graphiql_enabled:
            self._set_graphiql_handler(graphiql_options, executor_http_endpoint)

    def _add_listeners(self, sdl, schema, modules):
        @self.listener('before_server_start')
        async def _cook_on_startup(app, loop):
            await app.engine.cook(
                sdl=sdl,
                schema_name=schema,
                modules=modules,
            )

    def _add_routes(self, executor_http_endpoint):
        for method in self.executor_http_methods:
            try:
                handler_func = getattr(Handlers, f'handle_{method.lower()}')
                route_handler = wrapped_partial(
                    handler_func, context_factory=self.context_factory,
                )
                self.add_route(
                    route_handler,
                    executor_http_endpoint,
                    [method],
                )
            except AttributeError:
                raise Exception(f'Unsupported <{method}> http method')

    def _set_graphiql_handler(self, options: Optional[Dict[str, Any]], executor_endpoint: str):
        if options is None:
            options = {}

        graphiql_options = {
            'endpoint': executor_endpoint,
            'query': options.get('default_query', ''),
            'variables': self._validate_and_compute_graphiql_option(
                options.get('default_variables'),
                'default_variables',
                '',
                2,
            ),
            'headers': self._validate_and_compute_graphiql_option(
                options.get('default_headers'),
                'default_headers',
                '{}',
            ),
            'http_method': 'POST' if 'POST' in self.executor_http_methods else 'GET',
        }
        handler_ = wrapped_partial(graphiql_handler, graphiql_options=graphiql_options)
        self.add_route(handler_, '/graphiql', ['GET'])

    def _validate_and_compute_graphiql_option(
        self, raw_value: Any, option_name: str, default_value: str, indent: int = 0
    ) -> str:
        if not raw_value:
            return default_value

        if not isinstance(raw_value, dict):
            raise TypeError(f'< graphiql_options.{option_name} > parameter should be a dict.')

        try:
            return json.dumps(raw_value, indent=indent)
        except Exception as e:
            raise ValueError(
                f'Unable to jsonify < graphiql_options.{option_name}> value. Error: {e}'
            )


__all__ = [
    'Application',
]
