import logging
import logging.config
import math
import signal
import threading
import uuid

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
        self.requests = {}
        self.geolocation_required = False

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

    def check_geolocation(self, lat, lon):
        a = settings.GEOLOCATION_POSITION
        b = (lat, lon)

        a = (math.radians(a[0]), math.radians(a[1]))
        b = (math.radians(b[0]), math.radians(b[1]))
        dlon = b[1] - a[1]
        dlat = b[0] - a[0]
        a = (math.sin(dlat/2))**2 + math.cos(a[0]) * math.cos(b[0]) * (math.sin(dlon/2))**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))

        return (c * 3961) <= settings.GEOLOCATION_MAX_DISTANCE

    def on_interaction_command(self, client, command):

        if 'type' in command:

            allowed = True

            # handle geolocation
            if settings.GEOLOCATION_REQUIRED:
                if 'lat' in command and 'lon' in command:
                    if not self.check_geolocation(command['lat'], command['lon']):
                        allowed = False
                else:
                    allowed = False

            if not allowed:
                result = {}
                result['type'] = 'not_allowed'

                client.send(result)

                return


            if command['type'] == 'set_color':
                if self.brainstem is not None:
                    self.brainstem.send(command)

            if command['type'] == 'get_question':
                if client.last_request_id and client.last_request_id in self.requests:
                    del self.requests[client.last_request_id]

                client.last_request_id = str(uuid.uuid4())
                self.requests[client.last_request_id] = client

                request = {}
                request['type'] = 'get_question'
                request['request_id'] = client.last_request_id
                if self.brainstem is not None:
                    self.brainstem.send(request)
                else:
                    result = {}
                    result['type'] = 'not_available'
                    client.send(result)

            if command['type'] == 'respond' and 'creature_id' in command and 'response_id' in command:
                if client.last_request_id and client.last_request_id in self.requests:
                    del self.requests[client.last_request_id]

                client.last_request_id = str(uuid.uuid4())
                self.requests[client.last_request_id] = client

                request = {}
                request['type'] = 'respond'
                request['request_id'] = client.last_request_id
                request['creature_id'] = command['creature_id']
                request['response_id'] = command['response_id']
                if self.brainstem is not None:
                    self.brainstem.send(request)
                else:
                    result = {}
                    result['type'] = 'not_available'
                    client.send(result)

    def on_brainstem_command(self, command):
        if 'type' in command:
            if command['type'] == 'question':
                request_id = command['request_id']

                if request_id in self.requests:
                    client = self.requests[request_id]
                    del self.requests[request_id]
                    if request_id == client.last_request_id:
                        client.last_request_id = None
                        client.send(command)

            if command['type'] == 'fell_asleep':
                request_id = command['request_id']

                if request_id in self.requests:
                    client = self.requests[request_id]
                    del self.requests[request_id]
                    if request_id == client.last_request_id:
                        client.last_request_id = None

                        result = {}
                        result['type'] = 'fell_asleep'
                        client.send(result)

            if command['type'] == 'none_awake':
                request_id = command['request_id']

                if request_id in self.requests:
                    client = self.requests[request_id]
                    del self.requests[request_id]
                    if request_id == client.last_request_id:
                        client.last_request_id = None

                        result = {}
                        result['type'] = 'none_awake'
                        client.send(result)

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
