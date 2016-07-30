"""
Contains the resources associated with back-end application data objects.
"""

from pyramid.security import Allow, Everyone, Authenticated

from Knowledge_Database_App.content.content_view import ContentView
from Knowledge_Database_App.content.edit_view import EditView
from Knowledge_Database_App.content.vote_view import VoteView
from Knowledge_Database_App.user.user_view import UserView
from Knowledge_Database_App.user.admin_view import AdminView
from Knowledge_Database_App.user.report_view import ReportView


class MyResource:
    pass


root = MyResource()


def get_root(request):
    return root


VIEW = "view"
EDIT = "edit"


class ContentResource(ContentView):

    def __acl__(self):
        pass


class EditResource(EditView):

    def __acl__(self):
        pass


class VoteResource(VoteView):

    def __acl__(self):
        pass


class UserResource(UserView):

    def __acl__(self):
        pass


class AdminResource(AdminView):

    def __acl__(self):
        pass


class ReportResource(ReportView):

    def __acl__(self):
        pass
