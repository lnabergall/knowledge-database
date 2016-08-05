"""
Contains the resources associated with back-end application data objects.
"""

from pyramid.security import Allow, Everyone, Authenticated, ALL_PERMISSIONS

from Knowledge_Database_App.content.edit import is_ip_address
from Knowledge_Database_App.content.content_view import ContentView
from Knowledge_Database_App.content.edit_view import EditView
from Knowledge_Database_App.content.vote_view import VoteView
from Knowledge_Database_App.user.user_view import UserView
from Knowledge_Database_App.user.admin_view import AdminView
from Knowledge_Database_App.user.report_view import ReportView
from Knowledge_Database_App.web_api.web_api.permissions import (
    VIEW, CREATE, MODIFY, DELETE, AUTHOR)


class Root:

    def __init__(self, request):
        self.request = request


def get_root(request):
    return Root(request)


def format_identifier(user_id):
    try:
        user_id = int(user_id)
    except ValueError:
        if is_ip_address(user_id):
            return "ip_address:" + str(user_id)
    except:
        raise
    else:
        return "user_id:" + str(user_id)


def get_identifiers(user_id, request):
    try:
        formatted_id = format_identifier(user_id)
    except:
        return None
    else:
        return [formatted_id]


ADMIN = "admin"


class ContentResource(ContentView):

    def __acl__(self):
        if self.content["authors"] is not None:
            author_list = [(Allow, format_identifier(user["user_id"]), AUTHOR)
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
        edit = EditView(self.vote["edit_id"], validation_status="validating")
        content = ContentView(content_id=edit.edit["content_id"])
        if content["authors"] is not None:
            author_list = [(Allow, format_identifier(user["user_id"]),
                            (VIEW, AUTHOR)) for user in content["authors"]]
        else:
            author_list = []
        return [
            (Allow, ADMIN, VIEW)
        ] + author_list


class UserResource(UserView):

    def __acl__(self):
        return [
            (Deny, Authenticated, CREATE),
            (Allow, Everyone, CREATE),
            (Allow, format_identifier(self.user["user_id"]),
             (VIEW, MODIFY, DELETE)),
        ]


class AdminResource(AdminView):

    def __acl__(self):
        return [
            (Allow, format_identifier(self.admin["user_id"]),
             (VIEW, MODIFY, DELETE)),
        ]


class ReportResource(ReportView):

    def __acl__(self):
        return [
            (Allow, Everyone, CREATE),
            (Allow, ADMIN, ALL_PERMISSIONS)
        ]
