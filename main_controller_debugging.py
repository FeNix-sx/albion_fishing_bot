import time
from modules.audio_detector import AudioDetectorEnhanced
from modules.fishing_bot import FishingBot
from modules.auto_mouse_click import AutoMouseClick
from modules.screen_divider import ScreenDivider
from modules.item_recognizer import ItemRecognizer
import pyautogui
from datetime import datetime
import os


def get_target_catches():
    """Запрашиваем количество рыб"""
    while True:
        try:
            target_catches = int(input("\n🎯 Сколько рыб нужно поймать? "))
            if target_catches > 0:
                return target_catches
            print("❌ Введите число больше 0!")
        except ValueError:
            print("❌ Пожалуйста, введите число!")


def take_item_screenshot():
    """Делает скриншот области с предметом"""
    screenshots_dir = "captured_items"
    os.makedirs(screenshots_dir, exist_ok=True)

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{screenshots_dir}/item_{timestamp}.png"

    # Делаем скриншот всей области экрана (ItemRecognizer сам вырежет нужную часть)
    pyautogui.screenshot(filename)
    return filename


def main():
    print("\n🎮 Запуск автоматической рыбалки")

    # Получаем настройки
    target_catches = get_target_catches()
    divider = ScreenDivider().setup()
    recognizer = ItemRecognizer()

    print(f"\n🎯 Цель: поймать {target_catches} рыб")
    print("\nУправление:")
    print("❌ Для выхода нажмите Ctrl+C")
    print("-" * 50)

    # Пауза перед началом
    print("\n⏳ Подготовка ...")
    for i in range(3, 0, -1):
        print(f"Начало через {i}...")
        time.sleep(1)
    print("\n🎣 Начинаем ловлю!")

    # Инициализация компонентов
    mouse_click = AutoMouseClick(min_hold_time=0.4, max_hold_time=1.1)
    detector = AudioDetectorEnhanced("template_mono.json")

    total_catches = 0
    while total_catches < target_catches:
        try:
            # Перемещаем курсор перед забросом
            divider.move_to_random_area()

            # Процесс рыбалки
            print("\n🎣 Нажатие кнопки мыши...")
            mouse_click.run()

            detector.run()

            print("\n🎯 Сигнал обнаружен! Ловлю...")
            bot = FishingBot("img/float_small.jpg")
            bot.run()

            # Обработка результата
            if bot.catches > 0:
                total_catches += 1
                print(f"\n🎉 Рыба поймана! Всего: {total_catches}/{target_catches}")

                # Делаем скриншот и распознаем предмет
                time.sleep(1.2)  # Ждем появления окна с добычей
                screenshot_path = take_item_screenshot()
                item_name, count, _ = recognizer.process_image(screenshot_path)

                if item_name:
                    print(f"🐟 Поймано: {item_name} ({count} шт)")
                else:
                    print("❌ Не удалось распознать предмет")

                # Удаляем временный файл скриншота
                try:
                    os.remove(screenshot_path)
                except:
                    pass
            else:
                print("\n❌ Рыба сорвалась!")

            if total_catches < target_catches:
                print("\n⏳ Ожидание следующего клёва...")
                time.sleep(3)

        except KeyboardInterrupt:
            print("\n\n👋 Программа остановлена пользователем")
            print(f"🎣 Итоговый улов: {total_catches} рыб")
            break
        except Exception as e:
            print(f"\n⚠️ Произошла ошибка: {str(e)}")
            time.sleep(1)

    print("\n🎊 Достигнута цель! Завершение работы...")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n👋 Программа остановлена пользователем")