import cgi

from pyramid.httpexceptions import HTTPFound
from pyramid.response import Response
from pyramid.view import view_config


# First view, available at http://localhost:6543/
@view_config(route_name="hello", renderer="hello_world.pt")
def hello_word(request):
	return dict(name=request.matchdict["name"])
