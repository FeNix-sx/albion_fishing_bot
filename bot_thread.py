from PyQt5.QtCore import QThread, pyqtSignal, QProcess
import os
import sys
import locale


class BotThread(QThread):
    log_signal = pyqtSignal(str)
    status_signal = pyqtSignal(bool)

    def __init__(self):
        super().__init__()
        self.process = QProcess()
        self.process.readyReadStandardOutput.connect(self.handle_output)
        self.process.readyReadStandardError.connect(self.handle_error)
        self.process.finished.connect(self.process_finished)

    def run(self):
        try:
            self.status_signal.emit(True)
            self.log_signal.emit("Запуск main.py...")

            # Устанавливаем правильную кодировку для Windows
            if os.name == 'nt':
                os.environ["PYTHONIOENCODING"] = "utf-8"
                self.process.setProcessChannelMode(QProcess.MergedChannels)

            # Запускаем main.py через тот же интерпретатор Python
            python_exec = sys.executable
            self.process.start(python_exec, ['main.py'])

            if not self.process.waitForStarted():
                self.log_signal.emit("Ошибка: не удалось запустить процесс")

        except Exception as e:
            self.log_signal.emit(f"Ошибка запуска: {str(e)}")

    def handle_output(self):
        data = self.process.readAllStandardOutput().data()
        try:
            text = data.decode('utf-8').strip()
            if text:
                self.log_signal.emit(text)
        except UnicodeDecodeError:
            try:
                text = data.decode(locale.getpreferredencoding()).strip()
                if text:
                    self.log_signal.emit(text)
            except Exception as e:
                self.log_signal.emit(f"Ошибка декодирования вывода: {str(e)}")

    def handle_error(self):
        data = self.process.readAllStandardError().data()
        try:
            text = data.decode('utf-8').strip()
            if text:
                self.log_signal.emit(f"ОШИБКА: {text}")
        except UnicodeDecodeError:
            try:
                text = data.decode(locale.getpreferredencoding()).strip()
                if text:
                    self.log_signal.emit(f"ОШИБКА: {text}")
            except Exception as e:
                self.log_signal.emit(f"Ошибка декодирования ошибки: {str(e)}")

    def process_finished(self):
        self.status_signal.emit(False)
        self.log_signal.emit("Процесс завершен")

    def stop(self):
        if self.process.state() == QProcess.Running:
            self.process.terminate()
            if not self.process.waitForFinished(2000):
                self.process.kill()
        self.status_signal.emit(False)