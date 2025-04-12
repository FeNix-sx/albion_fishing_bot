"""
Главный скрипт бота для рыбалки в Albion Online.
Координирует работу всех модулей:
1. Управление мышью (AutoMouseClick)
2. Разделение экрана (ScreenDivider)
3. Детектирование поклевки (AudioDetectorEnhanced)
4. Распознавание улова (ItemRecognizer)
5. Основная логика рыбалки (FishingBot)
Запускает интерфейс для задания цели по количеству рыб.
"""

import time
from collections import defaultdict
from audio_detector_single import AudioDetectorEnhanced
from fishing_bot import FishingBot
from auto_mouse_click import AutoMouseClick
from screen_divider import ScreenDivider
from item_recognizer import ItemRecognizer
import pyautogui
import os
import json
import logging
from datetime import datetime


# --- Настройка логирования ---
def setup_logging():
    """Создает папку logs/ и настраивает запись логов"""
    if not os.path.exists('logs'):
        os.makedirs('logs')
    logging.basicConfig(
        filename=f'logs/bot_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def log_error(error_msg, screenshot=False):
    """Логирует ошибку и при необходимости сохраняет скриншот"""
    logging.error(error_msg)
    if screenshot:
        try:
            pyautogui.screenshot(f'logs/error_{int(time.time())}.png')
        except Exception as e:
            logging.error(f"Ошибка при создании скриншота: {e}")


# Инициализация логов
setup_logging()


# --- Ваш исходный код (без изменений в логике) ---
class FishingManager:
    def __init__(self):
        self.catch_stats = defaultdict(int)
        self.recognizer = ItemRecognizer()
        logging.info("Инициализирован FishingManager")

    def print_header(self, target):
        msg = f"Цель: поймать {target} рыб"
        print(f"\n🎯 {msg}")
        logging.info(msg)
        print("❌ Для выхода нажмите Ctrl+C")
        print("-" * 50)

    def countdown(self):
        print("\n⏳ Подготовка ...")
        logging.info("Подготовка к запуску")
        for i in range(3, 0, -1):
            print(f"Начало через {i}...")
            time.sleep(1)
        print("\n🎣 Начинаем ловлю!")
        logging.info("Ловля начата")

    def process_catch(self, total, target):
        try:
            time.sleep(1.2)
            screenshot = "temp_catch.png"
            pyautogui.screenshot(screenshot)

            item_name, count, _ = self.recognizer.process_image(screenshot)
            if item_name:
                self.catch_stats[item_name] += count
                msg = f"Поймано: {item_name} ({count} шт). Всего: {total}/{target}"
                print(f"🎉 Рыба поймана! Всего: {total}/{target}")
                print(f"🐟 {msg}")
                logging.info(msg)
            else:
                msg = "Рыба поймана (не удалось распознать)"
                print("🎉 " + msg)
                logging.warning(msg)

            if os.path.exists(screenshot):
                os.remove(screenshot)
        except Exception as e:
            log_error(f"Ошибка в process_catch: {e}", screenshot=True)

    def print_summary(self):
        print("\n" + "-" * 50)
        print("Всего поймано:")
        logging.info("Итоги ловли:")
        for item, count in self.catch_stats.items():
            line = f"{item.ljust(25)} {'-' * (10 - len(str(count)))} {count} шт"
            print(line)
            logging.info(line)
        print("\n🎊 Достигнута цель! Завершение работы...")
        logging.info("Цель достигнута, завершение")


def load_config():
    try:
        with open('config.json', 'r') as f:
            return json.load(f)
    except Exception as e:
        log_error(f"Ошибка загрузки config.json: {e}")
        return None


def main():
    logging.info("=== Запуск программы ===")
    print("\n🎮 Запуск автоматической рыбалки")

    try:
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

                img_float:str = "img/float_small.jpg"
                bot = FishingBot(img_float)
                bot.run()

                if bot.catches > 0:
                    total += 1
                    manager.process_catch(total, target)

                if total < target:
                    time.sleep(3)

            except KeyboardInterrupt:
                print("\n👋 Программа остановлена пользователем")
                logging.warning("Остановка по Ctrl+C")
                break
            except Exception as e:
                log_error(f"Ошибка в основном цикле: {e}", screenshot=True)
                continue

        manager.print_summary()

    except Exception as e:
        log_error(f"Критическая ошибка: {e}", screenshot=True)
        print("⚠️ Произошла ошибка! Подробности в logs/")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Программа остановлена пользователем")
        logging.info("Принудительное завершение")
    except Exception as e:
        log_error(f"Фатальная ошибка: {e}", screenshot=True)