import threading
from modules.fishing_bot import FishingBot  # Импорт вашего оригинального класса


class FishingBotController:
    """Обёртка для управления FishingBot с поддержкой GUI."""

    def __init__(self):
        self.bot = FishingBot()  # Ваш оригинальный класс без изменений
        self._is_running = False
        self._thread = None

    def start(self):
        """Запускает бота в отдельном потоке."""
        if self._is_running:
            return False

        self._is_running = True
        self._thread = threading.Thread(target=self._run_bot)
        self._thread.daemon = True
        self._thread.start()
        return True

    def stop(self):
        """Останавливает бота."""
        self._is_running = False
        if self._thread:
            self._thread.join()
        self.bot.stop()  # Если в вашем классе есть метод stop()

    def _run_bot(self):
        while self._is_running:
            try:
                self.bot.run()  # Основная логика
                self.signals.log_signal.emit("Бот работает...")
            except Exception as e:
                self.signals.log_signal.emit(f"Ошибка: {str(e)}")

    def is_running(self):
        """Проверяет, работает ли бот."""
        return self._is_running

    def set_sensitivity(self, value):
        """Пример: обновление чувствительности (если нужно)."""
        if hasattr(self.bot, 'set_sensitivity'):
            self.bot.set_sensitivity(value)