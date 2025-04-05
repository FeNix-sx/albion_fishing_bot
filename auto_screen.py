import os
from PIL import ImageGrab
from datetime import datetime

class ScreenshotTaker:
    def __init__(self, save_folder="screens"):
        """
        Инициализация класса.
        :param save_folder: Папка для сохранения скриншотов (по умолчанию 'screens')
        """
        self.save_folder = save_folder
        # Создаем папку, если её нет
        os.makedirs(self.save_folder, exist_ok=True)

    def take_screenshot(self):
        """Делает скриншот всего экрана и возвращает изображение"""
        return ImageGrab.grab()

    def save_screenshot(self, image, filename=None):
        """
        Сохраняет скриншот в файл.
        :param image: Изображение (объект PIL.Image)
        :param filename: Имя файла (если None, будет сгенерировано автоматически)
        :return: Полный путь к сохраненному файлу
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"screenshot_{timestamp}.png"
        save_path = os.path.join(self.save_folder, filename)
        image.save(save_path)
        return save_path

    def run(self, filename=None):
        """
        Делает и сохраняет скриншот.
        :param filename: Имя файла (опционально)
        :return: Путь к сохраненному файлу
        """
        screenshot = self.take_screenshot()
        saved_path = self.save_screenshot(screenshot, filename)
        print(f"Скриншот сохранен: {saved_path}")
        return saved_path


# Пример использования:
if __name__ == "__main__":
    # Создаем экземпляр класса
    screenshotter = ScreenshotTaker()

    # Делаем скриншот и сохраняем его
    screenshotter.run()