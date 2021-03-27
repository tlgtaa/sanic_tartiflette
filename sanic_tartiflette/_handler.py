import json
import logging
import time

from platformlib import statsd
from platformlib.exceptions import AuthenticationError

from ._exceptions import BadRequestError
from ._utils import format_errors

logger = logging.getLogger(__name__)


async def _handle_query(req, query, query_vars, operation_name, context):
    try:
        if not operation_name:
            operation_name = None
        return await req.app.engine.execute(
            query=query,
            variables=query_vars,
            context=context,
            operation_name=operation_name,
        )
    except Exception as e:  # pylint: disable=broad-except
        logger.exception(e)
        return {'data': None, 'errors': format_errors([e])}


async def _get_params(req):
    if 'query' not in req.query:
        raise BadRequestError('The mandatory "query" parameter is missing.')

    variables = None
    if 'variables' in req.query and req.query['variables'] != '':
        try:
            variables = json.loads(req.query['variables'])
        except Exception:
            message = 'The "variables" parameter is invalid. A JSON mapping is expected.'
            raise BadRequestError(message)

    return req.query['query'], variables, req.query.get('operationName')


async def _post_params(req):
    try:
        req_content = req.json
    except Exception:  # pylint: disable=broad-except
        raise BadRequestError('Body should be a JSON object')

    if 'query' not in req_content:
        raise BadRequestError('The mandatory "query" parameter is missing.')

    variables = None
    if 'variables' in req_content and req_content['variables'] != '':
        variables = req_content['variables']
        try:
            if isinstance(variables, str):
                variables = json.loads(variables)
        except Exception:
            message = 'The "variables" parameter is invalid. A JSON mapping is expected.'
            raise BadRequestError(message)

    return req_content['query'], variables, req_content.get('operationName')


class Handlers:
    @staticmethod
    async def _handle(param_func, req, context_factory):
        context_factory_mgr = context_factory(req)

        async with context_factory_mgr as context:
            try:
                qry, qry_vars, oprn_name = await param_func(req)
                start_time = time.time()
                data = await _handle_query(req, qry, qry_vars, oprn_name, context)
                complete_time = (time.time() - start_time) * 1000
                async with statsd.client() as client:
                    client.timing(f'graphql.{qry.split()[0]}.latency', value=complete_time)
            except BadRequestError as e:
                data = {'data': None, 'errors': format_errors([e])}

            return req.app.response_formatter(req, data, context)

    @staticmethod
    async def handle_get(req, context_factory):
        if not req.pfm.user:
            raise AuthenticationError

        return await Handlers._handle(_get_params, req, context_factory)

    @staticmethod
    async def handle_post(req, context_factory):
        if not req.pfm.user:
            raise AuthenticationError

        return await Handlers._handle(_post_params, req, context_factory)
