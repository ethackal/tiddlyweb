
import urllib

from tiddlyweb.bag import Bag
from tiddlyweb.store import Store
from tiddlyweb.serializer import Serializer
from tiddlyweb import control
from tiddlyweb import web
from tiddlyweb.web.http import HTTP404

# XXX the store should be in the environ!

serializers = {
        'text/html': ['html', 'text/html'],
        'text/plain': ['text', 'text/plain'],
        'default': ['html', 'text/html'],
        }

def list(environ, start_response):
    store = environ['tiddlyweb.store']
    bags = store.list_bags()

    start_response("200 OK",
            [('Content-Type', 'text/plain')])

    return [ '%s\n' % bag.name for bag in bags]

def get_tiddlers(environ, start_response):
    filter_string = urllib.unquote(environ['QUERY_STRING'])

    bag_name = environ['wsgiorg.routing_args'][1]['bag_name']
    bag = Bag(bag_name)

    store = environ['tiddlyweb.store']

    try:
        store.get(bag)
    except NoBagError, e:
        raise HTTP404, '%s not found, %s' % (bag.name, e)

    tiddlers = control.filter_tiddlers_from_bag(bag, filter_string)
    tmp_bag = Bag('tmp_bag')
    for tiddler in tiddlers:
        tmp_bag.add_tiddler(tiddler)

    serialize_type, mime_type = web.get_serialize_type(environ, serializers)
    serializer = Serializer(tmp_bag, serialize_type)

    start_response("200 OK", [('Content-Type', mime_type)])
    return [serializer.to_string()]