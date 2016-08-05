"""
Contains view callables serving data from backend application layers
to the client.
"""

from pyramid.view import view_defaults, view_config
from pyramid.i18n import TranslationStringFactory


_ = TranslationStringFactory('web_api')


def test_view(request):
    return {'project': 'web_api'}


class ContentResourceView:

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


class ContentPieceResourceView:

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

    def post_edit(self):
        pass

    def get_edit_vote(self):
        pass

    def post_edit_vote(self):
        pass

    def get_edit_activity(self):
        pass


class UserResourceView:

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


class ReportResourceView:

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
