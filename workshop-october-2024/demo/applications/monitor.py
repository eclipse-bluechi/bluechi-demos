#
# Copyright Contributors to the Eclipse BlueChi project
#
# SPDX-License-Identifier: MIT-0

import time
import signal
import requests
import logging
import sys

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.StreamHandler(stream=sys.stdout))


class Monitor():

    def __init__(self) -> None:
        self.is_running = True

    def run(self) -> None:
        while self.is_running:
            try:
                resp = requests.get("http://127.0.0.1:5000/tire/pressure")
                if resp.status_code != 200:
                    logger.error(f"Failed to fetch tire pressure")
                    continue

                pressure = int(resp.content)
                if pressure < 50:
                    logger.error(f"Tire pressue '{pressure}' below threshold!")
                else:
                    logger.info(f"Tire pressure '{pressure}' is fine")
            except Exception as ex:
                logger.error(f"Failed fetching tire pressure: {ex}")

            time.sleep(5)

    def shutdown(self) -> None:
        self.is_running = False


class ShutdownHandler:
    def __init__(self, monitor: Monitor) -> None:
        self.monitor = monitor

    def handle_kill(self, signum, frame):
        self.monitor.shutdown()

    def __enter__(self):
        signal.signal(signal.SIGINT, self.handle_kill)

    def __exit__(self, type, value, traceback):
        pass


if __name__ == "__main__":
    monitor = Monitor()
    with ShutdownHandler(monitor):
        monitor.run()
