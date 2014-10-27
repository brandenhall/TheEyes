import socket
import logging

from tornado import ioloop
from tornado import iostream


class ReconnectingTCPClient(object):
    handler = None
    timeout = 10000
    num_try = -1
    Connection = socket.SOCK_STREAM

    def __init__(self, name):
        self.sock = socket.socket(socket.AF_INET, self.Connection, 0)
        self.stream = iostream.IOStream(self.sock)
        self.iol = ioloop.IOLoop.instance()
        self.scheduler = ioloop.PeriodicCallback(
            self.try_connect, self.timeout, io_loop=self.iol)
        self.client = None
        self.name = name

    def connect(self, HOST, PORT, timeout=1000, num_try=-1):
        self.num_try = num_try
        self.attempts = 0
        self.HOST = HOST
        self.PORT = PORT
        self.try_connect(True)

    def try_connect(self, first_time=False):

        if self.attempts != self.num_try:
            self.attempts += 1
            if first_time:
                logging.info("{} trying to connect...".format(self.name))
            else:
                logging.info("{} trying to reconnect...".format(self.name))

            self.sock = socket.socket(socket.AF_INET, self.Connection, 0)
            self.stream = iostream.IOStream(self.sock)
            self.stream.connect((self.HOST, self.PORT,), self.on_connect)
            self.scheduler.stop()
        else:
            try:
                self.scheduler.stop()
            except Exception:
                pass
            self.iol.close()

    def on_connect(self):
        self.attempts = 0
        self.stream.set_close_callback(self.on_close)
        self.client = self.handler(self.stream, self.HOST+':'+str(self.PORT))

    def stop(self):
        self.stream.close()

    def on_close(self):
        if self.client:
            self.client.on_close()
        else:
            logging.warning(
                "Cannot connect, host %s:%s is unreachable", self.HOST, self.PORT)
        if self.attempts != self.num_try:
            self.attempts = 0
            self.scheduler.start()
        else:
            self.iol.stop()
            self.iol.close()
