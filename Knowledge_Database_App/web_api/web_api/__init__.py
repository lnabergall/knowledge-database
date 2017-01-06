"""
Contains the server start-up code and URL dispatch definitions.

Functions:

    main
"""

from pyramid.config import Configurator
from pyramid.authorization import ACLAuthorizationPolicy

from Knowledge_Database_App.storage import exceptions as storage_except
from Knowledge_Database_App.content import exceptions as content_except
from Knowledge_Database_App.user import exceptions as user_except
from Knowledge_Database_App.web_api.web_api import resources
from Knowledge_Database_App.web_api.web_api.permissions import (
    VIEW, CREATE, MODIFY, DELETE, AUTHOR)
from Knowledge_Database_App.web_api.web_api.authentication import (
    CustomSessionAuthPolicy)


def main(global_config, **settings):
    """
    This function returns a WSGI application.
    
    It is usually called by the PasteDeploy framework during 
    ``paster serve``.
    """
    settings.setdefault("jinja2.i18n.domain", "web_api")

    authentication_policy = CustomSessionAuthPolicy(
        callback=resources.get_identifiers)
    authorization_policy = ACLAuthorizationPolicy()

    config = Configurator(root_factory=resources.get_root, settings=settings)
    config.add_translation_dirs("locale/")
    config.set_authentication_policy(authentication_policy)
    config.set_authorization_policy(authorization_policy)
    config.include("pyramid_jinja2")
    config.include("pyramid_redis_sessions")

    config.add_static_view("static", "static")
    config.add_route("home", "/home")
    config.add_view("web_api.views.test_view",
                    context="web_api.resources.MyResource",
                    renderer="templates/mytemplate.jinja2",
                    route_name="home")

    config.add_notfound_view("web_api.views.ExceptionView",
                             attr="not_found")
    config.add_forbidden_view("web_api.views.ExceptionView",
                             attr="forbidden")

    config.add_view("web_api.views.CustomExceptionView",
                    attr="unknown_failure",
                    context=Exception)
    config.add_view("web_api.views.CustomExceptionView",
                    attr="failed_db_storage",
                    context=storage_except.ActionError)
    config.add_view("web_api.views.CustomExceptionView",
                    attr="failed_db_retrieval",
                    context=storage_except.SelectError)
    config.add_view("web_api.views.CustomExceptionView",
                    attr="invalid_data",
                    context=storage_except.InputError)
    config.add_view("web_api.views.CustomExceptionView",
                    attr="failed_uniqueness",
                    context=storage_except.UniquenessViolationError)
    config.add_view("web_api.views.CustomExceptionView",
                    attr="duplicate_vote",
                    context=content_except.DuplicateVoteError)
    config.add_view("web_api.views.CustomExceptionView",
                    attr="invalid_content",
                    context=content_except.ContentError)
    config.add_view("web_api.views.CustomExceptionView",
                    attr="duplicate_content",
                    context=content_except.DuplicateError)
    config.add_view("web_api.views.CustomExceptionView",
                    attr="expired_edit",
                    context=content_except.DataMatchingError)
    config.add_view("web_api.views.CustomExceptionView",
                    attr="closed_vote",
                    context=content_except.VoteStatusError)
    config.add_view("web_api.views.CustomExceptionView",
                    attr="invalid_password",
                    context=user_except.PasswordError)
    config.add_view("web_api.views.CustomExceptionView",
                    attr="invalid_username",
                    context=user_except.UserNameError)
    config.add_view("web_api.views.CustomExceptionView",
                    attr="invalid_email",
                    context=user_except.EmailAddressError)
    config.add_view("web_api.views.CustomExceptionView",
                    attr="rejected_authentication",
                    context=user_except.AuthenticationError)
    config.add_view("web_api.views.CustomExceptionView",
                    attr="rejected_rememberme",
                    context=user_except.RememberUserError)
    config.add_view("web_api.views.CustomExceptionView",
                    attr="rejected_confirmation",
                    context=user_except.ConfirmationError)

    config.add_route("content", "/content", factory=resources.content_factory)
    config.add_view("web_api.views.ContentResourceView",
                    route_name="content",
                    attr="get",
                    request_method="GET",
                    renderer="json",
                    context=resources.ContentResource,
                    permission=VIEW)
    config.add_view("web_api.views.ContentResourceView",
                    route_name="content",
                    attr="post",
                    request_method="POST",
                    renderer="json",
                    context=resources.ContentResource,
                    permission=CREATE,
                    require_csrf=True)

    config.add_route("content_piece", "/content/{content_id}",
                     factory=resources.content_factory)
    config.add_view("web_api.views.ContentPieceResourceView",
                    route_name="content_piece",
                    attr="get",
                    request_method="GET",
                    renderer="json",
                    context=resources.ContentResource,
                    permission=VIEW)

    config.add_route("piece_authors", "/content/{content_id}/authors",
                     factory=resources.content_factory)
    config.add_view("web_api.views.ContentPieceResourceView",
                    route_name="piece_authors",
                    attr="get_authors",
                    request_method="GET",
                    renderer="json",
                    context=resources.ContentResource,
                    permission=VIEW)

    config.add_route("piece_edits", "/content/{content_id}/edits",
                     factory=resources.edit_factory)
    config.add_view("web_api.views.ContentPieceResourceView",
                    route_name="piece_edits",
                    attr="get_edits",
                    request_method="GET",
                    renderer="json",
                    context=resources.EditResource,
                    permission=VIEW)
    config.add_view("web_api.views.ContentPieceResourceView",
                    route_name="piece_edits",
                    attr="post_edit",
                    request_method="POST",
                    renderer="json",
                    context=resources.EditResource,
                    permission=CREATE,
                    require_csrf=True)

    config.add_route("piece_edit", "/content/{content_id}/edits/{edit_id}",
                     factory=resources.edit_factory)
    config.add_view("web_api.views.ContentPieceResourceView",
                    route_name="piece_edit",
                    attr="get_edit",
                    request_method="GET",
                    renderer="json",
                    context=resources.EditResource,
                    permission=VIEW)

    config.add_route("edit_vote", "/content/{content_id}/edits/{edit_id}/votes",
                     factory=resources.vote_factory)
    config.add_view("web_api.views.ContentPieceResourceView",
                    route_name="edit_vote",
                    attr="get_edit_vote",
                    request_method="GET",
                    renderer="json",
                    context=resources.VoteResource,
                    permission=VIEW)
    config.add_view("web_api.views.ContentPieceResourceView",
                    route_name="edit_vote",
                    attr="post_edit_vote",
                    request_method="POST",
                    renderer="json",
                    context=resources.VoteResource,
                    permission=CREATE,
                    require_csrf=True)

    config.add_route("piece_edit_activity", "/content/{content_id}/edit_activity",
                     factory=resources.content_factory)
    config.add_view("web_api.views.ContentPieceResourceView",
                    route_name="piece_edit_activity",
                    attr="get_edit_activity",
                    request_method="GET",
                    renderer="json",
                    context=resources.ContentResource,
                    permission=AUTHOR)

    config.add_route("content_names", "/content/names",
                     factory=resources.content_factory)
    config.add_view("web_api.views.ContentResourceView",
                    route_name="content_names",
                    attr="get_names",
                    request_method="GET",
                    renderer="json",
                    context=resources.ContentResource,
                    permission=VIEW)

    config.add_route("content_types", "/content/content_types",
                     factory=resources.content_factory)
    config.add_view("web_api.views.ContentResourceView",
                    route_name="content_types",
                    attr="get_content_types",
                    request_method="GET",
                    renderer="json",
                    context=resources.ContentResource,
                    permission=VIEW)

    config.add_route("content_keywords", "/content/keywords",
                     factory=resources.content_factory)
    config.add_view("web_api.views.ContentResourceView",
                    route_name="content_keywords",
                    attr="get_keywords",
                    request_method="GET",
                    renderer="json",
                    context=resources.ContentResource,
                    permission=VIEW)

    config.add_route("content_citations", "/content/citations",
                     factory=resources.content_factory)
    config.add_view("web_api.views.ContentResourceView",
                    route_name="content_citations",
                    attr="get_citations",
                    request_method="GET",
                    renderer="json",
                    context=resources.ContentResource,
                    permission=VIEW)

    config.add_route("users", "/users", factory=resources.user_factory)
    config.add_view("web_api.views.UserResourceView",
                    route_name="users",
                    attr="post",
                    request_method="POST",
                    renderer="json",
                    context=resources.UserResource,
                    permission=CREATE)
    config.add_view("web_api.views.UserResourceView",
                    route_name="users",
                    attr="patch",
                    request_method="PATCH",
                    renderer="json",
                    context=resources.UserResource,
                    permission=MODIFY,
                    require_csrf=True)
    config.add_view("web_api.views.UserResourceView",
                    route_name="users",
                    attr="delete",
                    request_method="DELETE",
                    renderer="json",
                    context=resources.UserResource,
                    permission=DELETE,
                    require_csrf=True)

    config.add_route("user_sessions", "/users/sessions",
                     factory=resources.user_factory)
    config.add_view("web_api.views.UserResourceView",
                    route_name="user_sessions",
                    attr="post_session",
                    request_method="POST",
                    renderer="json",
                    context=resources.UserResource,
                    permission=MODIFY,
                    require_csrf=True)
    config.add_view("web_api.views.UserResourceView",
                    route_name="user_sessions",
                    attr="delete_session",
                    request_method="DELETE",
                    renderer="json",
                    context=resources.UserResource,
                    permission=MODIFY,
                    require_csrf=True)

    config.add_route("user", "/users/{user_id}",
                     factory=resources.user_factory)
    config.add_view("web_api.views.UserResourceView",
                    route_name="user",
                    attr="get",
                    request_method="GET",
                    renderer="json",
                    context=resources.UserResource,
                    permission=VIEW)

    config.add_route("user_activity", "/users/{user_id}/recent_activity",
                     factory=resources.user_factory)
    config.add_view("web_api.views.UserResourceView",
                    route_name="user_activity",
                    attr="get_recent_activity",
                    request_method="GET",
                    renderer="json",
                    context=resources.UserResource,
                    permission=VIEW)

    config.add_route("user_content", "/users/{user_id}/content",
                     factory=resources.user_factory)
    config.add_view("web_api.views.UserResourceView",
                    route_name="user_content",
                    attr="get_content",
                    request_method="GET",
                    renderer="json",
                    context=resources.UserResource,
                    permission=VIEW)

    config.add_route("user_edits", "/users/{user_id}/edits",
                     factory=resources.user_factory)
    config.add_view("web_api.views.UserResourceView",
                    route_name="user_edits",
                    attr="get_edits",
                    request_method="GET",
                    renderer="json",
                    context=resources.UserResource,
                    permission=VIEW)

    config.add_route("admin", "/admins/{id}", factory=resources.admin_factory)
    config.add_view("web_api.views.UserResourceView",
                    route_name="user",
                    attr="get",
                    request_method="GET",
                    renderer="json",
                    context=resources.AdminResource,
                    permission=VIEW)

    config.add_route("reports", "/reports", factory=resources.report_factory)
    config.add_view("web_api.views.ReportResourceView",
                    route_name="reports",
                    attr="get",
                    request_method="GET",
                    renderer="json",
                    context=resources.ReportResource,
                    permission=VIEW)
    config.add_view("web_api.views.ReportResourceView",
                    route_name="reports",
                    attr="post",
                    request_method="POST",
                    renderer="json",
                    context=resources.ReportResource,
                    permission=CREATE)

    config.add_route("report", "/reports/{report_id}",
                     factory=resources.report_factory)
    config.add_view("web_api.views.ReportResourceView",
                    route_name="report",
                    attr="get_report",
                    request_method="GET",
                    renderer="json",
                    context=resources.ReportResource,
                    permission=VIEW)

    config.add_route("admin_reports", "/reports/{report_id}/admin_reports",
                     factory=resources.report_factory)
    config.add_view("web_api.views.ReportResourceView",
                    route_name="admin_reports",
                    attr="post_admin_report",
                    request_method="POST",
                    renderer="json",
                    context=resources.ReportResource,
                    permission=MODIFY,
                    require_csrf=True)

    return config.make_wsgi_app()
