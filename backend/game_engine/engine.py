import threading
from multiprocessing import Process
import time
from game_engine.events import SMSEvent, EventQueue, AmazonSQS
from game_engine.database import Database
from typing import Text
from game_engine.twilio import TwilioSMSNotifier
from multiprocessing import Pool, TimeoutError
from game_engine.common import GameError
from game_engine.common import log_message
from concurrent.futures import ThreadPoolExecutor
from game_engine.common import GameOptions


class Engine(object):

    def __init__(self, options: GameOptions, sqs_config_path: Text = '', twilio_config_path: Text = '', gamedb: Database = None):
        self._options = options
        self._output_events = AmazonSQS(
            json_config_path=sqs_config_path)
        self._sqs_config_path = sqs_config_path
        self._twilio_config_path = twilio_config_path
        self._stop = threading.Event()
        self._workers = list()
        self._gamedb = gamedb
        self._executor = ThreadPoolExecutor(
            max_workers=options.engine_worker_thread_count)
        for _ in range(options.engine_worker_thread_count):
            self._executor.submit(self._do_work_fn)

    def add_event(self, event: SMSEvent) -> None:
        self._output_events.put(event, blocking=False)

    def stop(self):
        log_message('Shutting down all engine workers.')
        self._stop.set()

    def _do_work_fn(self) -> None:
        event = None
        queue = AmazonSQS(json_config_path=self._sqs_config_path)
        notifier = TwilioSMSNotifier(json_config_path=self._twilio_config_path)
        while not self._stop.is_set():
            try:
                log_message('Getting event from queue...')
                event = queue.get()
                log_message(
                    'Engine worker processing event {}'.format(event.to_json()))
                notifier.send(sms_event_messages=event.messages)
            except Exception as e:
                log_message(
                    'Engine worker failed with exception {}.'.format(e))
        log_message('Shutting down workder thread {}.'.format(
            threading.current_thread().ident))
