import logging
import random

from conf import settings

logger = logging.getLogger(__name__)


class Creature(object):

    def __init__(self):
        self.name = ''
        self.lifespan = 30
        self.life_remaining = 30
        self.restlessness = 0
        self.minimum_blink = 0
        self.maximum_blink = 1
        self.sclera_color = (0, 0, 0)
        self.lid_color = (0, 0, 0)
        self.default = []
        self.layer = []
        self.is_overlay = False
        self.pupil_mask = []
        self.current = []
        self.eyes = []

        self.is_awake = False
        self.is_blinking = False
        self.blink_frame = 1

        self.moves = []
        self.next_move = 0
        self.position = 31

        self.current_eyes = []

        self.blink_toggle = False
        self.blink_index = 0
        self.next_blink = 0

    def update(self, elapsed):
        if self.is_awake:
            self.move()

            self.draw_eyes()
            self.draw_lids()

            # move blink every other frame
            self.blink_frame += 1

            if self.blink_frame % settings.BLINK_STEP == 0:
                self.blink_frame = 1
                if self.is_blinking:
                    self.step_blink()
                else:
                    self.next_blink -= 1
                    if self.next_blink <= 0:
                        self.blink_index = 0
                        self.is_blinking = True

    def wakeup(self):
        self.is_awake = True
        self.is_blinking = True
        self.position = 31
        self.life_remaining = self.lifespan
        self.blink_index = settings.BLINK_CLOSED_INDEX + 2

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

        for i in range(settings.PIXELS_PER_EYE):
            pixel = ((blink_color if blink_pixels[i] else None) or self.current_eyes[0][i])

            for e in self.current_eyes:
                e[i] = pixel

    def step_blink(self):
        self.blink_index += 1
        if self.blink_index == settings.BLINK_CLOSED_INDEX + 1:

            if self.life_remaining == 0:
                self.is_awake = False
                self.brainstem.wake_creature(self)

        elif self.blink_index == len(settings.BLINK):
            self.blink_index = 0
            self.next_blink = random.randint(self.minimum_blink,
                                             self.maximum_blink)
            self.is_blinking = False
            self.life_remaining -= 1
