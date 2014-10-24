from tornado.tcpserver import TCPServer


class LineServer(TCPServer):
    handler = None

    def handle_stream(self, stream, address):
        self.handler(stream, address)
