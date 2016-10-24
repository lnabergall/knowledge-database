"""
Contains view callables serving data from backend application layers
to the client.
"""

from pyramid.view import view_defaults, view_config
from pyramid.i18n import TranslationStringFactory

from Knowledge_Database_App.web_api.web_api.authentication import (
    remember_authenticated)


_ = TranslationStringFactory('web_api')


def test_view(request):
    return {'project': 'web_api'}


class ContentResourceView:

    def __init__(self, request):
        self.request = request

    def get(self):
        if self.request.exception:
            pass
        else:
            pass

    def post(self):
        if self.request.exception:
            pass
        else:
            pass

    def get_names(self):
        if self.request.exception:
            pass
        else:
            pass

    def get_content_types(self):
        if self.request.exception:
            pass
        else:
            pass

    def get_keywords(self):
        if self.request.exception:
            pass
        else:
            pass

    def get_citations(self):
        if self.request.exception:
            pass
        else:
            pass


class ContentPieceResourceView:

    def __init__(self, request):
        self.request = request

    def get(self):
        if self.request.exception:
            pass
        else:
            pass

    def get_authors(self):
        if self.request.exception:
            pass
        else:
            pass

    def get_edits(self):
        if self.request.exception:
            pass
        else:
            pass

    def get_edit(self):
        if self.request.exception:
            pass
        else:
            pass

    def post_edit(self):
        if self.request.exception:
            pass
        else:
            pass

    def get_edit_vote(self):
        if self.request.exception:
            pass
        else:
            pass

    def post_edit_vote(self):
        if self.request.exception:
            pass
        else:
            pass

    def get_edit_activity(self):
        if self.request.exception:
            pass
        else:
            pass


class UserResourceView:

    def __init__(self, request):
        self.request = request
        self.came_from = (self.request.params.get("came_from") or
                          self.request.json_body.get("came_from"))
        self.url = self.request.current_route_url

    def get(self):
        if self.request.exception:
            pass
        else:
            return self.get_recent_activity()

    def get_recent_activity(self):
        if self.request.exception:
            pass
        else:
            pass

    def get_content(self):
        if self.request.exception:
            pass
        else:
            pass

    def get_edits(self):
        if self.request.exception:
            pass
        else:
            pass

    def post(self):
        if self.request.exception:
            pass
        else:
            self.request.response.status_code = 201
            return {
                "data": {
                    "email": self.request.context.email,
                    "password": self.request.context.password,
                    "user_name": self.request.context.user_name,
                },
                "links": {
                    "came_from": self.came_from,
                    "url": self.url,
                    "go_to": self.request.route_url("user_sessions"),
                },
                "message": "A confirmation email will be sent to you " +
                           "shortly to verify your email address prior " +
                           "to login.",
            }

    def patch(self):
        if self.request.exception:
            pass
        else:
            pass

    def delete(self):
        if self.request.exception:
            pass
        else:
            pass

    def post_session(self):
        if self.request.exception:
            pass
        else:
            if not self.request.authenticated_userid:
                remember_authenticated(request, self.request.context.user_id)
            return {
                "data": {
                    "email": self.request.context.email,
                    "password": self.request.context.password,
                    "user_name": self.request.context.user_name,
                },
                "links": {
                    "came_from": self.came_from,
                    "url": self.url,
                    "go_to": self.request.route_url("user",
                        user_id=self.request.context.user_id),
                },
                "message": "Login successful.",
            }

    def delete_session(self):
        if self.request.exception:
            pass
        else:
            if self.request.authenticated_userid:
                self.request.session.invalidate()
            return {
                "links": {
                    "came_from": self.came_from,
                    "url": self.url,
                    "go_to": self.request.route_url("home"),
                },
                "message": "Logout successful."
            }


class ReportResourceView:

    def __init__(self, request):
        self.request = request

    def get(self):
        if self.request.exception:
            pass
        else:
            pass

    def post(self):
        if self.request.exception:
            pass
        else:
            pass

    def get_report(self):
        if self.request.exception:
            pass
        else:
            pass

    def post_admin_report(self):
        if self.request.exception:
            pass
        else:
            pass
