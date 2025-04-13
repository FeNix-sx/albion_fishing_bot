"""
Модуль автоматического клика мышью:
1. Генерирует случайные интервалы с учетом базовой задержки
2. Принимает динамический параметр задержки в run()
3. Имитирует человеческий ввод с вариативностью
"""

import random
import time
import pyautogui

class AutoMouseClick:
    def __init__(self, delta_time=0.1):
        """
        :param delta_time: Разброс вокруг базовой задержки (в секундах)
        """
        self.delta_time = delta_time

    def run(self, base_delay=0.9):
        """
        :param base_delay: Базовая задержка (будет варьироваться в пределах ±delta_time)
        """
        # Генерация конечной задержки
        hold_time = random.uniform(
            max(0.1, base_delay - self.delta_time),  # Минимум 0.1 сек
            base_delay + self.delta_time
        )

        pyautogui.mouseDown()
        time.sleep(hold_time)
        pyautogui.mouseUp()