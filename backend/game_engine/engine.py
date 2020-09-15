import threading
from multiprocessing import Process
import time
from game_engine.events import SMSEvent, EventQueue, AmazonSQS
from game_engine.database import Database
from typing import Text
from game_engine.twilio import SMSNotifier
from game_engine.twilio import TwilioSMSNotifier
from multiprocessing import Pool, TimeoutError
from game_engine.common import GameError
from game_engine.common import log_message
from concurrent.futures import ThreadPoolExecutor
from game_engine.common import GameOptions
from game_engine.events import EventQueueError
import traceback


class Engine(object):

    def __init__(self, options: GameOptions, game_id: Text, sqs_config_path: Text = '', twilio_config_path: Text = '', gamedb: Database = None):
        self._options = options
        self.game_id = game_id
        self._output_events = AmazonSQS(
            json_config_path=sqs_config_path,
            game_id=game_id)
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
        log_message(message='Shutting down all engine workers.',
                    game_id=self.game_id)
        self._stop.set()

    def _get_sms_notifier(self) -> SMSNotifier:
        return TwilioSMSNotifier(json_config_path=self._twilio_config_path, game_id=self.game_id)

    def _do_work_fn(self) -> None:
        event = None
        notifier = self._get_sms_notifier()
        queue = AmazonSQS(
            json_config_path=self._sqs_config_path, game_id=self.game_id)
        while not self._stop.is_set():
            try:
                event = queue.get()
                game_id = ""
                if hasattr(event, "game_id"):
                    game_id = event.game_id
                log_message(
                    message='Engine worker processing event {}'.format(
                        event.to_json()),
                    game_id=self.game_id)
                notifier.send(sms_event_messages=event.messages(
                    gamedb=self._gamedb))
            except EventQueueError:
                pass
            except Exception as e:
                log_message(
                    message=f'Engine worker failed with exception {str(e)} {traceback.format_stack()}.',
                    game_id=self.game_id)
                self.stop()
                raise

        log_message(message='Shutting down workder thread {}.'.format(
            threading.current_thread().ident),
            game_id=self.game_id)
