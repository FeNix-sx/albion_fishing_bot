"""
Главный скрипт бота для рыбалки в Albion Online.
Обновленная версия с правильным порядком применения наживки.
"""

import time
import pyautogui
import os
from collections import defaultdict
from modules.audio_detector import AudioDetectorEnhanced
from modules.fishing_bot import FishingBot
from modules.auto_mouse_click import AutoMouseClick
from modules.screen_divider import ScreenDivider
from modules.item_recognizer import ItemRecognizer
from template_finder import BaitApplier


class FishingManager:
    def __init__(self):
        self.catch_stats = defaultdict(int)
        self.recognizer = ItemRecognizer()
        self.use_bait = False
        self.bait_remaining = 0
        self.last_bait_time = None
        self.bait_applier = BaitApplier()

    def print_header(self, target):
        bait_status = " (с наживкой)" if self.use_bait else ""
        print(f"\n🎯 Цель: поймать {target} рыб{bait_status}")
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

            if self.use_bait:
                self.bait_remaining -= 1
                print(f"🪱 Наживка: осталось {self.bait_remaining}/10 рыб")
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

        if self.use_bait:
            print(f"\n🪱 Использовано наживок: {self.catch_stats.get('Наживка', 0)}")
        print("\n🎊 Достигнута цель! Завершение работы...")


def get_target_with_bait():
    """Получаем цель с проверкой на кратность 10 при использовании наживки"""
    while True:
        try:
            target = int(input("🎯 Сколько рыб нужно поймать? (кратно 10): "))
            if target % 10 == 0:
                return target
            print("⚠️ При использовании наживки укажите количество, кратное 10 (10, 20, 30...)")
        except ValueError:
            print("⚠️ Пожалуйста, введите целое число")


def ask_about_bait():
    """Спрашиваем пользователя об использовании наживки"""
    while True:
        answer = input("🪱 Использовать наживку? (да/нет): ").lower()
        if answer in ['да', 'д', 'yes', 'y']:
            return True
        elif answer in ['нет', 'н', 'no', 'n']:
            return False
        print("⚠️ Пожалуйста, ответьте 'да' или 'нет'")


def main():
    print("\n🎮 Запуск автоматической рыбалки")

    # 1. Сначала спрашиваем про наживку
    manager = FishingManager()
    manager.use_bait = ask_about_bait()

    # 2. Затем запрашиваем количество рыбы
    if manager.use_bait:
        target = get_target_with_bait()
    else:
        target = int(input("\n🎯 Сколько рыб нужно поймать? "))

    # 3. Выбор областей для рыбалки
    divider = ScreenDivider(rows=7, cols=9).setup()
    mouse_click = AutoMouseClick(delta_time=0.08)
    detector = AudioDetectorEnhanced("template_mono.json")

    # 4. Запуск с заголовком и обратным отсчетом
    manager.print_header(target)
    manager.countdown()

    # 5. Перемещение в центр экрана и клик
    screen_width, screen_height = pyautogui.size()
    center_x, center_y = screen_width // 2, screen_height // 2
    pyautogui.moveTo(center_x, center_y, duration=0.5)
    pyautogui.click()
    time.sleep(0.5)

    # 6. Применение наживки (если нужно)
    if manager.use_bait:
        if manager.bait_applier.apply_bait():
            manager.bait_remaining = 10
            manager.last_bait_time = time.time()
        else:
            print("⚠️ Не удалось применить наживку, продолжаем без нее")
            manager.use_bait = False

    # Основной цикл рыбалки
    total = 0
    while total < target:
        try:
            # Проверяем необходимость новой наживки
            if manager.use_bait and (manager.bait_remaining <= 0 or
                                     (time.time() - manager.last_bait_time) >= 600):  # 10 минут
                print("\n🪱 Наживка закончилась, применяем новую...")
                # Снова перемещаем в центр и кликаем перед применением наживки
                pyautogui.moveTo(center_x, center_y, duration=0.5)
                pyautogui.click()
                time.sleep(0.5)

                if manager.bait_applier.apply_bait():
                    manager.bait_remaining = 10
                    manager.last_bait_time = time.time()
                else:
                    print("⚠️ Не удалось применить наживку, продолжаем без нее")
                    manager.use_bait = False

            divider.move_to_random_area()
            mouse_click.run(divider.current_delay)
            detector.run()

            img: str = "img/float_small.jpg"
            bot = FishingBot(img)
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