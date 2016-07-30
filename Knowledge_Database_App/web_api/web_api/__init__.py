"""
Contains the server start-up code and URL dispatch definitions.

Functions:

    main
"""

from pyramid.config import Configurator
from pyramid.authentication import SessionAuthenticationPolicy
from pyramid.authorization import ACLAuthorizationPolicy
from web_api.resources import get_root


def main(global_config, **settings):
    """
    This function returns a WSGI application.
    
    It is usually called by the PasteDeploy framework during 
    ``paster serve``.
    """
    settings.setdefault("jinja2.i18n.domain", "web_api")

    authentication_policy = SessionAuthenticationPolicy()
    authorization_policy = ACLAuthorizationPolicy()

    config = Configurator(root_factory=get_root, settings=settings)
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

    config.add_route("content", "/content")
    config.add_view("web_api.views.ContentResourceView",
                    route_name="content",
                    attr="get",
                    request_method="GET",
                    renderer="json")
    config.add_view("web_api.views.ContentResourceView",
                    route_name="content",
                    attr="post",
                    request_method="POST",
                    renderer="json")

    config.add_route("content_piece", "/content/{content_id}")
    config.add_view("web_api.views.ContentPieceResourceView",
                    route_name="content_piece",
                    attr="get",
                    request_method="GET",
                    renderer="json")

    config.add_route("piece_authors", "/content/{content_id}/authors")
    config.add_view("web_api.views.ContentPieceResourceView",
                    route_name="piece_authors",
                    attr="get_authors",
                    request_method="GET",
                    renderer="json")

    config.add_route("piece_edits", "/content/{content_id}/edits")
    config.add_view("web_api.views.ContentPieceResourceView",
                    route_name="piece_edits",
                    attr="get_edits",
                    request_method="GET",
                    renderer="json")

    config.add_route("piece_edit", "/content/{content_id}/edits/{edit_id}")
    config.add_view("web_api.views.ContentPieceResourceView",
                    route_name="piece_edit",
                    attr="get_edit",
                    request_method="GET",
                    renderer="json")

    config.add_route("edit_vote", "/content/{content_id}/edits/{edit_id}/votes")
    config.add_view("web_api.views.ContentPieceResourceView",
                    route_name="edit_vote",
                    attr="get_edit_vote",
                    request_method="GET",
                    renderer="json")
    config.add_view("web_api.views.ContentPieceResourceView",
                    route_name="edit_vote",
                    attr="post_edit_vote",
                    request_method="POST",
                    renderer="json")

    config.add_route("piece_edit_activity", "/content/{content_id}/edit_activity")
    config.add_view("web_api.views.ContentPieceResourceView",
                    route_name="piece_edit_activity",
                    attr="get_edit_activity",
                    request_method="GET",
                    renderer="json")

    config.add_route("content_names", "/content/names")
    config.add_view("web_api.views.ContentResourceView",
                    route_name="content_names",
                    attr="get_names",
                    request_method="GET",
                    renderer="json")

    config.add_route("content_types", "/content/content_types")
    config.add_view("web_api.views.ContentResourceView",
                    route_name="content_types",
                    attr="get_content_types",
                    request_method="GET",
                    renderer="json")

    config.add_route("content_keywords", "/content/keywords")
    config.add_view("web_api.views.ContentResourceView",
                    route_name="content_keywords",
                    attr="get_keywords",
                    request_method="GET",
                    renderer="json")

    config.add_route("content_citations", "/content/citations")
    config.add_view("web_api.views.ContentResourceView",
                    route_name="content_citations",
                    attr="get_citations",
                    request_method="GET",
                    renderer="json")

    config.add_route("users", "/users")
    config.add_view("web_api.views.UserResourceView",
                    route_name="users",
                    attr="post",
                    request_method="POST",
                    renderer="json")
    config.add_view("web_api.views.UserResourceView",
                    route_name="users",
                    attr="patch",
                    request_method="PATCH",
                    renderer="json")
    config.add_view("web_api.views.UserResourceView",
                    route_name="users",
                    attr="delete",
                    request_method="DELETE",
                    renderer="json")

    config.add_route("user_sessions", "/users/sessions")
    config.add_view("web_api.views.UserResourceView",
                    route_name="user_sessions",
                    attr="post_session",
                    request_method="POST",
                    renderer="json")
    config.add_view("web_api.views.UserResourceView",
                    route_name="user_sessions",
                    attr="delete_session",
                    request_method="DELETE",
                    renderer="json")

    config.add_route("user", "/users/{user_id}")
    config.add_view("web_api.views.UserResourceView",
                    route_name="user",
                    attr="get",
                    request_method="GET",
                    renderer="json")

    config.add_route("user_activity", "/users/{user_id}/recent_activity")
    config.add_view("web_api.views.UserResourceView",
                    route_name="user_activity",
                    attr="get_recent_activity",
                    request_method="GET",
                    renderer="json")

    config.add_route("user_content", "/users/{user_id}/content")
    config.add_view("web_api.views.UserResourceView",
                    route_name="user_content",
                    attr="get_content",
                    request_method="GET",
                    renderer="json")

    config.add_route("user_edits", "/users/{user_id}/edits")
    config.add_view("web_api.views.UserResourceView",
                    route_name="user_edits",
                    attr="get_edits",
                    request_method="GET",
                    renderer="json")

    config.add_route("admin", "/admins/{id}")
    config.add_view("web_api.views.UserResourceView",
                    route_name="user",
                    attr="get",
                    request_method="GET",
                    renderer="json")

    config.add_route("reports", "/reports")
    config.add_view("web_api.views.ReportResourceView",
                    route_name="reports",
                    attr="get",
                    request_method="GET",
                    renderer="json")
    config.add_view("web_api.views.ReportResourceView",
                    route_name="reports",
                    attr="post",
                    request_method="POST",
                    renderer="json")

    config.add_route("report", "/reports/{report_id}")
    config.add_view("web_api.views.ReportResourceView",
                    route_name="report",
                    attr="get_report",
                    request_method="GET",
                    renderer="json")

    config.add_route("admin_reports", "/reports/{report_id}/admin_reports")
    config.add_view("web_api.views.ReportResourceView",
                    route_name="admin_reports",
                    attr="post_admin_report",
                    request_method="POST",
                    renderer="json")

    return config.make_wsgi_app()
