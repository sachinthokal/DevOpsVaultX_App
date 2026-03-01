import logging
import time
import traceback
import json
from django.conf import settings

# Logger initialization
logger = logging.getLogger("request.audit")

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Initialize exception stack to None for each request
        request._exception_stack = None
        start_time = time.time()

        # Capture Request Payload only if DEBUG is True
        req_payload = None
        if settings.DEBUG:
            try:
                if request.content_type == 'application/json':
                    req_payload = json.loads(request.body.decode('utf-8'))
                else:
                    # Convert QueryDict to a standard dictionary
                    req_payload = request.POST.dict()
                
                # Mask sensitive information for security
                if not settings.DEBUG:
                    sensitive_keys = ['password', 'otp', 'csrfmiddlewaretoken', 'new_password']
                    for key in sensitive_keys:
                        if key in req_payload:
                            req_payload[key] = "********"
            except Exception:
                req_payload = "<Unparseable Data>"

        # Execute the request and get response
        response = self.get_response(request)

        # Calculate duration and get status code
        duration = round(time.time() - start_time, 3)
        status = getattr(response, "status_code", 200)
        
        # Capture Response Payload only if DEBUG is True
        res_payload = None
        if settings.DEBUG:
            try:
                content_type = response.get('Content-Type', '')
                
                # 1. Capture JSON response
                if "application/json" in content_type:
                    res_payload = json.loads(response.content.decode('utf-8'))
                
                # 2. Capture Redirect location (Important for 302 status)
                elif status in [301, 302]:
                    res_payload = {"redirect_to": response.get('Location', 'unknown')}
                
                # 3. Capture Django UI Messages if any
                if hasattr(request, '_messages') and request._messages:
                    messages_list = [str(m) for m in request._messages]
                    if res_payload is None:
                        res_payload = {"messages": messages_list}
                    elif isinstance(res_payload, dict):
                        res_payload["messages"] = messages_list

            except Exception:
                res_payload = "<Response Payload Capture Failed>"

        # Prepare base log data
        log_extra = {
            "ip": self.get_client_ip(request),
            "user_id": request.user.id if hasattr(request, "user") and request.user.is_authenticated else None,
            "method": request.method,
            "path": request.path,
            "status_code": status,
            "duration": duration,
            "exception": getattr(request, "_exception_stack", None),
        }

        # Inject payloads into logs only during development/debug mode
        if settings.DEBUG:
            log_extra["request_payload"] = req_payload
            log_extra["response_payload"] = res_payload

        # Get response reason or custom message
        reason = getattr(response, "reason_phrase", "HTTP Request")
        log_msg = f"{request.method} {request.path} - {status}"

        # Categorize logging based on status and duration
        if status >= 500:
            logger.error(f"Server Error: {reason}", extra=log_extra)
        elif status >= 400:
            logger.warning(f"Client Error: {reason}", extra=log_extra)
        elif duration > 5:  # Log as warning if request takes more than 5 seconds
            logger.warning(f"Slow Request: {log_msg}", extra=log_extra)
        else:
            logger.info(log_msg, extra=log_extra)

        return response

    def process_exception(self, request, exception):
        """
        Triggered when a view raises an unhandled exception.
        Captures the full traceback for the audit log.
        """
        request._exception_stack = traceback.format_exc()
        logger.debug(f"Exception captured in middleware: {str(exception)}")
        return None  # Let Django continue with its default exception handling

    def get_client_ip(self, request):
        """
        Extract the real client IP address, accounting for proxy headers.
        """
        xff = request.META.get("HTTP_X_FORWARDED_FOR")
        if xff:
            return xff.split(",")[0].strip()
        return request.META.get("REMOTE_ADDR", "unknown")