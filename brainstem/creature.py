class Creature(object):

    def __init__(self):
        self.offset_a = 0
        self.offset_b = 0
        self.offset_c = 0
        self.name = ''
        self.circadian_offset = 0
        self.circadian_period = 0
        self.restlessness = 0
        self.minimum_speed = 0
        self.maximum_speed = 1
        self.sclera_color = (0, 0, 0)
        self.lid_color = (0, 0, 0)
        self.pixels = []
        self.responses = {}
