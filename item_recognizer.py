import cv2
import pytesseract
import re
import os
import pyautogui
import numpy as np
from typing import Tuple, Optional, Dict, List
from items_db import ITEMS_DB

# Указываем путь к Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'


class ItemRecognizer:
    def __init__(self, items_db: Dict[str, List[str]] = None):
        """
        Инициализация распознавателя

        :param items_db: Словарь с базой предметов (если None, загрузится из items_db.py)
        """
        self.items_db = items_db if items_db is not None else ITEMS_DB
        self.base_resolution = (2560, 1440)
        self.base_coords = (1050, 1510, 70, 170)  # x1, x2, y1, y2 для базового разрешения

        # Специальные исправления для часто неправильно распознаваемых названий
        self.special_corrections = {
            'астер рыбной ловли': 'Книга интуиции',
            'рыбной ловли': 'Книга интуиции',
            'яркоперый получено': 'Яркоперый судак',
            'истая форел': 'Пятнистая форель',
            'амышовый подкаменщи': 'Камышовый подкаменщик',
            'подкаменщи шт': 'Камышовый подкаменщик'
        }

    def get_scaled_coords(self, img) -> Tuple[int, int, int, int]:
        """Рассчитывает координаты области пропорционально базовому разрешению"""
        height, width = img.shape[:2]
        width_ratio = width / self.base_resolution[0]
        height_ratio = height / self.base_resolution[1]
        return (
            int(self.base_coords[0] * width_ratio),
            int(self.base_coords[1] * width_ratio),
            int(self.base_coords[2] * height_ratio),
            int(self.base_coords[3] * height_ratio)
        )

    def preprocess_image(self, roi):
        """Предварительная обработка изображения для улучшения распознавания"""
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        # Увеличиваем контраст
        processed = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
        # Убираем шумы
        kernel = np.ones((2, 2), np.uint8)
        processed = cv2.morphologyEx(processed, cv2.MORPH_CLOSE, kernel)
        return processed

    def extract_text(self, roi) -> str:
        """Распознает текст с области изображения"""
        processed = self.preprocess_image(roi)
        try:
            # Пробуем разные конфигурации OCR
            text = pytesseract.image_to_string(
                processed,
                lang='rus',
                config='--psm 6 --oem 3'  # Оптимальный режим для строк
            )
            return text.strip()
        except pytesseract.TesseractNotFoundError:
            print("Ошибка: Tesseract не установлен или путь указан неверно")
            return ""

    def clean_text(self, text: str) -> Tuple[Optional[str], int]:
        """Очищает и нормализует распознанный текст"""
        if not text:
            return None, 0

        # Извлечение количества (более надежная версия)
        count = 1
        count_matches = re.findall(r'\b\d+\b', text)
        if count_matches:
            count = int(count_matches[-1])  # Берем последнее найденное число

        # Очистка названия
        name = re.sub(r'(Получено|получено|ПОЛУЧЕНО)[^\d]*\d*[^\w]*шт\.*', '', text, flags=re.IGNORECASE)
        name = re.sub(r'[^а-яА-ЯёЁ\s\-]', '', name.strip())
        name = re.sub(r'\s+', ' ', name)

        # Применение специальных исправлений
        for wrong, correct in self.special_corrections.items():
            if wrong in name.lower():
                return correct, count

        # Фильтрация некорректных названий
        words = [word for word in name.split()
                 if len(word) > 1 and not word.isdigit() and word.lower() not in ['шт', 'получено']]

        return ' '.join(words) if words else None, count

    def find_match(self, text: str) -> Optional[str]:
        """Улучшенный поиск по ключевым словам с приоритетом полных совпадений"""
        if not text or len(text) < 2:
            return None

        text_lower = text.lower()

        # 1. Проверка полных совпадений (сначала)
        for name in self.items_db:
            if text_lower == name.lower():
                return name

        # 2. Проверка частичных совпадений
        for name, keywords in self.items_db.items():
            # Проверяем все ключевые слова
            for keyword in keywords:
                if keyword in text_lower or text_lower in keyword:
                    return name

        return None

    def process_image(self, image_path: str) -> Tuple[Optional[str], int, Optional[str]]:
        """
        Обрабатывает одно изображение

        :return: (matched_name, count, clean_name)
                 где clean_name может быть None если предмет опознан
        """
        img = cv2.imread(image_path)
        if img is None:
            print(f"Ошибка загрузки изображения: {image_path}")
            return None, 0, None

        x1, x2, y1, y2 = self.get_scaled_coords(img)
        roi = img[y1:y2, x1:x2]

        text = self.extract_text(roi)
        clean_name, count = self.clean_text(text)

        # Специальная проверка для сложных случаев
        if clean_name and 'амышовый' in clean_name.lower() and 'подкаменщи' in clean_name.lower():
            return 'Камышовый подкаменщик', count, clean_name

        matched_name = self.find_match(clean_name) if clean_name else None

        return matched_name, count, clean_name

    def handle_new_item(self, new_name: str) -> bool:
        """
        Предлагает добавить новый предмет в базу
        :return: True если предмет был добавлен
        """
        print(f"\nОбнаружен новый предмет: {new_name}")
        choice = input("Добавить в базу? (y/n): ").lower()

        if choice != 'y':
            return False

        base_name = input("Каноническое название: ").strip()
        if not base_name:
            return False

        keywords = input("Ключевые слова через запятую: ").lower().strip()
        keywords = [k.strip() for k in keywords.split(',') if k.strip()]

        # Добавляем в базу
        self.items_db[base_name] = keywords
        print(f"Добавлен новый предмет: {base_name}")

        # Обновляем файл базы
        self._update_items_db_file()
        return True

    def _update_items_db_file(self):
        """Обновляет файл items_db.py с новыми предметами"""
        with open('items_db.py', 'w', encoding='utf-8') as f:
            f.write('# -*- coding: utf-8 -*-\n')
            f.write('"""\nБаза известных предметов для распознавания.\n"""\n\n')
            f.write('ITEMS_DB = {\n')
            for name, keywords in self.items_db.items():
                f.write(f"    '{name}': {keywords},\n")
            f.write('}\n')

    def capture_and_recognize(self):
        """Делает скриншот и сразу распознает предмет"""
        screenshot_path = "temp_item_capture.png"
        pyautogui.screenshot(screenshot_path)
        result = self.process_image(screenshot_path)

        try:
            os.remove(screenshot_path)
        except:
            pass

        return result


# Пример использования
if __name__ == "__main__":
    recognizer = ItemRecognizer()
    image_path = "screenshot_2025-04-05_10-01-16.png"  # Укажите путь к вашему скриншоту

    matched_name, count, clean_name = recognizer.process_image(image_path)

    if matched_name:
        print(f"Распознано: {matched_name} ({count} шт)")
    elif clean_name:
        print(f"Неизвестный предмет: {clean_name}")
        if recognizer.handle_new_item(clean_name):
            # Переобрабатываем с обновленной базой
            matched_name, count, _ = recognizer.process_image(image_path)
            if matched_name:
                print(f"Теперь распознано как: {matched_name}")
    else:
        print("Не удалось распознать предмет")