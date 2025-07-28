class LastVisitedMiddleware:
    """This middleware sets the last visited url as session field"""

    def __init__(self, get_response):
        self.get_response = get_response


    def __call__(self, request):
        # Code to be executed for each request before
        # the view (and later middleware) are called.
        self.save_last_page(request)
        response = self.get_response(request)

        # Code to be executed for each request/response after
        # the view is called.

        return response

    def save_last_page(self, request):
        """Intercept the request and add the current path to it"""
        
        request_path = request.get_full_path_info()

        try:
            request.session['last_visited'] = request.session['currently_visiting']
            request.session['http_referer'] = request.META.get('HTTP_REFERER', request_path)
        except KeyError:
            # silence the exception - this is the users first request
            pass

        request.session['currently_visiting'] = request_path
        


