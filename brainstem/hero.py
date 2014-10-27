import logging
import random

from conf import settings


class Hero(object):
    def __init__(self, item, eye):
        self.animation = item[0]
        self.eye = eye
        self.frame = 0
        self.loops = item[1]
        self.is_complete = False

    def draw(self):
        if self.frame == len(self.animation):
            self.loops -= 1

            if self.loops == 0:
                self.eye.set_pixels([(0, 0, 0)] * settings.PIXELS_PER_EYE)
                self.is_complete = True
                self.eye.available = True
                self.eye = None
                self.animation = None
            else:
                self.frame = 0
        else:
            self.eye.set_pixels(self.animation[self.frame])
            self.frame += 1


class HeroManager(object):
    def __init__(self, eyes):
        self.eyes = eyes
        self.animations = []
        self.heros = []
        self.frame = 0

    def add_animation(self, animation, loops):
        self.animations.append((animation, loops))

    def update(self):
        if self.frame == 0:
            self.frame = 4

            if random.randint(0, settings.HERO_RATE * 15) == 1:
                tries = 0
                eye = None
                while eye is None and tries < settings.EYE_COUNT * 2:
                    eye = random.choice(self.eyes)
                    tries += 1
                    if eye.available is False:
                        eye = None

                if eye is not None:
                    eye.available = False
                    item = random.choice(self.animations)
                    hero = Hero(item, eye)
                    self.heros.append(hero)

            for hero in self.heros:
                hero.draw()

            self.heros = [x for x in self.heros if not x.is_complete]

        self.frame -= 1
