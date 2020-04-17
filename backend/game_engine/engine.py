import threading
from multiprocessing import Process
import time
from game_engine.events import SMSEvent, EventQueue, AmazonSQS
from typing import Text

class Engine(object):

    def __init__(self, options: object, sqs_config_path: Text):
        self._options = options
        self._input_events = AmazonSQS(
            json_config_path=sqs_config_path)
        self._stop = threading.Event()
        self._workers = list()

    def add_event(self, event: SMSEvent):
        self._output_events.put(event, blocking=False)
