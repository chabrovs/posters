

class EnsureSessionKeyMiddleware:
    """
    This class purpose is to ensure that the session_key is create for all Anonymous users within all project applications.
    If the 'request.session.session_key' == None, than this middleware is responsible for creating the 'session_key' for the request. 
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Ensure a session key is present
        if not request.session.session_key:
            request.session.create()  # Create a new session if it doesn't exist

        # Proceed with the request processing
        response = self.get_response(request)
        return response
