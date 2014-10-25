import logging
import math
import random


from conf import settings


class Creature(object):

    def __init__(self):
        self.name = ''
        self.circadian_offset = 0
        self.circadian_period = 0
        self.restlessness = 0
        self.minimum_speed = 0
        self.maximum_speed = 1
        self.minimum_blink = 0
        self.maximum_blink = 1
        self.sclera_color = (0, 0, 0)
        self.lid_color = (0, 0, 0)
        self.default = []
        self.responses = {}
        self.eyes = []

        self.is_awake = False
        self.is_transitioning = False
        self.is_blinking = False
        self.is_tired = False
        self.is_responding = False

        self.frame = 0

        self.eye_alpha = None
        self.eye_beta = None

        self.blink_toggle = False
        self.blink_index = 0
        self.next_blink = 0

    def update(self, time):
        circ = (math.sin(time * (math.pi / self.circadian_period * 0.5))
                + self.circadian_offset)
        rate = 6 - ((1 + self.circadian_offset) / circ * 6)

        # wake up!
        if circ > 0 and not self.is_awake:
            self.position = 30
            self.blink_index = settings.BLINK_CLOSED_INDEX
            self.is_awake = True
            self.is_transitioning = True
            self.is_blinking = True

            # go find eyes!
            while self.eye_alpha is None:
                self.eye_alpha = random.choice(self.eyes)
                if not self.eye_alpha.available:
                    self.eye_alpha = None

            eye_index = 0
            while self.eye_beta is None:
                pref_index = self.eye_alpha.preferences[eye_index] - 1
                if self.eyes[pref_index].available:
                    self.eye_beta = self.eyes[pref_index]
                else:
                    eye_index += 1

            self.eye_alpha.available = False
            self.eye_beta.available = False

            logging.info("{} wakes up, selects eyes {} and {}".format(self.name, self.eye_alpha.id, self.eye_beta.id))

        if self.is_awake:

            # go to sleep at next blink
            if circ < 0:
                self.is_tired = True

            if self.frame >= rate:
                self.move()
                self.frame = 0

            self.draw_eyes()
            self.draw_lids()

            self.blink_toggle = not self.blink_toggle

            if self.blink_toggle:
                if self.is_blinking:
                    if self.is_tired:
                        self.is_transitioning = True
                    self.step_blink()
                else:
                    self.next_blink -= 1
                    if self.next_blink <= 0:
                        self.blink_index = 0
                        self.is_blinking = True

    def move(self):
        pass

    def draw_eyes(self):
        self.eye_alpha.set_pixels(self.default)
        self.eye_beta.set_pixels(self.default)

    def draw_lids(self):
        blink_pixels = settings.BLINK[self.blink_index]
        blink_color = (0, 0, 0)
        if not self.is_transitioning:
            blink_color = self.lid_color

        for i in range(settings.PIXELS_PER_EYE):
            self.eye_alpha[i] = self.eye_beta[i] = (
                (blink_color if blink_pixels[i] else None) or
                self.eye_alpha[i])

    def step_blink(self):
        self.blink_index += 1
        if self.is_tired and self.blink_index == settings.BLINK_CLOSED_INDEX + 1:
            self.blink_index = 0
            self.is_awake = False
            self.is_blinking = False
            self.is_transitioning = False
            self.eye_alpha.available = True
            self.eye_beta.available = True
            self.eye_alpha = None
            self.eye_beta = None

        if self.blink_index == len(settings.BLINK):
            self.blink_index = 0
            self.next_blink = random.randint(self.minimum_blink,
                                             self.maximum_blink)
            self.is_blinking = False
            self.is_transitioning = False
