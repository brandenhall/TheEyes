import logging
import logging.config
import signal
import handlers
import random
import requests
import time
import opc

from conf import settings
from eye import Eye
from hero import HeroManager
from creature import Creature, CreatureQuestion, CreatureResponse
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
        self.wakeup_exclude_frames = 0
        self.start_time = time.time() / 60

    def start(self):
        logger.info("Starting Brainstem...")
        self.opc_client = opc.Client('localhost:7890')

        self.cortex_client = ReconnectingTCPClient('Brainstem')
        self.cortex_client.handler = handlers.CortexHandler

        self.simulation_clients = []
        self.creatures = []
        self.creature_table = {}

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

        if settings.CORTEX_ENABLED:
            self.heartbeat = PeriodicCallback(self.send_heartbeat, settings.CORTEX_HEARTBEAT)
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
                    creature.id = row['id']
                    creature.eyes = self.eyes
                    creature.name = row['name']
                    creature.image = '/media' + row['image'][1:]
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

                    creature.default = [
                        (int(x[0:2], 16),
                         int(x[2:4], 16),
                         int(x[4:6], 16)) for x in row['eye'][0]
                    ]
                    creature.layer = [
                        (int(x[0:2], 16),
                         int(x[2:4], 16),
                         int(x[4:6], 16)) for x in row['overlay'][0]
                    ]
                    creature.is_overlay = row['is_overlay']
                    creature.pupil_mask = [x == "000000" for x in row['pupil_mask'][0]]

                    for question in row['questions']:
                        if question['enabled']:
                            q = CreatureQuestion()
                            q.question = question['question']
                            for response in question['responses']:
                                r = CreatureResponse()
                                r.id = response['id']
                                r.response = response['response']
                                self.responses[response['id']] = creature
                                r.animation = [
                                    [(int(y[0:2], 16),
                                      int(y[2:4], 16),
                                      int(y[4:6], 16)) for y in x] for x in response['animation']
                                ]
                                r.loops = response['loops']
                                creature.responses[response['id']] = r
                                q.responses.append(r)

                            creature.questions.append(q)

                    logger.info('Finished adding creature "{}"'.format(creature.name))
                    self.creatures.append(creature)
                    self.creature_table[creature.id] = creature

            except ValueError:
                logger.error("Can not parse eye data. Well shit.")
        else:
            logger.error("Can not load the creature data. Bollocks.")

        logger.info('Creature data loaded from CMS')

        self.hero_manager = HeroManager(self.eyes)
        r = requests.get(settings.CMS_API_URL + "heroanimations/")

        if r.status_code == 200:
            try:
                data = r.json()
                for row in data:
                    self.hero_manager.add_animation([
                        [(int(y[0:2], 16),
                          int(y[2:4], 16),
                          int(y[4:6], 16)) for y in x] for x in row['animation']
                        ], row['loops'])

            except ValueError:
                logger.error("Can not hero data. Well shit.")

        else:
            logger.error("Can not load hero data. Bollocks.")

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
        self.workers.apply_async(self.update_async)

    def update_async(self):
        t = time.time() / 60
        if Creature.wakeup_exclude_frames > 0:
            Creature.wakeup_exclude_frames -= 1

        for creature in self.creatures:
            creature.update(t - self.start_time)

        self.hero_manager.update()
        self.blit()

    def blit(self):
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
        self.heartbeat.start()

    def remove_cortex_client(self, client):
        if self.cortex == client:
            self.cortex = None
            self.heartbeat.stop()

    def send_heartbeat(self):
        if self.cortex is not None:
            self.cortex.send({'type': 'heartbeat', 'time': time.time()})

    def clear(self):
        self.pixels = [(0, 0, 0)] * settings.PIXEL_COUNT
        self.blit()
        self.blit()

    def on_cortex_command(self, command):
        if 'type' in command:

            # set color for debugging
            if command['type'] == 'set_color':
                color = command['color']
                for i in range(settings.PIXEL_COUNT):
                    self.pixels[i] = color

            # get a question from an awake creature
            elif command['type'] == 'get_question' and 'request_id' in command:
                awake_creatures = [c for c in self.creatures if c.is_awake]
                if len(awake_creatures) > 0:
                    creature = random.choice(awake_creatures)
                    creature.start_listening()
                    question = random.choice(creature.questions)
                    random.shuffle(question.responses)
                    result = {}
                    result['type'] = 'question'
                    result['request_id'] = command['request_id']
                    result['creature'] = creature.name
                    result['creature_id'] = creature.id
                    result['image'] = creature.image
                    result['question'] = question.question
                    result['responses'] = []
                    for response in question.responses:
                        result['responses'].append({
                            'id': response.id,
                            'response': response.response})
                else:
                    result = {}
                    result['type'] = 'none_awake'
                    result['request_id'] = command['request_id']

                self.cortex.send(result)

            elif command['type'] == 'respond' and 'request_id' in command and 'creature_id' in command and 'response_id' in command:
                creature_id = command['creature_id']
                response_id = command['response_id']

                if creature_id in self.creature_table:
                    creature = self.creature_table[creature_id]
                    if creature.is_awake:
                        creature.respond(response_id)
                    else:
                        # what happens if the user takes too long and the creature falls asleep
                        result = {}
                        result['type'] = 'fell_asleep'
                        result['request_id'] = command['request_id']
                        self.cortex.send(result)

            elif command['type'] == 'heartbeat':
                pass
    def sig_handler(self, sig, frame):
        logger.warning('Caught signal: %s', sig)
        IOLoop.instance().add_callback(self.shutdown)

    def shutdown(self):
        logger.info('Stopping Brainstem...')
        try:
            self.updater.stop()
            self.heartbeat.stop()
            self.clear()

        except Exception as err:
            logger.error("Could not close servers gracfully. {}".format(err))

        finally:
            IOLoop.instance().stop()
            logger.info('Shutdown')

if __name__ == "__main__":
    brainstem = Brainstem()
    brainstem.start()
