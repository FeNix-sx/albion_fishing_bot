import os
import cv2
import pytesseract
import re
import time
from collections import defaultdict
from typing import Dict, List, Tuple, Optional


class ScreenshotProcessor:
    """Класс для обработки скриншотов с распознаванием текста"""

    def __init__(self, items_db: Dict[str, List[str]], tesseract_path: str = None):
        """
        Инициализация процессора

        :param items_db: Словарь с базой предметов {'Название': ['ключевые', 'слова']}
        :param tesseract_path: Путь к tesseract.exe (если не в PATH)
        """
        if tesseract_path:
            pytesseract.pytesseract.tesseract_cmd = tesseract_path

        self.items_db = items_db
        self.base_resolution = (2560, 1440)
        self.base_coords = (1050, 1510, 70, 170)  # x1, x2, y1, y2 для базового разрешения

        # Специальные исправления для часто неправильно распознаваемых названий
        self.special_corrections = {
            'астер рыбной ловли': 'Книга интуиции',
            'рыбной ловли': 'Книга интуиции',
            'яркоперый получено': 'Яркоперый судак',
            'истая форел': 'Пятнистая форель'
        }

    def get_scaled_coords(self, img) -> Tuple[int, int, int, int]:
        """Рассчитывает координаты области пропорционально базовому разрешению"""
        height, width = img.shape[:2]

        width_ratio = width / self.base_resolution[0]
        height_ratio = height / self.base_resolution[1]

        x1 = int(self.base_coords[0] * width_ratio)
        x2 = int(self.base_coords[1] * width_ratio)
        y1 = int(self.base_coords[2] * height_ratio)
        y2 = int(self.base_coords[3] * height_ratio)

        return x1, x2, y1, y2

    def preprocess_image(self, roi, method: str = 'threshold_otsu'):
        """Применяет разные методы предобработки изображения"""
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

        if method == 'threshold_otsu':
            _, processed = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        elif method == 'adaptive_gaussian':
            processed = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
                                              cv2.THRESH_BINARY, 11, 2)
        elif method == 'denoise':
            processed = cv2.fastNlMeansDenoising(gray, None, 30, 7, 21)
            _, processed = cv2.threshold(processed, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        else:
            _, processed = cv2.threshold(gray, 150, 255, cv2.THRESH_BINARY)

        return processed

    def extract_text_with_retry(self, roi, lang: str = 'rus', retries: int = 3) -> str:
        """Пытается распознать текст с разными методами предобработки"""
        methods = ['threshold_otsu', 'adaptive_gaussian', 'denoise']
        best_text = ''
        best_conf = 0

        for method in methods[:retries]:
            try:
                processed = self.preprocess_image(roi, method)
                data = pytesseract.image_to_data(processed, lang=lang, output_type=pytesseract.Output.DICT)

                valid_confs = [float(conf) for conf in data['conf'] if conf != '-1']
                if not valid_confs:
                    continue

                current_conf = sum(valid_confs) / len(valid_confs)

                if current_conf > best_conf:
                    best_conf = current_conf
                    best_text = ' '.join([word for word, conf in zip(data['text'], data['conf'])
                                          if conf != '-1' and float(conf) > 60])

                    if best_conf > 90:
                        break

            except Exception as e:
                continue

        return best_text.strip() if best_text else pytesseract.image_to_string(roi, lang=lang)

    def clean_extracted_text(self, text: str) -> Tuple[Optional[str], int]:
        """Очищает и нормализует распознанный текст"""
        if not text:
            return None, 0

        # Удаление фразы о количестве
        count_match = re.search(r'(?<=Получено\s)\d+(?=\s*шт)', text, re.IGNORECASE)
        count = int(count_match.group(0)) if count_match else 1

        text_clean = re.sub(r'Получено\s*\d+\s*шт\.*', '', text, flags=re.IGNORECASE)
        text_clean = re.sub(r'[^а-яА-ЯёЁ\s\-]', '', text_clean.strip())
        text_clean = re.sub(r'\s+', ' ', text_clean)

        # Применение специальных исправлений
        for wrong, correct in self.special_corrections.items():
            if wrong in text_clean.lower():
                return correct, count

        # Фильтрация слишком коротких или некорректных названий
        words = [word for word in text_clean.split()
                 if len(word) > 1 and not word.isdigit()]

        return ' '.join(words) if words else None, count

    def find_item_match(self, text: str) -> Optional[str]:
        """Находит соответствие в базе предметов"""
        if not text or len(text) < 2:
            return None

        text_lower = text.lower()
        for item_name, keywords in self.items_db.items():
            if any(keyword in text_lower for keyword in keywords):
                return item_name
        return None

    def process_single_image(self, image_path: str) -> Dict:
        """Обрабатывает один скриншот"""
        img = cv2.imread(image_path)
        if img is None:
            return None

        x1, x2, y1, y2 = self.get_scaled_coords(img)
        roi = img[y1:y2, x1:x2]

        text = self.extract_text_with_retry(roi)
        clean_name, count = self.clean_extracted_text(text)
        matched_name = self.find_item_match(clean_name)

        return {
            'file': os.path.basename(image_path),
            'raw_text': text,
            'clean_name': clean_name,
            'item_name': matched_name,
            'count': count
        }

    def process_folder(self, folder_path: str) -> Tuple[Dict, Dict]:
        """
        Обрабатывает все изображения в папке

        :return: (results, stats) - словарь результатов и статистика
        """
        results = {}
        item_stats = defaultdict(int)

        files = [f for f in os.listdir(folder_path)
                 if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp'))]

        print(f"Начата обработка {len(files)} файлов...")
        start_time = time.time()

        for i, filename in enumerate(files, 1):
            filepath = os.path.join(folder_path, filename)
            result = self.process_single_image(filepath)

            if not result:
                continue

            name = result['item_name'] or result['clean_name']
            if name:
                item_stats[name] += result['count']

            results[filename] = result

            if i % 10 == 0 or i == len(files):
                elapsed = time.time() - start_time
                print(f"Обработано {i}/{len(files)} файлов ({elapsed:.1f} сек)")

        return results, dict(item_stats)

    def save_results(self, results: Dict, output_file: str = 'results.py'):
        """Сохраняет результаты в Python-файл"""
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write("# Результаты распознавания\n")
            f.write("from typing import Dict, TypedDict\n")
            f.write("from collections import defaultdict\n\n")
            f.write("class ResultItem(TypedDict):\n")
            f.write("    file: str\n")
            f.write("    raw_text: str\n")
            f.write("    clean_name: str\n")
            f.write("    item_name: str\n")
            f.write("    count: int\n\n")
            f.write("data: Dict[str, ResultItem] = {\n")
            for filename, item in results.items():
                f.write(f'    "{filename}": {{\n')
                f.write(f'        "file": "{item["file"]}",\n')
                f.write(f'        "raw_text": """{item["raw_text"]}""",\n')
                f.write(f'        "clean_name": """{item["clean_name"]}""",\n')
                f.write(f'        "item_name": "{item["item_name"]}",\n')
                f.write(f'        "count": {item["count"]},\n')
                f.write('    },\n')
            f.write("}\n\n")
            f.write("stats = defaultdict(int)\n")
            f.write("for item in data.values():\n")
            f.write("    name = item['item_name'] or item['clean_name']\n")
            f.write("    if name:\n")
            f.write("        stats[name] += item['count']\n")

    def print_statistics(self, stats: Dict):
        """Выводит статистику"""
        print("\nСтатистика пойманного:")
        print("-" * 40)
        for item, count in sorted(stats.items(), key=lambda x: x[1], reverse=True):
            print(f"{item:.<30} {count:>4} шт")
        print("-" * 40)
        print(f"Всего предметов: {len(stats)}")
        print(f"Общее количество: {sum(stats.values())}")


if __name__ == "__main__":
    # Пример использования
    from items_db import ITEMS_DB

    processor = ScreenshotProcessor(
        items_db=ITEMS_DB,
        tesseract_path=r'C:\Program Files\Tesseract-OCR\tesseract.exe'
    )

    # Обработка папки со скриншотами
    results, stats = processor.process_folder('screens')

    # Вывод и сохранение результатов
    processor.print_statistics(stats)
    processor.save_results(results)

    print("\nГотово! Результаты сохранены в results.py")