#
# Copyright Contributors to the Eclipse BlueChi project
#
# SPDX-License-Identifier: MIT-0

import can
import signal
import threading
import logging
import sys
from flask_cors import CORS
from flask import Flask, Response
from werkzeug.serving import make_server, BaseWSGIServer

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))


class Server():

    def __init__(self) -> None:
        self.app = Flask(__name__)
        self.app.config.from_object(__name__)
        self.app.config.from_envvar('SKELETON_SETTINGS', silent=True)
        CORS(self.app)
        self.app.wsgi_app = ProxyFixupHelper(self.app.wsgi_app)

        @self.app.route("/tire/pressure", methods=["GET"])
        def handle_tire_pressure():
            print("Handling GET /tire/pressure...")

            return Response(f"{self.tire_pressure}", status=200, mimetype="text/plain")

        self.server: BaseWSGIServer = make_server("127.0.0.1", 5000, self.app)

        self.tire_pressure = 0
        self.canbus = can.Bus(interface='socketcan',
                              channel='vcan0',
                              receive_own_messages=False)

        self.tire_pressure_worker: threading.Thread = None
        self.flask_worker: threading.Thread = None

    def update_tire_pressure(self):
        try:
            for msg in self.canbus:
                pressure = int.from_bytes(
                    msg.data, byteorder='big', signed=False)
                logger.info(
                    f"Update tire pressure from '{self.tire_pressure}' to '{pressure}'")
                self.tire_pressure = pressure
        except can.exceptions.CanError as ex:
            if not self.canbus._is_shutdown:
                logger.error(f"CANError: {ex}")

    def run(self) -> None:
        self.tire_pressure_worker = threading.Thread(
            target=self.update_tire_pressure, args=())
        self.tire_pressure_worker.start()

        self.flask_worker = threading.Thread(
            target=self.server.serve_forever, args=())
        self.flask_worker.start()

        self.tire_pressure_worker.join()
        self.flask_worker.join()

    def shutdown(self) -> None:
        self.canbus.shutdown()
        self.server.shutdown()


class ProxyFixupHelper(object):
    def __init__(self, app):
        self.app = app

    def __call__(self, environ, start_response):
        # Only perform this fixup if the current remote host is localhost.
        if environ['REMOTE_ADDR'] == '127.0.0.1':
            host = environ.get('HTTP_X_REAL_IP', False)
            if host:
                environ['REMOTE_ADDR'] = host
        return self.app(environ, start_response)


class ShutdownHandler:
    def __init__(self, server: Server) -> None:
        self.server = server

    def handle_kill(self, signum, frame):
        self.server.shutdown()

    def __enter__(self):
        signal.signal(signal.SIGINT, self.handle_kill)

    def __exit__(self, type, value, traceback):
        pass


if __name__ == "__main__":
    server = Server()
    with ShutdownHandler(server):
        server.run()
