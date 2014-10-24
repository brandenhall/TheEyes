import logging
import logging.config
import signal
import threading

from .conf import settings
from .handlers import InteractionHandler, BrainstemHandler
from .servers import LineServer

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.web import Application

logger = logging.getLogger(__name__)


class Cortex():
    _instance_lock = threading.Lock()

    @staticmethod
    def instance():
        if not hasattr(Cortex, "_instance"):
            with Cortex._instance_lock:
                if not hasattr(Cortex, "_instance"):
                    # New instance after double check
                    Cortex._instance = Cortex()
        return Cortex._instance

    def __init__(self):
        logging.config.dictConfig(settings.LOGGING)
        signal.signal(signal.SIGTERM, self.sig_handler)
        signal.signal(signal.SIGINT, self.sig_handler)

        self.interaction_clients = []
        self.brainstem = None

        apps = [(r'/', InteractionHandler), ]

        application = Application(apps)

        self.http_server = HTTPServer(application)
        self.brainstem_server = LineServer()
        self.brainstem_server.handler = BrainstemHandler

    def start(self):
        logger.info("Starting Cortex...")

        self.http_server.listen(settings.HTTP_PORT)
        self.brainstem_server.listen(settings.BRAINSTEM_PORT)
        IOLoop.instance().start()

    def add_interaction_client(self, client):
        logger.info('Interaction client connected')
        self.interaction_clients.append(client)

    def remove_interaction_client(self, client):
        logger.info('Interaction client disconnected')
        self.interaction_clients.remove(client)

    def on_interaction_command(self, command):
        if 'type' in command:
            if command['type'] == 'set_color':
                if self.brainstem is not None:
                    self.brainstem.send(command)

    def add_brainstem_client(self, client):
        logger.info('Brainstem client connected')
        self.brainstem = client
        for client in self.interaction_clients:
            client.send_status()

    def remove_brainstem_client(self, client):
        logger.info('Brainstem client disconnected')
        if self.brainstem == client:
            self.brainstem = None

            for client in self.interaction_clients:
                client.send_status()

    def sig_handler(self, sig, frame):
        logger.warning('Caught signal: %s', sig)
        IOLoop.instance().add_callback(self.shutdown)

    def shutdown(self):
        logger.info('Stopping Cortex...')
        try:
            pass

        except Exception as err:
            logger.error("Could not close servers gracfully. {}".format(err))

        finally:
            IOLoop.instance().stop()
            logger.info('Shutdown')


if __name__ == "__main__":
    cortex = Cortex.instance()
    cortex.start()
