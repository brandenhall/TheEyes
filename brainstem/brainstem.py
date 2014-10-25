import logging
import logging.config
import signal
import handlers
import requests
import time
import opc

from conf import settings
from eye import Eye
from creature import Creature
from clients import ReconnectingTCPClient

from multiprocessing.pool import ThreadPool

from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop, PeriodicCallback
from tornado.web import Application
from tornado import gen

logger = logging.getLogger(__name__)


class Brainstem():
    def __init__(self):
        logger.info("Initializing Brainstem...")
        logging.config.dictConfig(settings.LOGGING)
        signal.signal(signal.SIGTERM, self.sig_handler)
        signal.signal(signal.SIGINT, self.sig_handler)
        handlers.CortexHandler.brainstem = self
        handlers.SimulatorHandler.brainstem = self
        self.workers = ThreadPool(10)

    def start(self):
        logger.info("Starting Brainstem...")
        self.opc_client = opc.Client('localhost:7890')

        self.cortex_client = ReconnectingTCPClient('Brainstem')
        self.cortex_client.handler = handlers.CortexHandler

        self.simulation_clients = []
        self.creatures = []

        if settings.DEBUG:
            apps = [(r'/ws', handlers.SimulatorHandler), ]
            apps.append((r'/(.*)',
                        handlers.IndexStaticFileHandler,
                        {'path': settings.WEBROOT}))
            application = Application(apps)
            self.http_server = HTTPServer(application)
            self.http_server.listen(settings.HTTP_PORT)

        self.updater = PeriodicCallback(self.update, 1000/settings.FRAMERATE)
        self.load_content()

        self.cortex_client.connect(settings.CORTEX_HOST, settings.CORTEX_PORT)

        IOLoop.instance().start()

    def load_content(self):
        # first, load the eye data
        self.updater.stop()
        self.clear()
        self.eyes = []
        for i in range(settings.EYE_COUNT):
            self.eyes.append(Eye(self.pixels, i * settings.PIXELS_PER_EYE))

        for index, eye in enumerate(self.eyes):
            eye.set_pixels(settings.NUMBERS[index])

        # two blits to prevent interpolation
        self.blit()
        self.blit()

        r = requests.get(settings.CMS_API_URL + "eyes/")

        if r.status_code == 200:
            try:
                data = r.json()
                for index, row in enumerate(data):
                    self.eyes[index].id = row['number']
                    self.eyes[index].preferences = row['preferences']

            except ValueError:
                logger.error("Can not parse eye data. Well shit.")
        else:
            logger.error("Can not load the eye data, crap.")

        logger.info("Eye data loaded from CMS.")

        # then load the creatures
        self.creatures = []
        self.responses = {}
        r = requests.get(settings.CMS_API_URL + "creatures/")

        if r.status_code == 200:
            try:
                data = r.json()
                for row in data:
                    creature = Creature()
                    creature.eyes = self.eyes
                    creature.name = row['name']
                    creature.circadian_offset = row['circadian_offset']
                    creature.circadian_period = row['circadian_period']
                    creature.restlessness = row['restlessness']
                    creature.minimum_speed = row['minimum_speed']
                    creature.maximum_speed = row['maximum_speed']
                    creature.minimum_blink = row['minimum_blink']
                    creature.maximum_blink = row['maximum_blink']
                    creature.sclera_color = (
                        int(row['sclera_color'][0:2], 16),
                        int(row['sclera_color'][2:4], 16),
                        int(row['sclera_color'][4:6], 16)
                    )
                    creature.lid_color = (
                        int(row['lid_color'][0:2], 16),
                        int(row['lid_color'][2:4], 16),
                        int(row['lid_color'][4:6], 16)
                    )

                    # list comprehensions - WHAT MOTHERFUCKER!?!
                    creature.default = [
                        (int(x[0:2], 16),
                         int(x[2:4], 16),
                         int(x[4:6], 16)) for x in row['eye'][0]
                    ]

                    for question in row['questions']:
                        for response in question['responses']:
                            self.responses[response['id']] = creature
                            frames = [
                                [(int(y[0:2], 16),
                                  int(y[2:4], 16),
                                  int(y[4:6], 16)) for y in x] for x in response['animation']
                            ]
                            creature.responses[response['id']] = frames
                            logger.info('Loaded "{}" animation with {} frames'.format(creature.name, len(frames)))

                    logger.info('Finished adding creature "{}"'.format(creature.name))
                    self.creatures.append(creature)

            except ValueError:
                logger.error("Can not parse eye data. Well shit.")
        else:
            logger.error("Can not load the creature data. Bollocks.")

        logger.info('Creature data loaded from CMS')

        self.test_pattern()

    @gen.engine
    def test_pattern(self):
        colors = ((255, 0, 0),
                  (0, 255, 0),
                  (0, 0, 255),
                  (255, 255, 0),
                  (255, 0, 255),
                  (0, 255, 255),
                  (255, 255, 255),
                  (0, 0, 0))

        for color in colors:
            for i in range(settings.PIXEL_COUNT):
                self.pixels[i] = color
            # two blits to prevent interpolation
            self.blit()
            self.blit()
            yield gen.Task(IOLoop.instance().add_timeout, time.time() + 1)

        self.updater.start()

    def update(self):
        t = time.time() / 60
        for creature in self.creatures:
            creature.update(t)
        self.blit()

    def blit(self):
        self.workers.apply_async(self.blit_async)

    def blit_async(self):
        """Draw and update all creatures"""

        if len(self.simulation_clients) > 0:
            data = bytes()

            for i in range(settings.EYE_COUNT):
                data += self.encode(i)

            for client in self.simulation_clients:
                client.write_message(data, True)

        self.opc_client.put_pixels(self.pixels)

    def encode(self, index):
        count = 0
        palette = {}
        pbn = []
        output = bytearray()
        output.append(0)

        # simple palette based compression
        for i in range(settings.PIXELS_PER_EYE):
            pixel = self.pixels[(index * settings.PIXELS_PER_EYE) + i]
            color = pixel[0] << 16 | pixel[1] << 8 | pixel[2]
            if color not in palette:
                palette[color] = count
                pbn.append(count)
                output.extend(pixel)
                count += 1
            else:
                pbn.append(palette[color])

        output[0] = len(palette)

        for p in pbn:
            output.append(p)

        return bytes(output)

    def add_simulation_client(self, client):
        logger.info('Simulation client connected')
        self.simulation_clients.append(client)

    def remove_simulation_client(self, client):
        logger.info('Simulation client disconnected')
        self.simulation_clients.remove(client)

    def add_cortex_client(self, client):
        self.cortex = client

    def remove_cortex_client(self, client):
        if self.cortex == client:
            self.cortex = None

    def clear(self):
        self.pixels = [(0, 0, 0)] * settings.PIXEL_COUNT
        self.blit()
        self.blit()

    def on_cortex_command(self, command):
        if 'type' in command:
            if command['type'] == 'set_color':
                color = command['color']
                for i in range(settings.PIXEL_COUNT):
                    self.pixels[i] = color

    def sig_handler(self, sig, frame):
        logger.warning('Caught signal: %s', sig)
        IOLoop.instance().add_callback(self.shutdown)

    def shutdown(self):
        logger.info('Stopping Brainstem...')
        try:
            self.updater.stop()
            self.clear()

        except Exception as err:
            logger.error("Could not close servers gracfully. {}".format(err))

        finally:
            IOLoop.instance().stop()
            logger.info('Shutdown')

if __name__ == "__main__":
    brainstem = Brainstem()
    brainstem.start()
