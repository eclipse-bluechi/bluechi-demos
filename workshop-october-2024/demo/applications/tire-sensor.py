#
# Copyright Contributors to the Eclipse BlueChi project
#
# SPDX-License-Identifier: MIT-0

import can
import signal
import time
import random
import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))


class TirePressureService():

    def __init__(self) -> None:
        self.canbus = can.Bus(interface='socketcan',
                              channel='vcan0',
                              receive_own_messages=False)
        self.is_running = True

    def run(self):
        try:
            while self.is_running:
                pressure = random.randrange(0, 100)
                logger.info(
                    f"Sending CAN message with tire pressure: {pressure}")
                msg = can.Message(data=[pressure])
                self.canbus.send(msg)

                time.sleep(2)
        except can.exceptions.CanError as ex:
            if not self.canbus._is_shutdown:
                logger.error(f"CANError: {ex}")

    def shutdown(self):
        self.is_running = False
        self.canbus.shutdown()


class ShutdownHandler:
    def __init__(self, service: TirePressureService) -> None:
        self.service = service

    def handle_kill(self, signum, frame):
        service.shutdown()

    def __enter__(self):
        signal.signal(signal.SIGINT, self.handle_kill)

    def __exit__(self, type, value, traceback):
        pass


if __name__ == "__main__":
    service = TirePressureService()
    with ShutdownHandler(service):
        service.run()
