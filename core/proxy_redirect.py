import datetime
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from apps.admin_app.views import api_logging
from core.constants import PROXY_ERROR_MESSAGE
from core.string_constants import LINE_BREAK
from rest_framework import status
from config.settings import EMPLOYER_SERVER_URL
from core.response_format import message_response

# URL of the external server to proxy requests to

@csrf_exempt  # Exempt from CSRF verification for simplicity
def proxy_function(request):
    """
    Proxy requests to an external server.
    """
    # Construct the full URL to the external server
    url = EMPLOYER_SERVER_URL+request.path

    # Forward the request to the external server
    try:
        response = requests.request(
            method=request.method,
            url=url,
            headers={key: value for key, value in request.headers.items() if key != 'Host'},
            data=request.body,
            params=request.GET,
            cookies=request.COOKIES,
            allow_redirects=False  # Avoid handling redirects
        )
        json_data = response.json()
        
        # Check if the parsed data is a list (since lists are valid JSON but not an object)
        if isinstance(json_data, list):
            return JsonResponse(json_data, status=response.status_code, safe=False)
        else:
            # Return the JSON object directly
            return JsonResponse(json_data, status=response.status_code)

    except requests.RequestException as e:
        log_data = [f"info|| {datetime.datetime.now()}: proxy redirection error"]
        context = {
                "request_url": request.META['PATH_INFO'], "error": e, "payload": request.body}
        log_data.append(f"info || context :{context}")
        log_data.append(LINE_BREAK)
        api_logging(log_data)
        return JsonResponse(message_response(PROXY_ERROR_MESSAGE), status=status.HTTP_400_BAD_REQUEST)