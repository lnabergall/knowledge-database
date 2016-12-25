"""
Contains view callables serving data from backend application layers
to the client.
"""

from pyramid.view import view_defaults, view_config
from pyramid.i18n import TranslationStringFactory

from Knowledge_Database_App.web_api.web_api.authentication import (
    remember_authenticated)
from Knowledge_Database_App.content.content_view import ContentView
from Knowledge_Database_App.content.edit_view import EditView
from Knowledge_Database_App.content.vote_view import VoteView


_ = TranslationStringFactory('web_api')


def test_view(request):
    return {'project': 'web_api'}


class ContentResourceView:

    def __init__(self, request):
        self.request = request
        self.came_from = (self.request.params.get("came_from") or
                          self.request.json_body.get("came_from"))
        self.url = self.request.current_route_url

    def get(self):
        if self.request.exception:
            pass
        else:
            content_part = (self.request.matchdict.get("keyword")
                or self.request.matchdict.get("content_type")
                or self.request.matchdict.get("name")
                or self.request.matchdict.get("citation"))
            if self.request.matchdict.get("sort"):
                content_pieces = ContentView.bulk_retrieve(
                    sort=self.request.matchdict.get("sort"),
                    page_num=self.request.data["page_num"]
                )
            elif content_part:
                content_pieces = ContentView.bulk_retrieve(
                    sort=self.request.matchdict.get("sort"),
                    content_part=content_part,
                    page_num=self.request.data["page_num"]
                )
            elif self.request.matchdict.get("q"):
                content_pieces = ContentView.search(
                    query=self.request.matchdict["q"],
                    page_num=self.request.data["page_num"],
                )
            else:
                content_pieces = ContentView.bulk_retrieve(
                    page_num=self.request.data["page_num"])

            return {
                "data": content_pieces,
                "links": {
                    "came_from": self.came_from,
                    "url": self.url,
                },
                "message": "Content pieces retrieved successfully."
            }

    def post(self):
        if self.request.exception:
            pass
        else:
            self.request.response.status_code = 201
            return {
                "links": {
                    "came_from": self.came_from,
                    "url": self.url,
                    "go_to": self.request.route_url("content_piece",
                        content_id=self.request.context.content_id),   # Piece page
                },
                "message": ("Content submission successful. See the "
                            "included link for the public webpage."),
            }

    def get_names(self):
        if self.request.exception:
            pass
        else:
            names = ContentView.autocomplete(
                "name", self.request.matchdict["complete"])
            return {
                "data": names,
                "links": {
                    "came_from": self.came_from,
                    "url": self.url,
                },
                "message": "Name completions retrieved successfully."
            }

    def get_content_types(self):
        if self.request.exception:
            pass
        else:
            content_types = ContentView.get_parts(content_part="content_type")
            return {
                "data": content_types,
                "links": {
                    "came_from": self.came_from,
                    "url": self.url,
                },
                "message": "Content types retrieved successfully."
            }

    def get_keywords(self):
        if self.request.exception:
            pass
        else:
            if self.request.matchdict.get("complete"):
                keywords = ContentView.autocomplete(
                    "keyword", self.request.matchdict["complete"])
                response = {
                    "message": "Keyword completions retrieved successfully."
                }
            else:
                keywords = ContentView.get_parts(content_part="keyword",
                                                 page_num=self.request.data["page_num"])
                response = {"message": "Keywords retrieved successfully."}

            response.update({
                "data": keywords,
                "links": {
                    "came_from": self.came_from,
                    "url": self.url,
                },
            })
            return response

    def get_citations(self):
        if self.request.exception:
            pass
        else:
            if self.request.matchdict.get("complete"):
                citations = ContentView.autocomplete(
                    "citation", self.request.matchdict["complete"])
                response = {
                    "message": "Citation completions retrieved successfully."
                }
            else:
                citations = ContentView.get_parts(content_part="citation",
                                                  page_num=self.request.data["page_num"])
                response = {"message": "Citations retrieved successfully."}

            response.update({
                "data": citations,
                "links": {
                    "came_from": self.came_from,
                    "url": self.url,
                },
            })
            return response


class ContentPieceResourceView:

    def __init__(self, request):
        self.request = request
        self.came_from = (self.request.params.get("came_from") or
                          self.request.json_body.get("came_from"))
        self.url = self.request.current_route_url

    def get(self):
        if self.request.exception:
            pass
        else:
            return {
                "data": self.request.context.content,
                "links": {
                    "came_from": self.came_from,
                    "url": self.url,
                },
                "message": "Content piece retrieved successfully."
            }

    def get_authors(self):
        if self.request.exception:
            pass
        else:
            return {
                "data": self.request.context.content.authors,
                "links": {
                    "came_from": self.came_from,
                    "url": self.url,
                },
                "message": "Content piece authors retrieved successfully."
            }

    def get_edits(self):
        if self.request.exception:
            pass
        else:
            edits = EditView.bulk_retrieve(
                content_id=self.request.data["content_id"],
                page_num=self.request.data["page_num"] or 1)
            return {
                "data": edits,
                "links": {
                    "came_from": self.came_from,
                    "url": self.url,
                },
                "message": "Content piece edits retrieved successfully."
            }

    def get_edit(self):
        if self.request.exception:
            pass
        else:
            return {
                "data": self.request.context.edit,
                "links": {
                    "came_from": self.came_from,
                    "url": self.url,
                },
                "message": "Content piece edit retrieved successfully."
            }

    def post_edit(self):
        if self.request.exception:
            pass
        else:
            if self.request.data["submit"]:
                self.request.response.status_code = 201
                response = {
                    "links": {
                        "came_from": self.came_from,
                        "url": self.url,
                        "go_to": self.request.route_url("piece_edit",
                            edit_id=self.request.context.edit_id),   # Edit page
                    },
                    "message": ("Edit submission successful. See the "
                                "included link for the public webpage."),
                }
            else:
                if self.request.matchdict["check_conflict"]:
                    self.request.context.conflict = EditView.conflict
                response = {
                    "data": self.request.context.edit,
                    "links": {
                        "came_from": self.came_from,
                        "url": self.url,
                    },
                    "message": "Edit successfully assembled and validated."
                }
            return response


    def get_edit_vote(self):
        if self.request.exception:
            pass
        else:
            edit_id = self.request.data["edit_id"]
            vote_status = self.request.data["vote_status"]
            validation_status = self.request.data["validation_status"]
            try:
                vote_summary = VoteView.get_vote_results(
                    vote_status, edit_id, validation_status)
            except:
                pass
            else:
                return {
                    "data": vote_summary,
                    "links": {
                        "came_from": self.came_from,
                        "url": self.url,
                    },
                    "message": "Vote summary successfully retrieved."
                }

    def post_edit_vote(self):
        if self.request.exception:
            pass
        else:
            error_data = self.request.context.error_response
            response = {
                "links": {
                    "came_from": self.came_from,
                    "url": self.url,
                }
            }
            if error_data:
                response["data"] = {"earliest_edit_id": error_data}
                response["links"]["go_to"] = self.request.route_url(
                    "piece_edit", edit_id=error_data)
                response["message"] = ("To minimize the potential for " +
                    "edit conflicts, please vote on the earliest submitted " +
                    "edit before voting on later edits. See the included " +
                    "link for the public webpage to the earliest edit.")
            else:
                self.request.response.status_code = 201
                response["message"] = "Vote successfully submitted."

            return response

    def get_edit_activity(self):
        if self.request.exception:
            pass
        else:
            try:
                edit_activity = ContentView.validation_data(
                    self.request.authenticated_userid,
                    self.request.data["content_id"],
                    self.request.data["validating_page_num"],
                    self.request.data["closed_page_num"],
                )
            except:
                pass
            else:
                return {
                    "data": edit_activity,
                    "links": {
                        "came_from": self.came_from,
                        "url": self.url,
                    },
                    "message": "Edit activity successfully retrieved."
                }


class UserResourceView:

    def __init__(self, request):
        self.request = request
        self.came_from = (self.request.params.get("came_from") or
                          self.request.json_body.get("came_from"))
        self.url = self.request.current_route_url
        self.user = self.request.context

    def get(self):
        if self.request.exception:
            pass
        else:
            return self.get_recent_activity()

    def get_recent_activity(self):
        if self.request.exception:
            pass
        else:
            page_num = self.request.data["page_num"] or 1
            activity_data = ContentView.recent_activity(
                user_id=self.user.user_id, page_num=page_num)
            return {
                "data": activity_data,
                "links": {
                    "came_from": self.came_from,
                    "url": self.url,
                },
                "message": "Recent activity metadata retrieved successfully."
            }

    def get_content(self):
        if self.request.exception:
            pass
        else:
            page_num = self.request.data["page_num"] or 0
            user_content = ContentView.user_content(
                user_id=self.user.user_id, page_num=page_num)
            return {
                "data": user_content,
                "links": {
                    "came_from": self.came_from,
                    "url": self.url,
                },
                "message": "Authored content metadata retrieved successfully."
            }

    def get_edits(self):
        if self.request.exception:
            pass
        else:
            page_num = self.request.data["page_num"] or 1
            user_edits = EditView.bulk_retrieve(user_id=self.user.user_id,
                                                page_num=page_num)
            return {
                "data": user_edits,
                "links": {
                    "came_from": self.came_from,
                    "url": self.url,
                },
                "message": "User edit metadata retrieved successfully."
            }

    def post(self):
        if self.request.exception:
            pass
        else:
            self.request.response.status_code = 201
            return {
                "data": {
                    "email": self.user.email,
                    "user_name": self.user.user_name,
                },
                "links": {
                    "came_from": self.came_from,
                    "url": self.url,
                    "go_to": self.request.route_url("user_sessions"),   # Login
                },
                "message": ("Account registration successful. A confirmation "
                            "email will be sent to you shortly to verify "
                            "your email address."),
            }

    def patch(self):
        if self.request.exception:
            pass
        else:
            confirmation_id = self.request.data["confirmation_id"]
            if confirmation_id:
                try:
                    self.user.confirm(self.user.email, confirmation_id)
                except Exception as e:
                    pass
                else:
                    return {
                        "links": {
                            "came_from": self.came_from,
                            "url": self.url,
                            "go_to": self.request.route_url("user_sessions"),  # Login
                        },
                        "message": "Account email address confirmed.",
                    }
            else:
                try:
                    message = ""
                    if self.request.data["user_name"]:
                        self.user.update(self.user.user_id,
                            new_user_name=self.request.data["user_name"])
                        message = "User name updated."
                    elif self.request.data["email"]:
                        self.user.update(self.user.user_id,
                            new_email=self.request.data["email"])
                        message = ("Email address updated. A confirmation "
                                   "email will be sent to you shortly to verify "
                                   "your email address.")
                    elif self.request.data["password"]:
                        self.user.update(self.user.user_id,
                            new_password=self.request.data["password"])
                        message = "Password updated."
                except Exception as e:
                    pass
                else:
                    return {
                        "links": {
                            "came_from": self.came_from,
                            "url": self.url,
                        },
                        "message": message,
                    }

    def delete(self):
        if self.request.exception:
            pass
        else:
            try:
                self.user.delete(self.user.user_id)
            except Exception as e:
                pass
            else:
                return {
                    "links": {
                        "came_from": self.came_from,
                        "url": self.url,
                    },
                    "message": "Account deactivated.",
                }

    def post_session(self):
        if self.request.exception:
            pass
        else:
            if not self.request.authenticated_userid:
                remember_authenticated(self.request, self.user.user_id)
            return {
                "data": {
                    "email": self.user.email,
                    "user_name": self.user.user_name,
                },
                "links": {
                    "came_from": self.came_from,
                    "url": self.url,
                    "go_to": self.request.route_url("user",
                        user_id=self.user.user_id),  # User home
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
                    "go_to": self.request.route_url("home"),    # App home
                },
                "message": "Logout successful."
            }


class ReportResourceView:

    def __init__(self, request):
        self.request = request
        self.came_from = (self.request.params.get("came_from") or
                          self.request.json_body.get("came_from"))
        self.url = self.request.current_route_url

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
