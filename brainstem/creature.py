import logging
import math
import random

from conf import settings
from utils import weighted_choice


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
        self.layer = []
        self.is_overlay = False
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

        self.current_eyes = []

        self.blink_toggle = False
        self.blink_index = 0
        self.next_blink = 0

        self.is_responding = False
        self.response_frame = 0
        self.response_index = 0
        self.response_queue = []
        self.response_loops = 0
        self.is_flashing = False
        self.flash_frame = 0
        self.flash_count = 0

        self.listening_frame = 0

    def respond(self, response):
        if response in self.responses:
            if not self.is_responding:
                self.is_responding = True
                self.response_index = 0
                self.response_frame = 0
                self.is_flashing = True
                self.flash_frame = 0
                self.flash_count = 0
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

                if self.is_flashing:
                    if self.flash_frame <= 0:
                        self.flash_frame = 3
                        self.flash_count += 1
                        if self.flash_count == settings.FLASH_COUNT:
                            self.is_flashing = False
                        pixels = [settings.FLASH_COLOR] * settings.PIXELS_PER_EYE
                        for e in self.current_eyes:
                            e.set_pixels(pixels)
                    else:
                        self.current = self.default[:]
                        self.draw_eyes()

                    self.flash_frame -= 1

                else:
                    pixels = self.response_animation[self.response_index]

                    for e in self.current_eyes:
                        e.set_pixels(pixels)

                    self.response_index += 1

                    if self.response_index == len(self.response_animation):
                        self.response_loops -= 1
                        self.response_index = 0

                        if self.response_loops == 0:
                            self.is_responding = False
                            self.response_frame = 0
                            self.response_index = 0
                            self.response_animation = None

                            if len(self.response_queue) > 0:
                                self.respond(self.response_queue.pop(0))

            else:
                self.response_frame -= 1

        else:
            circ = (math.sin(elapsed * (math.pi / self.circadian_period * 0.5))
                    + self.circadian_offset)
            rate = 6 - ((1 + self.circadian_offset) / circ * 6)

            # wake up!
            if circ > 0 and not self.is_awake and Creature.wakeup_exclude_frames == 0:

                num_eyes = weighted_choice(settings.CREATURE_EYE_WEIGHTS)

                self.current_eyes = [None] * num_eyes
                eye_index = 1
                tries = 0
                first_eye = None
                while first_eye is None and tries < settings.EYE_COUNT * 2:
                    tries += 1
                    first_eye = random.choice(self.eyes)
                    if not first_eye.available:
                        first_eye = None

                if first_eye is None:
                    self.current_eyes = []
                    return

                self.current_eyes[0] = first_eye

                for i in range(1, num_eyes):
                    next_eye = None
                    tries = 0
                    eye_index = 0
                    while next_eye is None and tries < settings.EYE_COUNT * 2 and eye_index < len(first_eye.preferences):
                        pref_index = first_eye.preferences[eye_index] - 1
                        next_eye = self.eyes[pref_index]
                        if not next_eye.available or next_eye in self.current_eyes:
                            next_eye = None
                            eye_index += 1

                    self.current_eyes[i] = next_eye
                    if next_eye is None:
                        self.current_eyes = []
                        return

                for e in self.current_eyes:
                    e.available = False

                self.position = 31
                self.blink_index = settings.BLINK_CLOSED_INDEX
                self.is_awake = True
                self.is_transitioning = True
                self.is_blinking = True
                self.current = self.default[:]

                Creature.wakeup_exclude_frames = random.randint(
                    settings.WAKEUP_EXCLUDE_MIN_FRAMES,
                    settings.WAKEUP_EXCLUDE_MAX_FRAMES)

#                logging.info("{} wakes up, selects {} eyes".format(self.name, len(self.current_eyes)))

            if self.is_awake:

                # go to sleep at next blink
                if circ < 0 and self.listening_frame == 0:
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
        if random.random() <= self.restlessness:
            next_pos = None
            while next_pos is None:
                next_pos = random.choice(settings.CELL_NEIGHBORS[self.position])

                # apply pupil mask
                if next_pos is None or not self.pupil_mask[next_pos]:
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
                    neighbor = settings.CELL_NEIGHBORS[index][(move + 3) % 6]
                    if neighbor is None:
                        next_pixels[index] = self.sclera_color
                    else:
                        next_pixels[index] = self.current[neighbor]
                self.current = next_pixels

    def draw_eyes(self):
        if self.is_overlay:
            for e in self.current_eyes:
                e.set_pixels(self.current)

            for i in range(settings.PIXELS_PER_EYE):
                if self.layer[i] != (255, 255, 255):
                    pixel = self.layer[i]
                    for e in self.current_eyes:
                        e[i] = pixel
        else:
            for e in self.current_eyes:
                e.set_pixels(self.layer)

            for i in range(settings.PIXELS_PER_EYE):
                if self.current[i] != (255, 255, 255):
                    pixel = self.current[i]
                    for e in self.current_eyes:
                        e[i] = pixel

    def draw_lids(self):
        blink_pixels = settings.BLINK[self.blink_index]
        blink_color = (0, 0, 0)
        if not self.is_transitioning:
            blink_color = self.lid_color

        for i in range(settings.PIXELS_PER_EYE):
            pixel = ((blink_color if blink_pixels[i] else None) or self.current_eyes[0][i])

            for e in self.current_eyes:
                e[i] = pixel

    def step_blink(self):
        self.blink_index += 1
        if self.is_tired and self.blink_index == settings.BLINK_CLOSED_INDEX + 1:
            self.blink_index = 0
            self.is_tired = False
            self.is_awake = False
            self.is_blinking = False
            self.is_transitioning = False
            for e in self.current_eyes:
                e.available = True
            self.current_eyes = []

#            logging.info("{} goes to sleep".format(self.name))

        if self.blink_index == len(settings.BLINK):
            self.blink_index = 0
            self.next_blink = random.randint(self.minimum_blink,
                                             self.maximum_blink)
            self.is_blinking = False
            self.is_transitioning = False
