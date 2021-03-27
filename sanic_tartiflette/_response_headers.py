_RESPONSE_HEADERS_VAR = None
try:
    import contextvars

    _RESPONSE_HEADERS_VAR = contextvars.ContextVar('response_headers', default={})
except ImportError:
    pass


def get_response_headers():
    if _RESPONSE_HEADERS_VAR is not None:
        return _RESPONSE_HEADERS_VAR.get()
    return {}
