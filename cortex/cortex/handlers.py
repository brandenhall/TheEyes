import json
import logging

from .conf import settings

from tornado.iostream import StreamClosedError
from tornado.websocket import WebSocketHandler


class InteractionHandler(WebSocketHandler):
    def open(self):
        Cortex.instance().add_interaction_client(self)
        self.send_status()
        self.last_request_id = None

    def check_origin(self, origin):
        return True

    def on_message(self, message):
        try:
            data = json.loads(message.strip())
            Cortex.instance().on_interaction_command(self, data)
        except ValueError:
            logging.warning("Could not parse message {}".format(message))

    def send_status(self):
        message = {
            'type': 'status',
            'has_brainstem': (Cortex.instance().brainstem is not None),
            'geolocation_required': settings.GEOLOCATION_REQUIRED,
        }

        self.write_message(json.dumps(message))

    def send(self, message):
        try:
            data = json.dumps(message)
            logging.info('Send to interaction: {}'.format(data))
            self.write_message(data)
        except StreamClosedError:
            logging.info('Could not send, stream closed')
            self.on_close()

    def on_close(self):
        Cortex.instance().remove_interaction_client(self)


class BrainstemHandler():
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
            logging.info('Send to brainstem: {}'.format(data))
            self.stream.write(str.encode(data) + self.delimiter)
        except StreamClosedError:
            logging.info('Could not send, stream closed')
            self.on_close()

    def on_connect(self):
        Cortex.instance().add_brainstem_client(self)
        self.stream.set_close_callback(self.on_close)

    def on_close(self):
        Cortex.instance().remove_brainstem_client(self)

    def on_line_received(self, message):
        try:
            data = json.loads(message.strip())
            Cortex.instance().on_brainstem_command(data)

        except ValueError as err:
            logging.error("Problem parsing from client {}".format(err))

    def on_chunk(self, chunk):
        self.on_line_received(chunk[:-len(self.delimiter)].decode("utf-8"))
        self.wait()

# prevent circular references
from .cortex import Cortex
