from .conf import settings

from tornado.web import StaticFileHandler
from tornado.websocket import WebSocketHandler


class IndexStaticFileHandler(StaticFileHandler):
    def parse_url_path(self, url_path):
        if not url_path or url_path.endswith('/'):
            url_path += 'index.html'

        return super(IndexStaticFileHandler, self).parse_url_path(url_path)


class SimulatorHandler(WebSocketHandler):
    def open(self):
        Brainstem.instance().add_websocket_client(self)

    def check_origin(self, origin):
        if settings.DEBUG:
            return True
        else:
            return super().check_origin(origin)

    def on_message(self, message):
        pass

    def on_close(self):
        Brainstem.instance().remove_websocket_client(self)

# prevent circular references
from .brainstem import Brainstem
