class Engine(object):

    def __init__(self, options: GameOptions):
        self._options = options
        self._input_events = EventQueue()
        self._output_events = EventQueue()
        self._stop = threading.Event()
        self._workers = list()
        for _ in range(options.engine_worker_thread_count):
            worker = Process(target=self._worker_fn)
            self._workers.add(worker)
            worker.start()

    def add_event(self, event: Event):
        if isinstance(event, OutputEvent):
            self._output_events.put(event)
        elif isinstance(event, InputEvent):
            self._input_events.put(event)

    def _worker_fn(self):
        while not self._stop.is_set():
            event = self._input_events.get()

            # TODO(brandon): identify all arguments required by handler
            event.handle()
            time.sleep(self._options.engine_worker_sleep_interval_sec)