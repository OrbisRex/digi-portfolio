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
        
        request_path = request.build_absolute_uri() # In case HTTP_REFERE doesn't work.

        try:
            request.session['last_visited'] = request.session['currently_visiting']

            loop_count = request.session.get('http_referer_count', 0)
            last_page = request.META.get('HTTP_REFERER', request_path)
            last_session_page = request.session.get('http_referer_' + str(loop_count), '')

            # Remove records if more than 15
            if int(loop_count) > 15:
                request.session.update({'http_referer_1': last_session_page})
                for i in range(2, loop_count):
                    request.session.pop('http_referer_' + str(i))
                loop_count = 1
                request.session.update({'http_referer_count': loop_count})
            
            # Save the last page into a session under numbered slot
            if (last_page != last_session_page) and (last_page != request_path) and (loop_count <=15):
                loop_count += 1
                request.session.update({'http_referer_count': loop_count})
                request.session['http_referer_' + str(loop_count)] = request.META.get('HTTP_REFERER', request_path)
        except KeyError:
            # Silence the exception - this is the users first request
            loop_count = 0
            last_page = ''
            last_session_page = ''
            pass
        # TODO: Remove
        print('Check: '+str(loop_count))
        print('Current: '+request_path)
        print('META: '+last_page)
        print('Session: '+last_session_page)
        print(request.session.get('wizard', 'None'))
        # print(request.session.get('http_referer_count'))
        for i in range(1, loop_count+1):
            print(i)
            print(request.session.get('http_referer_' + str(i)))
        
        request.session['currently_visiting'] = request_path
        


