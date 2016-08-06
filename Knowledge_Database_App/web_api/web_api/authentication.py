"""
Authentication objects and settings.
"""

from pyramid.authentication import SessionAuthenticationPolicy

from Knowledge_Database_App.content.edit import is_ip_address


class CustomSessionAuthPolicy(SessionAuthenticationPolicy):

    def __init__(self, *args, **kwargs):
        super(CustomSessionAuthPolicy, self).__init__(*args, **kwargs)
        self.authenticated_userid_key = self.prefix + "authenticated_userid"

    def authenticated_userid(self, request):
        return int(request.session.get(self.authenticated_userid_key))
