"""
Contains view callables serving data from backend application layers
to the client.
"""

from pyramid.view import view_defaults, view_config
from pyramid.i18n import TranslationStringFactory

from Knowledge_Database_App.content.content_view import ContentView
from Knowledge_Database_App.content.edit_view import EditView
from Knowledge_Database_App.content.vote_view import VoteView
from Knowledge_Database_App.user.user_view import UserView
from Knowledge_Database_App.user.admin_view import AdminView
from Knowledge_Database_App.user.report_view import ReportView


_ = TranslationStringFactory('web_api')


def test_view(request):
    return {'project': 'web_api'}


class Content:

    def __init__(self, request):
        self.request = request

    def get(self):
        pass

    def post(self):
        pass

    def get_names(self):
        pass

    def get_content_types(self):
        pass

    def get_keywords(self):
        pass

    def get_citations(self):
        pass


class ContentPiece:

    def __init__(self, request):
        self.request = request

    def get(self):
        pass

    def get_authors(self):
        pass

    def get_edits(self):
        pass

    def get_edit(self):
        pass

    def get_edit_vote(self):
        pass

    def post_edit_vote(self):
        pass

    def get_edit_activity(self):
        pass


class User:

    def __init__(self, request):
        self.request = request

    def get(self):
        pass

    def get_recent_activity(self):
        pass

    def get_content(self):
        pass

    def get_edits(self):
        pass

    def post(self):
        pass

    def patch(self):
        pass

    def delete(self):
        pass

    def post_session(self):
        pass

    def delete_session(self):
        pass


class Report:

    def __init__(self, request):
        self.request = request

    def get(self):
        pass

    def post(self):
        pass

    def get_report(self):
        pass

    def post_admin_report(self):
        pass
