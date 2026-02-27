from django.utils import timezone
from django.conf import settings
import os

class VisitLogMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        try:
            path = request.path
            ip = request.META.get('REMOTE_ADDR', '')
            ua = request.META.get('HTTP_USER_AGENT', '')[:120]
            line = f"{timezone.now().isoformat()} | {ip} | {path} | {ua}\n"
            log_path = os.path.join(settings.BASE_DIR, 'visits.log')
            with open(log_path, 'a', encoding='utf-8') as f:
                f.write(line)
        except Exception:
            pass

        return response
