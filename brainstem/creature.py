import logging
import math
import random

from conf import settings


class CreatureResponse(object):
    def __init__(self):
        self.id = None
        self.response = None
        self.animation = []
        self.loops = 1


class CreatureQuestion(object):
    def __init__(self):
        self.question = None
        self.responses = []


class Creature(object):
    wakeup_exclude_frames = 0

    def __init__(self):
        self.name = ''
        self.circadian_offset = 0
        self.circadian_period = 0
        self.restlessness = 0
        self.minimum_speed = 0
        self.maximum_speed = 1
        self.minimum_blink = 0
        self.maximum_blink = 1
        self.image = None
        self.sclera_color = (0, 0, 0)
        self.lid_color = (0, 0, 0)
        self.default = []
        self.overlay = []
        self.pupil_mask = []
        self.current = []
        self.questions = []
        self.responses = {}
        self.eyes = []

        self.is_awake = False
        self.is_transitioning = False
        self.is_blinking = False
        self.is_tired = False
        self.is_responding = False

        self.frame = 0

        self.moves = []
        self.next_move = 0
        self.position = 31

        self.eye_alpha = None
        self.eye_beta = None

        self.blink_toggle = False
        self.blink_index = 0
        self.next_blink = 0

        self.is_responding = False
        self.response_frame = 0
        self.response_index = 0
        self.response_queue = []
        self.response_loops = 0

        self.listening_frame = 0

    def respond(self, response):
        if response in self.responses:
            if not self.is_responding:
                self.is_responding = True
                self.response_index = 0
                self.response_frame = 0
                self.response_loops = self.responses[response].loops
                self.response_animation = self.responses[response].animation
            else:
                self.response_queue.append(response)

    def start_listening(self):
        self.listening_frame = settings.LISTENING_FRAMES

    def update(self, elapsed):
        if self.listening_frame > 0:
            self.listening_frame -= 1

        # responding or just living
        if self.is_responding:
            if self.response_frame <= 0:
                self.response_frame = 3

                pixels = self.response_animation[self.response_index]
                self.eye_alpha.set_pixels(pixels)
                self.eye_beta.set_pixels(pixels)
                self.response_index += 1

                if self.response_index == len(self.response_animation):
                    self.response_loops -= 1

                    if self.response_loops == 0:
                        self.is_responding = False
                        self.response_frame = 0
                        self.response_index = 0
                        self.response_animation = None

                        if len(self.response_queue) > 0:
                            self.respond(self.response_queue.pop(0))
                    else:
                        self.response_index = 0

            else:
                self.response_frame -= 1

        else:
            circ = (math.sin(elapsed * (math.pi / self.circadian_period * 0.5))
                    + self.circadian_offset)
            rate = 6 - ((1 + self.circadian_offset) / circ * 6)

            # wake up!
            if circ > 0 and not self.is_awake and Creature.wakeup_exclude_frames == 0:
                # go find eyes!
                tries = 0
                while self.eye_alpha is None and tries < settings.EYE_COUNT * 2:
                    tries += 1
                    self.eye_alpha = random.choice(self.eyes)
                    if not self.eye_alpha.available:
                        self.eye_alpha = None

                # if we have one eye, go get another
                if self.eye_alpha is not None:
                    eye_index = 0
                    tries = 0
                    while self.eye_beta is None and tries < settings.EYE_COUNT * 2:
                        tries += 1
                        pref_index = self.eye_alpha.preferences[eye_index] - 1
                        if self.eyes[pref_index].available:
                            self.eye_beta = self.eyes[pref_index]
                        else:
                            eye_index += 1

                    if self.eye_beta is not None:
                        self.eye_alpha.available = False
                        self.eye_beta.available = False
                        self.position = 31
                        self.blink_index = settings.BLINK_CLOSED_INDEX
                        self.is_awake = True
                        self.is_transitioning = True
                        self.is_blinking = True
                        self.current = self.default[:]

                        Creature.wakeup_exclude_frames = random.randint(
                            settings.WAKEUP_EXCLUDE_MIN_FRAMES,
                            settings.WAKEUP_EXCLUDE_MAX_FRAMES)

                        logging.info("{} wakes up, selects eyes {} and {}".format(self.name, self.eye_alpha.id, self.eye_beta.id))

            if self.is_awake:

                # go to sleep at next blink
                if circ < 0 and self.listening_frame == 0:
                    self.is_tired = True

                if self.frame >= rate:
                    self.move()
                    self.frame = 0

                self.draw_eyes()
                self.draw_overlay()
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
        if random.random() <= self.restlessness:
            next_pos = None
            while next_pos is None:
                next_pos = random.choice(settings.CELL_NEIGHBORS[self.position])

                # apply pupil mask
                if next_pos is not None and not self.pupil_mask[next_pos]:
                    next_pos = None

            self.position = next_pos

            tracking = self.position
            cells = [self.position, ]
            while tracking != 31:
                tracking = settings.CELL_PATHS[tracking]
                cells.append(tracking)

            cells.reverse()
            last_cell = cells.pop(0)

            moves = []
            while len(cells) > 0:
                cell = cells.pop(0)
                moves.append(settings.CELL_NEIGHBORS[last_cell].index(cell))
                last_cell = cell

            self.current = self.default[:]

            for move in moves:
                next_pixels = [None] * settings.PIXELS_PER_EYE
                for index in range(settings.PIXELS_PER_EYE):
                    neighbor = settings.CELL_NEIGHBORS[index][move]
                    if neighbor is None:
                        next_pixels[index] = self.sclera_color
                    else:
                        next_pixels[index] = self.current[neighbor]
                self.current = next_pixels

    def draw_eyes(self):
        self.eye_alpha.set_pixels(self.current)
        self.eye_beta.set_pixels(self.current)

    def draw_overlay(self):
        for i in range(settings.PIXELS_PER_EYE):
            if self.overlay[i] != (255, 255, 255):
                self.eye_alpha[i] = self.eye_beta[i] = self.overlay[i]

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
            self.is_tired = False
            self.is_awake = False
            self.is_blinking = False
            self.is_transitioning = False
            self.eye_alpha.available = True
            self.eye_beta.available = True
            self.eye_alpha = None
            self.eye_beta = None
            logging.info("{} goes to sleep".format(self.name))

        if self.blink_index == len(settings.BLINK):
            self.blink_index = 0
            self.next_blink = random.randint(self.minimum_blink,
                                             self.maximum_blink)
            self.is_blinking = False
            self.is_transitioning = False
