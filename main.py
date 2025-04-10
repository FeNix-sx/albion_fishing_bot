import time
from collections import defaultdict
from audio_detector_single import AudioDetectorEnhanced
from fishing_bot import FishingBot
from auto_mouse_click import AutoMouseClick
from screen_divider import ScreenDivider
from item_recognizer import ItemRecognizer
import pyautogui
import os


class FishingManager:
    def __init__(self):
        self.catch_stats = defaultdict(int)
        self.recognizer = ItemRecognizer()

    def print_header(self, target):
        print(f"\n🎯 Цель: поймать {target} рыб")
        print("❌ Для выхода нажмите Ctrl+C")
        print("-" * 50)

    def countdown(self):
        print("\n⏳ Подготовка ...")
        for i in range(3, 0, -1):
            print(f"Начало через {i}...")
            time.sleep(1)
        print("\n🎣 Начинаем ловлю!")

    def process_catch(self, total, target):
        time.sleep(1.2)
        screenshot = "temp_catch.png"
        pyautogui.screenshot(screenshot)

        item_name, count, _ = self.recognizer.process_image(screenshot)
        if item_name:
            self.catch_stats[item_name] += count
            print(f"🎉 Рыба поймана! Всего: {total}/{target}")
            print(f"🐟 Поймано: {item_name} ({count} шт)")
        else:
            print("🎉 Рыба поймана! (не удалось распознать)")

        try:
            os.remove(screenshot)
        except:
            pass

    def print_summary(self):
        print("\n" + "-" * 50)
        print("Всего поймано:")
        for item, count in self.catch_stats.items():
            print(f"{item.ljust(25)} {'-' * (10 - len(str(count)))} {count} шт")
        print("\n🎊 Достигнута цель! Завершение работы...")


def main():
    print("\n🎮 Запуск автоматической рыбалки")
    target = int(input("\n🎯 Сколько рыб нужно поймать? "))

    manager = FishingManager()
    divider = ScreenDivider().setup()
    mouse_click = AutoMouseClick(min_hold_time=0.4, max_hold_time=1.1)
    detector = AudioDetectorEnhanced("template_mono.json")

    manager.print_header(target)
    manager.countdown()

    total = 0
    while total < target:
        try:
            divider.move_to_random_area()
            mouse_click.run()
            detector.run()

            bot = FishingBot("float_small.jpg")
            bot.run()

            if bot.catches > 0:
                total += 1
                manager.process_catch(total, target)

            if total < target:
                time.sleep(3)

        except KeyboardInterrupt:
            print("\n👋 Программа остановлена пользователем")
            break

    manager.print_summary()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Программа остановлена пользователем")