import json
from functools import partial, update_wrapper

from sanic import response

from ._response_headers import get_response_headers


def format_error(err):
    formatted_error = {'type': 'internal_error', 'message': 'Server internal'}

    if isinstance(err, Exception):
        formatted_error['message'] = str(err)

    return formatted_error


def format_errors(errors):
    formatted_errors = []
    for error in errors:
        formatted_errors.append(format_error(error))

    return formatted_errors


def prepare_response(_req, data, _ctx):
    headers = get_response_headers()
    return response.json(data, headers=headers, dumps=json.dumps)


def wrapped_partial(func, *args, **kwargs):
    partial_func = partial(func, *args, **kwargs)
    update_wrapper(partial_func, func)
    return partial_func
