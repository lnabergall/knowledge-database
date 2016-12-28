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
from Knowledge_Database_App.user.report_view import ReportView


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
                try:
                    content_pieces = ContentView.bulk_retrieve(
                        sort=self.request.matchdict.get("sort"),
                        page_num=self.request.data["page_num"]
                    )
                except Exception as e:
                    pass
            elif content_part:
                try:
                    content_pieces = ContentView.bulk_retrieve(
                        sort=self.request.matchdict.get("sort"),
                        content_part=content_part,
                        page_num=self.request.data["page_num"]
                    )
                except Exception as e:
                    pass
            elif self.request.matchdict.get("q"):
                try:
                    content_pieces = ContentView.search(
                        query=self.request.matchdict["q"],
                        page_num=self.request.data["page_num"],
                    )
                except Exception as e:
                    pass
            else:
                try:
                    content_pieces = ContentView.bulk_retrieve(
                        page_num=self.request.data["page_num"])
                except Exception as e:
                    pass
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
            try:
                names = ContentView.autocomplete(
                    "name", self.request.matchdict["complete"])
            except Exception as e:
                pass
            else:
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
            try:
                content_types = ContentView.get_parts(content_part="content_type")
            except Exception as e:
                pass
            else:
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
                try:
                    keywords = ContentView.autocomplete(
                        "keyword", self.request.matchdict["complete"])
                except Exception as e:
                    pass
                else:
                    response = {
                        "message": "Keyword completions retrieved successfully."
                    }
            else:
                try:
                    keywords = ContentView.get_parts(content_part="keyword",
                                                    page_num=self.request.data["page_num"])
                except Exception as e:
                    pass
                else:
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
                try:
                    citations = ContentView.autocomplete(
                        "citation", self.request.matchdict["complete"])
                except Exception as e:
                    pass
                else:
                    response = {
                        "message": "Citation completions retrieved successfully."
                    }
            else:
                try:
                    citations = ContentView.get_parts(
                        content_part="citation",
                        page_num=self.request.data["page_num"])
                except Exception as e:
                    pass
                else:
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
            try:
                edits = EditView.bulk_retrieve(
                    content_id=self.request.data["content_id"],
                    page_num=self.request.data["page_num"] or 1)
            except Exception as e:
                pass
            else:
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
            except Exception as e:
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
                    "piece_edit", edit_id=error_data)   # Page of oldest edit
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
            except Exception as e:
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
            try:
                activity_data = ContentView.recent_activity(
                    user_id=self.user.user_id, page_num=page_num)
            except Exception as e:
                pass
            else:
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
            try:
                user_content = ContentView.user_content(
                    user_id=self.user.user_id, page_num=page_num)
            except Exception as e:
                pass
            else:
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
            try:
                user_edits = EditView.bulk_retrieve(user_id=self.user.user_id,
                                                    page_num=page_num)
            except Exception as e:
                pass
            else:
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
            report_status = self.request.matchdict["report_status"]
            id = (self.request.matchdict.get("admin_id")
                  or self.request.matchdict.get("user_id")
                  or self.request.matchdict.get("content_id")
                  or self.request.matchdict.get("ip_address"))
            id_type = ({"admin_id", "user_id", "content_id", "ip_address"}
                       & set(self.request.matchdict.keys()))
            if len(id_type) != 1:
                pass    # ERROR
            else:
                kargs = {
                    id_type.pop(): id,
                    "report_status": report_status,
                    "page_num": self.request.data["page_num"]
                }
                try:
                    reports = ReportView.bulk_retrieve(**kargs)
                except Exception as e:
                    pass
                else:
                    return {
                        "data": reports,
                        "links": {
                            "came_from": self.came_from,
                            "url": self.url,
                        },
                        "message": "User reports retrieved successfully."
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
                    "go_to": self.request.route_url("report",
                        report_id=self.request.context["report_id"])  # Report page
                },
                "message": "User report successfully submitted."
            }

    def get_report(self):
        if self.request.exception:
            pass
        else:
            return {
                "data": self.request.context.report,
                "links": {
                    "came_from": self.came_from,
                    "url": self.url,
                },
                "message": "User report retrieved successfully."
            }

    def post_admin_report(self):
        if self.request.exception:
            pass
        else:
            try:
                ReportView.resolve(
                    report_id=self.request.data["report_id"],
                    report_status=self.request.data["report_status"],
                    admin_report=self.request.data["admin_report"]
                )
            except Exception as e:
                pass
            else:
                self.request.response.status_code = 201
                return {
                    "links": {
                        "came_from": self.came_from,
                        "url": self.url,
                        "go_to": self.request.route_url("report",
                            report_id=self.request.data["report_id"])  # Report page
                    },
                    "message": "Admin resolution report submitted successfully."
                }
