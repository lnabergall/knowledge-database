"""
Contains the resources associated with back-end application data objects.
"""

from pyramid.security import Allow, Everyone, Authenticated, ALL_PERMISSIONS

from Knowledge_Database_App.content.content_view import ContentView
from Knowledge_Database_App.content.edit_view import EditView
from Knowledge_Database_App.content.vote_view import VoteView
from Knowledge_Database_App.user.user_view import UserView
from Knowledge_Database_App.user.admin_view import AdminView
from Knowledge_Database_App.user.report_view import ReportView
from Knowledge_Database_App.web_api.web_api.permissions import (
    VIEW, CREATE, MODIFY, AUTHOR)


class Root:

    def __init__(self, request):
        self.request = request


def get_root(request):
    return Root(request)


def get_identifiers(user_id, request):
    pass


USER_ID_PREFIX = "user_id:"
ADMIN = "admin"


class ContentResource(ContentView):

    def __acl__(self):
        if self.content["authors"] is not None:
            author_list = [(Allow, USER_ID_PREFIX + user["user_id"], AUTHOR)
                           for user in self.content["authors"]]
        else:
            author_list = []
        return [
            (Allow, Everyone, VIEW),
            (Allow, Authenticated, CREATE),
            (Allow, ADMIN, ALL_PERMISSIONS)
        ] + author_list


class EditResource(EditView):

    def __acl__(self):
        return [
            (Allow, Everyone, (VIEW, CREATE))
        ]


class VoteResource(VoteView):

    def __acl__(self):
        if self.content["authors"] is not None:
            author_list = [(Allow, USER_ID_PREFIX + user["user_id"], AUTHOR)
                           for user in self.content["authors"]]
            # NOT WORKING, NEED TO ADD ACCESS TO CONTENT AUTHORS
        else:
            author_list = []
        return [
            (Allow, ADMIN, VIEW)
        ] + author_list


class UserResource(UserView):

    def __acl__(self):
        pass


class AdminResource(AdminView):

    def __acl__(self):
        pass


class ReportResource(ReportView):

    def __acl__(self):
        return [
            (Allow, Everyone, CREATE),
            (Allow, ADMIN, VIEW)
        ]
