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

    def __del__(self):
        log_message('Shutting down all engine workers.')
        self._stop.set()

    def add_event(self, event: SMSEvent) -> None:
        self._output_events.put(event, blocking=False)

    def _do_work_fn(self) -> None:
        event = None
        queue = AmazonSQS(json_config_path=self._sqs_config_path)
        notifier = TwilioSMSNotifier(json_config_path=self._twilio_config_path)
        while not self._stop.is_set():
            try:
                event = queue.get()
                log_message(
                    'Engine worker processing event {}'.format(event.to_json()))
                recipient_list = event.recipient_list(gamedb=self._gamedb)
                message = event.message_content(gamedb=self._gamedb)
                if len(recipient_list) > 1:
                    notifier.send_bulk_sms(
                        message=message,
                        recipient_addresses=recipient_list
                    )
                elif len(recipient_list) == 1:
                    notifier.send_sms(
                        message=message,
                        recipient_address=recipient_list[0]
                    )
                else:
                    pass
            except Exception as e:
                log_message(
                    'Engine worker failed with exception {}.'.format(e))
                if event:
                    # TODO(brandon) implement error resolution and monitoring system
                    self._output_events.put(event)
        log_message('Shutting down workder thread {}.'.format(
            threading.current_thread().ident))
