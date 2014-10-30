import logging


class Eye():

    def __init__(self, pixels, index):
        self.id = 0
        self.preferences = []
        self.start_index = index
        self.end_index = index + 63
        self.pixels = pixels
        self.frame = 0
        self.available = True

    def set_pixels(self, data):
        self.pixels[self.start_index:self.end_index] = data

    def __setitem__(self, name, item):
        try:
            self.pixels[self.start_index + name] = item
        except TypeError:
            logging.error("Can not set {} to {}".format(name, item))

    def __getitem__(self, key):
        try:
            return self.pixels[key + self.start_index]
        except TypeError:
            logging.error("Can not get {}".format(key))
            return None

    def __str__(self):
        return self.id
