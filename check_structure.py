import os

EXPECTED_STRUCTURE = {
    'img': ['float_small.jpg', 'fishing.png', 'bite.png'],
    'modules': [
        'audio_detector_single.py',
        'auto_mouse_click.py',
        'fishing_bot.py',
        'item_recognizer.py',
        'screen_divider.py',
        'utils/error_handling.py',
        'utils/image_utils.py'
    ],
    'required_root': ['main.py', 'config.json', 'template_mono.json']
}


def check_structure():
    for folder, files in EXPECTED_STRUCTURE.items():
        if folder == 'required_root':
            for file in files:
                if not os.path.exists(file):
                    print(f'[ERROR] Отсутствует файл: {file}')
            continue

        if not os.path.exists(folder):
            print(f'[ERROR] Отсутствует папка: {folder}')
            continue

        for file in files:
            path = os.path.join(folder, file)
            if not os.path.exists(path):
                print(f'[ERROR] Отсутствует файл: {path}')

    print("[OK] Проверка структуры завершена")


if __name__ == "__main__":
    check_structure()