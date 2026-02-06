import logging
import time
import traceback

# Logger initialization
logger = logging.getLogger("request.audit")

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()

        # Execute the request
        response = self.get_response(request)

        # Calculate metrics
        duration = round(time.time() - start_time, 3)
        status = getattr(response, "status_code", 200)
        
        # Prepare log data
        log_extra = {
            "ip": self.get_client_ip(request),
            "user_id": request.user.id if hasattr(request, "user") and request.user.is_authenticated else None,
            "method": request.method,
            "path": request.path,
            "status_code": status,
            "duration": duration,
            "exception": getattr(request, "_exception_stack", None),
        }

        message = getattr(response, "reason_phrase", "HTTP Request")

        # Logging based on status code
        if status >= 500:
            logger.error(message, extra=log_extra)
        elif status >= 400:
            logger.warning(message, extra=log_extra)
        elif duration > 5:  # Slow request threshold
            logger.warning("Slow Request", extra=log_extra)
        else:
            logger.info(message, extra=log_extra)

        return response

    def process_exception(self, request, exception):
        """
        Captured when a view raises an exception.
        """
        request._exception_stack = traceback.format_exc()
        return None  # Let Django handle the standard error response

    def get_client_ip(self, request):
        """
        Get real IP even if behind a proxy like Nginx.
        """
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            return xff.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")