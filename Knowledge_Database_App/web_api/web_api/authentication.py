"""
Authentication objects and settings.
"""

from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.security import _get_authentication_policy

from Knowledge_Database_App.content.edit import is_ip_address


class CustomSessionAuthPolicy(SessionAuthenticationPolicy):

    def __init__(self, *args, **kwargs):
        super(CustomSessionAuthPolicy, self).__init__(*args, **kwargs)
        self.authenticated_userid_key = self.prefix + "authenticated_userid"

    def authenticated_userid(self, request):
        stored_id = request.session.get(self.authenticated_userid_key)
        try:
            return int(stored_id)
        except TypeError:
            return stored_id

    def remember_authenticated(self, request, userid, **kw):
        self.remember(request, userid, **kw)
        request.session[self.authenticated_userid_key] = userid
        return []


def remember_authenticated(request, userid, **kw):
        policy = _get_authentication_policy(request)
        if policy is None:
            return []
        else:
            return policy.remember_authenticated(request, userid, **kw)