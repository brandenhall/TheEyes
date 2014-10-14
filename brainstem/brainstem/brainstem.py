import logging
import logging.config
import signal
import threading

from .conf import settings
from .eye import Eye
from .handlers import IndexStaticFileHandler, SimulatorHandler

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.web import Application

logger = logging.getLogger(__name__)


class Brainstem():
    _instance_lock = threading.Lock()

    @staticmethod
    def instance():
        if not hasattr(Brainstem, "_instance"):
            with Brainstem._instance_lock:
                if not hasattr(Brainstem, "_instance"):
                    # New instance after double check
                    Brainstem._instance = Brainstem()
        return Brainstem._instance

    def __init__(self):
        logging.config.dictConfig(settings.LOGGING)
        signal.signal(signal.SIGTERM, self.sig_handler)
        signal.signal(signal.SIGINT, self.sig_handler)

        self.websocket_clients = []

        application = Application([
            (r'/ws', SimulatorHandler),
            (r'/(.*)', IndexStaticFileHandler, {'path': 'simulator'}),
        ])

        self.http_server = HTTPServer(application)

        self.eye = Eye()
        self.test = PeriodicCallback(self.send_preview, 2000)
        self.test.start()

    def start(self):
        logger.info("Starting Brainstem...")

        self.http_server.listen(settings.HTTP_PORT)
        IOLoop.instance().start()

    def send_preview(self):
        if len(self.websocket_clients) > 0:
            data = self.eye.encode()
            for client in self.websocket_clients:
                client.write_message(data, True)

    def add_websocket_client(self, client):
        logger.info('Websocket client connected')
        self.websocket_clients.append(client)

    def remove_websocket_client(self, client):
        logger.info('Websocket client disconnected')
        self.websocket_clients.remove(client)

    def sig_handler(self, sig, frame):
        logger.warning('Caught signal: %s', sig)
        IOLoop.instance().add_callback(self.shutdown)

    def shutdown(self):
        logger.info('Stopping Brainstem...')
        try:
            pass

        except Exception as err:
            logger.error("Could not close servers gracfully. {}".format(err))

        finally:
            IOLoop.instance().stop()
            logger.info('Shutdown')


if __name__ == "__main__":
    brainstem = Brainstem.instance()
    brainstem.start()
