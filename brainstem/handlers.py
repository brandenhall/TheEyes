import json
import logging

from tornado.iostream import StreamClosedError

from conf import settings

from tornado.web import StaticFileHandler
from tornado.websocket import WebSocketHandler


class IndexStaticFileHandler(StaticFileHandler):
    def parse_url_path(self, url_path):
        if not url_path or url_path.endswith('/'):
            url_path += 'index.html'

        return super(IndexStaticFileHandler, self).parse_url_path(url_path)


class SimulatorHandler(WebSocketHandler):
    brainstem = None

    def open(self):
        self.brainstem.add_simulation_client(self)

    def check_origin(self, origin):
        if settings.DEBUG:
            return True
        else:
            return super().check_origin(origin)

    def on_message(self, message):
        pass

    def on_close(self):
        self.brainstem.remove_simulation_client(self)


class CortexHandler():
    brainstem = None
    stream = None
    address = None
    delimiter = b"\r\n"

    def __init__(self, stream, address):
        self.stream = stream
        self.address = address
        self.on_connect()
        self.wait()

    def wait(self):
        self.stream.read_until(self.delimiter, self.on_chunk)

    def send(self, message):
        try:
            data = json.dumps(message)
            self.stream.write(str.encode(data) + self.delimiter)
        except StreamClosedError:
            logging.warning("Could not send to cortex, stream is closed!")
            self.on_close()

    def on_connect(self):
        self.brainstem.add_cortex_client(self)

    def on_close(self):
        self.brainstem.remove_cortex_client(self)

    def on_line_received(self, line):
        logging.info(line)

        try:
            data = json.loads(line)
            self.brainstem.on_cortex_command(data)

        except ValueError as err:
            logging.error("Problem parsing from client {}".format(err))

    def on_chunk(self, chunk):
        self.on_line_received(chunk[:-len(self.delimiter)].decode("utf-8"))
        self.wait()
