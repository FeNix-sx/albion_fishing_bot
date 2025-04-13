import threading
import time
from PyQt5.QtCore import QObject, pyqtSignal

class BotManager(QObject):
    log_message = pyqtSignal(str)
    status_changed = pyqtSignal(bool)

    def __init__(self, template_path):
        super().__init__()
        self.template_path = template_path
        self._running = False
        self._thread = None
        self._lock = threading.Lock()
        self.bot = None  # Инициализация будет при первом запуске

    def _initialize_bot(self):
        """Ленивая инициализация бота с правильными параметрами"""
        if self.bot is None:
            from modules.fishing_bot import FishingBot
            self.bot = FishingBot(template_path=self.template_path)

    def start(self):
        if self._running:
            return

        self._initialize_bot()  # Инициализируем бота при первом запуске
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self.status_changed.emit(True)
        self.log_message.emit("Бот запущен")

    def stop(self):
        if not self._running:
            return

        self._running = False
        if self._thread:
            self._thread.join()
        self.status_changed.emit(False)
        self.log_message.emit("Бот остановлен")

    def _run(self):
        while self._running:
            with self._lock:
                try:
                    self.bot.run()  # Ваш оригинальный код
                except Exception as e:
                    self.log_message.emit(f"Ошибка: {str(e)}")
                    time.sleep(1)