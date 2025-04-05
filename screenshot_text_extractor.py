import os
import cv2
import pytesseract
import re
from collections import defaultdict

# Настройки Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Относительные координаты (ваши значения)
REL_COORDS = {
    'x1': 0.406640625,
    'x2': 0.591796875,
    'y1': 0.05277777777777778,
    'y2': 0.1076388888888889
}


def clean_text(text):
    """Очистка текста от лишних символов и артефактов OCR"""
    # Удаляем спецсимволы и цифры в начале строки
    text = re.sub(r'^[^а-яА-ЯёЁ]*', '', text.strip())
    # Удаляем лишние символы в конце (кроме цифр для количества)
    text = re.sub(r'[^а-яА-ЯёЁ0-9\s]+$', '', text)
    return text.strip()


def parse_item(text):
    """Разбирает текст на название и количество"""
    # Паттерны для поиска количества
    count_patterns = [
        r'Получено\s*(\d+)\s*шт',  # "Получено 2 шт"
        r'(\d+)\s*шт',  # "2 шт"
        r'(\d+)$'  # "2" в конце строки
    ]

    # Ищем количество
    count = None
    for pattern in count_patterns:
        match = re.search(pattern, text)
        if match:
            count = int(match.group(1))
            text = text[:match.start()].strip()
            break

    # Очищаем название
    name = clean_text(text)

    # Если название состоит из >2 слов, берем последние 2
    if name and len(name.split()) > 2:
        name = ' '.join(name.split()[-2:])

    return {'name': name, 'count': count}


def process_screenshots(folder_path):
    """Обрабатывает все скриншоты и возвращает структурированные данные"""
    results = defaultdict(list)

    for filename in os.listdir(folder_path):
        if not filename.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp')):
            continue

        filepath = os.path.join(folder_path, filename)
        img = cv2.imread(filepath)
        if img is None:
            continue

        # Вырезаем область интереса
        height, width = img.shape[:2]
        x1 = int(REL_COORDS['x1'] * width)
        x2 = int(REL_COORDS['x2'] * width)
        y1 = int(REL_COORDS['y1'] * height)
        y2 = int(REL_COORDS['y2'] * height)
        roi = img[y1:y2, x1:x2]

        # Улучшаем качество для OCR
        gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)

        # Распознаем текст
        text = pytesseract.image_to_string(thresh, lang='rus')
        item_data = parse_item(text)

        if item_data['name']:
            results[filename] = item_data

    return dict(results)


def save_to_py(data, output_file='fishing_results.py'):
    """Сохраняет данные в Python-файл"""
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# Результаты рыбалки/сбора\n")
        f.write("data = {\n")
        for filename, item in data.items():
            f.write(f'    "{filename}": {{\n')
            f.write(f'        "name": "{item["name"]}",\n')
            f.write(f'        "count": {item["count"]},\n')
            f.write('    },\n')
        f.write("}\n")


if __name__ == "__main__":
    screens_folder = 'screens'
    if not os.path.exists(screens_folder):
        print(f"Папка '{screens_folder}' не найдена!")
        exit()

    results = process_screenshots(screens_folder)
    save_to_py(results)
    print(f"Обработано {len(results)} скриншотов. Результаты сохранены в fishing_results.py")