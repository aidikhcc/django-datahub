import sys
from django.conf import settings
from django.http import HttpResponse
import traceback

class ErrorHandlingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            print(f"Exception in request: {str(e)}")
            traceback.print_exc()
            if settings.DEBUG:
                return HttpResponse(f"Error: {str(e)}\n\n{traceback.format_exc()}")
            raise 