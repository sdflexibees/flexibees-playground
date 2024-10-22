from rest_framework.response import Response


class ResponseFormatMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if isinstance(response, Response):
            try:
                data = response.data.copy()
                response.data.clear()
                response.data = dict(response.data)
                response.data['data'] = data
                response.data['status_code'] = response.status_code
                # you need to change private attribute `_is_render`
                # to call render second time
                response._is_rendered = False
                response.render()
            except:
                pass
        return response


def message_response(message):
    return {
        'message': message
    }

