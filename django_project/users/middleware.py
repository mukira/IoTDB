import cass

def get_user(request):
    """
    Function to read in the request data from the session, pull them from cassandra database, and log them in via django session
    """
    if 'username' in request.session:
        try:
            user = cass.get_user_by_username(request.session['username'])
            return {
                'username': user.username,
                'password': user.password,
                'is_authenticated': True
            }
        except cass.DatabaseError:
            pass
    return {
        'password': None,
        'is_authenticated': False,
    }


class LazyUser(object):
    """
    If you're already a logged in cached user, then be lazy and let you stay logged in
    """
    def __get__(self, request, obj_type=None):
        if not hasattr(request, '_cached_user'):
            request._cached_user = get_user(request)
        return request._cached_user


class UserMiddleware(object):
    """
    Main wrapper function for the middleware
    """
    def process_request(self, request):
        request.__class__.user = LazyUser()
