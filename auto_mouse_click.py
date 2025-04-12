"""
Модуль автоматического клика мышью:
1. Случайные интервалы между кликами
2. Разное время удержания кнопки
3. Имитация человеческого ввода
Настраивается через min_hold_time/max_hold_time.
"""

import win32api
import time
import random

class AutoMouseClick:
    def __init__(self, min_hold_time=0.2, max_hold_time=1.165):
        self.min_hold_time = min_hold_time
        self.max_hold_time = max_hold_time
        # print("\n🎮 Инициализация автоматического нажатия кнопки мыши")
        # print(f"Интервал удержания: от {self.min_hold_time} до {self.max_hold_time} сек")
        print("-" * 50)

    def run(self):
        # Генерируем случайное время удержания
        hold_time = random.uniform(self.min_hold_time, self.max_hold_time)
        # print(f"🎣 Заброска: {hold_time:.3f} сек")

        # Нажимаем левую кнопку мыши
        win32api.mouse_event(0x0002, 0, 0, 0, 0)  # Нажатие

        # Ждем заданное время
        time.sleep(hold_time)

        # Отпускаем кнопку
        win32api.mouse_event(0x0004, 0, 0, 0, 0)  # Отпускание

        # print("\n👋 Закинул удочку")

if __name__ == "__main__":
    # Пример использования
    mouse_click = AutoMouseClick()
    mouse_click.run()