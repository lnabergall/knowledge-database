"""
Contains the resources associated with back-end application data objects.
"""

from pyramid.security import Allow, Deny, Everyone, Authenticated, ALL_PERMISSIONS

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


def content_factory(request):
    data = {
        "content_id": (request.params.getone("content_id") or
                       request.json_body.get("content_id")),
        "accepted_edit_id": (request.params.getone("accepted_edit_id") or
                             request.json_body.get("accepted_edit_id")),
        "rejected_edit_id": (request.params.getone("rejected_edit_id") or
                             request.json_body.get("rejected_edit_id")),
        "content_type": (request.params.getone("content_type") or
                         request.json_body.get("content_type")),
        "name": (request.params.getone("name") or
                 request.json_body.get("name")),
        "alternate_names": (request.params.getone("alternate_names") or
                            request.json_body.get("alternate_names")),
        "text": (request.params.getone("text") or
                 request.json_body.get("text")),
        "keywords": (request.params.getone("keywords") or
                     request.json_body.get("keywords")),
        "citations": (request.params.getone("citations") or
                      request.json_body.get("citations")),
        "submit": (request.params.getone("submit") or
                   request.json_body.get("submit") or False),
    }
    user_id = request.authenticated_userid
    if user_id is None:
        return None
    else:
        data["first_author_id"] = user_id
        return ContentResource(**data)


class EditResource(EditView):

    def __acl__(self):
        return [
            (Allow, Everyone, (VIEW, CREATE))
        ]


def edit_factory(request):
    data = {
        "edit_id": (request.params.getone("edit_id") or
                    request.json_body.get("edit_id")),
        "validation_status": (request.params.getone("validation_status") or
                              request.json_body.get("validation_status")),
        "content_id": (request.params.getone("content_id") or
                       request.json_body.get("content_id")),
        "edit_text": (request.params.getone("edit_text") or
                      request.json_body.get("edit_text")),
        "edit_rationale": (request.params.getone("edit_rationale") or
                           request.json_body.get("edit_rationale")),
        "content_part": (request.params.getone("content_part") or
                         request.json_body.get("content_part")),
        "part_id": (request.params.getone("part_id") or
                    request.json_body.get("part_id")),
        "original_part_text": (request.params.getone("original_part_text") or
                               request.json_body.get("original_part_text")),
        "start_timestamp": (request.params.getone("start_timestamp") or
                            request.json_body.get("start_timestamp")),
        "submit": (request.params.getone("submit") or
                   request.json_body.get("submit") or False),
    }
    user_id = request.unauthenticated_userid
    auth_user_id = request.authenticated_userid
    if user_id is None:
        return None
    else:
        data["author_id"] = auth_user_id
        data["author_type"] = "U" if auth_user_id else user_id
        return EditResource(**data)


class VoteResource(VoteView):

    def __acl__(self):
        edit = EditView(self.vote["edit_id"], validation_status="validating")
        content = ContentView(content_id=edit.edit["content_id"])
        if content.authors is not None:
            author_list = [(Allow, format_identifier(user["user_id"]),
                            (VIEW, AUTHOR)) for user in content.authors]
        else:
            author_list = []
        return [
            (Allow, ADMIN, VIEW)
        ] + author_list


def vote_factory(request):
    data = {
        "vote_status": (request.params.getone("vote_status") or
                        request.json_body.get("vote_status")),
        "edit_id": (request.params.getone("edit_id") or
                    request.json_body.get("edit_id")),
        "vote": (request.params.getone("vote") or
                 request.json_body.get("vote")),
        "timestamp": (request.params.getone("timestamp") or
                      request.json_body.get("timestamp")),
        "close_timestamp": (request.params.getone("close_timestamp") or
                            request.json_body.get("close_timestamp")),
    }
    voter_id = request.authenticated_userid
    if voter_id is None:
        return None
    else:
        data["voter_id"] = voter_id
        return VoteResource(**data)


class UserResource(UserView):

    def __acl__(self):
        return [
            (Deny, Authenticated, CREATE),
            (Allow, Everyone, CREATE),
            (Allow, format_identifier(self.user["user_id"]),
            (VIEW, MODIFY, DELETE)),
        ]


def get_user_data(request):
    data = {
        "email": (request.params.getone("email") or
                  request.json_body.get("email")),
        "password": (request.params.getone("password") or
                     request.json_body.get("password")),
        "user_name": (request.params.getone("user_name") or
                      request.json_body.get("user_name")),
        "remember_id": (request.params.getone("remember_id") or
                        request.json_body.get("remember_id")),
        "remember_token": (request.params.getone("remember_token") or
                           request.json_body.get("remember_token")),
        "remember_user": (request.params.getone("remember_user") or
                          request.json_body.get("remember_user") or False),
        "confirmation_id": (request.params.getone("confirmation_id") or
                            request.json_body.get("confirmation_id")),
        "page_num": (request.params.getone("page_num") or
                     request.json_body.get("page_num")),
    }
    return data


def user_factory(request):
    data = get_user_data(request)
    user_id = request.authenticated_userid
    if user_id is None:
        return None
    else:
        data["user_id"] = user_id
        if (request.method != "PATCH"
                and request.matched_route.name != "user_content"
                and request.matched_route.name != "user_activity"
                and request.matched_route.name != "user_edits"):
            return UserResource(**data)
        else:
            request.set_property(get_user_data, "data", reify=True)
            return UserResource(user_id=data["user_id"])


class AdminResource(AdminView):

    def __acl__(self):
        return [
            (Allow, format_identifier(self.admin["user_id"]),
             (VIEW, MODIFY, DELETE)),
        ]


def admin_factory(request):
    return user_factory(request)


class ReportResource(ReportView):

    def __acl__(self):
        return [
            (Allow, Everyone, (CREATE, VIEW)),
            (Allow, ADMIN, ALL_PERMISSIONS)
        ]


def report_factory(request):
    data = {
        "report_id": (request.params.getone("report_id") or
                      request.json_body.get("report_id")),
        "report_status": (request.params.getone("report_status") or
                          request.json_body.get("report_status")),
        "content_id": (request.params.getone("content_id") or
                       request.json_body.get("content_id")),
        "report_text": (request.params.getone("report_text") or
                        request.json_body.get("report_text")),
        "report_type": (request.params.getone("report_type") or
                        request.json_body.get("report_type")),
    }
    user_id = request.unauthenticated_userid
    auth_user_id = request.authenticated_userid
    if user_id is None:
        return None
    else:
        data["author_id"] = auth_user_id
        data["author_type"] = "U" if auth_user_id else user_id
        return ReportResource(**data)
