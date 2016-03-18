import logging


def verify_json_response_or_raise_value_error(response):
    try:
        _ = response.json()
    except ValueError:
        message = (
            'Request url: {url}\n'
            'Request authorization headers: {headers}\n'
            'Response status code: {status_code}\n'
            'Response content: {content}'
        ).format(
            url=response.url,
            headers=response.headers.get('Authorization'),
            status_code=response.status_code,
            content=response.content
        )
        logging.error(message)
        raise
