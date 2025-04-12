"""
=== Dynamic Template Finder ===

Класс для поиска шаблонов с возможностью динамического изменения списка шаблонов
"""

import cv2
import numpy as np
import pyautogui
import time
import os
import math
from typing import List, Tuple, Optional, Dict

class TemplateFinder:
    def __init__(self, threshold: float = 0.8, scales: List[float] = None):
        """
        Инициализация поисковика шаблонов

        :param threshold: Порог совпадения (0.0-1.0)
        :param scales: Диапазон масштабов для поиска
        """
        self.threshold = threshold
        self.scales = scales or [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]
        self._templates = []

    @property
    def templates(self) -> List[str]:
        """Получить текущий список шаблонов"""
        return self._templates

    @templates.setter
    def templates(self, template_paths: List[str]):
        """Установить новый список шаблонов"""
        if not template_paths:
            raise ValueError("Список шаблонов не может быть пустым")

        for path in template_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Файл шаблона не найден: {path}")

        self._templates = template_paths

    def _find_best_match(self, screen: np.ndarray) -> Optional[Tuple[Tuple[int, int], Dict]]:
        """Поиск лучшего совпадения среди всех шаблонов"""
        for template_path in self._templates:
            try:
                template = cv2.imread(template_path)
                if template is None:
                    continue

                h, w = template.shape[:2]

                for scale in self.scales:
                    scaled_w = int(w * scale)
                    scaled_h = int(h * scale)
                    resized = cv2.resize(template, (scaled_w, scaled_h))

                    result = cv2.matchTemplate(screen, resized, cv2.TM_CCOEFF_NORMED)
                    _, max_val, _, max_loc = cv2.minMaxLoc(result)

                    if max_val >= self.threshold:
                        center_x = max_loc[0] + scaled_w // 2
                        center_y = max_loc[1] + scaled_h // 2
                        return (
                            (center_x, center_y),
                            {
                                'template': os.path.basename(template_path),
                                'confidence': max_val,
                                'position': (center_x, center_y)
                            }
                        )

            except Exception:
                continue

        return None

    def find_and_move(self, delay: float = 0) -> Optional[Dict]:
        """
        Поиск шаблона и плавное перемещение курсора

        :param delay: Задержка перед поиском (секунды)
        :return: Информация о найденном шаблоне или None
        """
        if not self._templates:
            raise ValueError("Список шаблонов не задан")

        if delay > 0:
            time.sleep(delay)

        try:
            screen = cv2.cvtColor(np.array(pyautogui.screenshot()), cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"Ошибка при создании скриншота: {str(e)}")
            return None

        result = self._find_best_match(screen)

        if result:
            (target_x, target_y), match_info = result
            current_x, current_y = pyautogui.position()

            # Рассчитываем расстояние и время перемещения
            distance = math.sqrt((target_x - current_x) ** 2 + (target_y - current_y) ** 2)
            duration = min(max(0.15, distance / 1500), 0.01)  # Быстро, но не мгновенно

            # Параметры для плавности
            steps = max(int(distance / 10), 5)
            sleep_time = duration / steps

            for step in range(1, steps + 1):
                # Квадратичная интерполяция для плавности
                t = step / steps
                progress = t * t  # Ускорение в начале

                x = int(current_x + (target_x - current_x) * progress)
                y = int(current_y + (target_y - current_y) * progress)
                pyautogui.moveTo(x, y)
                print(sleep_time, duration, steps)
                time.sleep(sleep_time)

            return match_info

        return None


# Пример использования
if __name__ == "__main__":
    # 1. Создаем экземпляр
    finder = TemplateFinder(threshold=0.8)

    # 2. Первый поиск (приманка)
    print("=== Поиск приманки ===")
    finder.templates = [
        'templates/bait.png',
        'templates/bait_low.png',
        'templates/bait_small.png',
        'templates/bait_small_low.png'
    ]

    bait_result = finder.find_and_move(delay=1)
    if bait_result:
        print(f"Найдена приманка: {bait_result['template']}")
        pyautogui.click()
    else:
        print("Приманка не найдена")

    # 3. Второй поиск (крючок)
    print("\n=== Поиск крючка ===")
    finder.templates = [
        'templates/hook.png',
        'templates/hook_alt.png'
    ]

    hook_result = finder.find_and_move(delay=1)
    if hook_result:
        print(f"Найден крючок: {hook_result['template']}")
        pyautogui.click()
    else:
        print("Крючок не найден")