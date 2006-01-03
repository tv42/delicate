# -*- python -*-
from twisted.application import service, internet
from twisted.python.components import registerAdapter
from nevow import appserver, inevow, rend
from delicate import ibookshelf, bookshelf
from delicate.delicious import fromdelicious
from delicate.web import view

application = service.Application("delicate")
myService = service.IServiceCollection(application)

shelf = fromdelicious.DeliciousBookmarkShelf(
    'delicate/delicious/test/export.html')

site = appserver.NevowSite(view.ViewResource(rootObject=shelf))

myServer = internet.TCPServer(8080, site)
myServer.setServiceParent(myService)
