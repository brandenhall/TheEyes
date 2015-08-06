import glob
import json
import logging
import logging.config
import signal
import random
import time
import opc

from conf import settings
from eye import Eye
from creature import Creature

from multiprocessing.pool import ThreadPool

from tornado.ioloop import IOLoop, PeriodicCallback
from tornado import gen

logger = logging.getLogger(__name__)


class Brainstem():
    def __init__(self):
        logging.config.dictConfig(settings.LOGGING)

        logger.info("Initializing Brainstem...")

        signal.signal(signal.SIGTERM, self.sig_handler)
        signal.signal(signal.SIGINT, self.sig_handler)

        self.workers = ThreadPool(10)
        self.wakeup_exclude_frames = 0
        self.start_time = time.time() / 60

    def start(self):
        logger.info("Starting Brainstem...")

        self.opc_client = opc.Client('localhost:7890')

        self.simulation_clients = []
        self.creatures = []
        self.creature_table = {}

        self.updater = PeriodicCallback(self.update, 1000/settings.FRAMERATE)
        self.load_content()

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

        # then load the creatures
        self.creatures = []
        self.responses = {}

        try:
            creature_files = glob.glob('data/creatures/*.json')

            for creature_file in creature_files:
                with open(creature_file) as f:
                    data = json.loads(f.read())

                    creature = Creature()
                    creature.brainstem = self
                    creature.eyes = self.eyes
                    creature.current_eyes = self.eyes
                    creature.name = data['name']
                    creature.lifespan = data['lifespan']
                    creature.restlessness = data['restlessness']
                    creature.minimum_blink = data['minimum_blink']
                    creature.maximum_blink = data['maximum_blink']
                    creature.sclera_color = (
                        int(data['sclera_color'][0:2], 16),
                        int(data['sclera_color'][2:4], 16),
                        int(data['sclera_color'][4:6], 16)
                    )
                    creature.lid_color = (
                        int(data['lid_color'][0:2], 16),
                        int(data['lid_color'][2:4], 16),
                        int(data['lid_color'][4:6], 16)
                    )

                    creature.default = [
                        (int(x[0:2], 16),
                         int(x[2:4], 16),
                         int(x[4:6], 16)) for x in data['eye'][0]
                    ]
                    creature.layer = [
                        (int(x[0:2], 16),
                         int(x[2:4], 16),
                         int(x[4:6], 16)) for x in data['overlay'][0]
                    ]
                    creature.is_overlay = data['is_overlay']
                    creature.pupil_mask = [x == "000000" for x in data['pupil_mask'][0]]
                    creature.current = creature.default[:]

                    self.creatures.append(creature)

                    logger.info('Loaded info for creature "{}"'.format(creature.name))

        except ValueError:
            logger.error("Can not parse eye data. Well shit.")

        logger.info('Creature data loaded from filesystem')

        self.test_pattern()

    @gen.engine
    def test_pattern(self):
        logger.info('Showing test pattern')
        patterns = (
            {'name': 'red', 'color': (255, 0, 0)},
            {'name': 'green', 'color': (0, 255, 0)},
            {'name': 'blue', 'color': (0, 0, 255)},
            {'name': 'yellow', 'color': (255, 255, 0)},
            {'name': 'magenta', 'color': (255, 0, 255)},
            {'name': 'cyan', 'color': (0, 255, 255)},
            {'name': 'white', 'color': (255, 255, 255)},
            {'name': 'black', 'color': (0, 0, 0)},
        )

        if settings.TEST_PATTERN_ENABLED:
            for pattern in patterns:
                logger.info('Now showing {}...'.format(pattern['name']))
                for i in range(settings.PIXEL_COUNT):
                    self.pixels[i] = pattern['color']
                # two blits to prevent interpolation
                self.blit()
                self.blit()
                yield gen.Task(IOLoop.instance().add_timeout, time.time() + 1)

        self.updater.start()

    def wake_creature(self, last_one):
        creature = random.choice(self.creatures)
        logger.info('Now waking creature "{}"'.format(creature.name))

        creature.wakeup()

    def update(self):
        one_awake = False
        t = time.time() / 60

        for creature in self.creatures:
            creature.update(t - self.start_time)
            if creature.is_awake:
                one_awake = True

        if not one_awake:
            self.wake_creature(None)

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

    def clear(self):
        self.pixels = [(0, 0, 0)] * settings.PIXEL_COUNT
        self.blit()
        self.blit()

    def sig_handler(self, sig, frame):
        logger.warning('Caught signal: %s', sig)
        IOLoop.instance().add_callback(self.shutdown)

    def shutdown(self):
        logger.info('Stopping Brainstem...')
        try:
            self.clear()

        except Exception as err:
            logger.error("Could not close servers gracfully. {}".format(err))

        finally:
            IOLoop.instance().stop()
            logger.info('Shutdown')

if __name__ == "__main__":
    brainstem = Brainstem()
    brainstem.start()
