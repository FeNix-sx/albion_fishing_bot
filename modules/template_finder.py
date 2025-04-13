"""
=== Advanced Template Finder ===

Класс для автоматического поиска графических шаблонов на экране
с последующим плавным перемещением курсора и возможностью
динамической смены шаблонов во время выполнения.
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
        Инициализация объекта для поиска шаблонов

        Параметры:
            threshold: float - порог уверенности совпадения (0.0-1.0)
            scales: List[float] - диапазон масштабов для поиска
        """
        self.threshold = threshold
        self.scales = scales or [0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3]
        self._templates = []

    @property
    def templates(self) -> List[str]:
        """Возвращает текущий список путей к шаблонам"""
        return self._templates

    @templates.setter
    def templates(self, template_paths: List[str]):
        """
        Устанавливает новые шаблоны для поиска с валидацией

        Параметры:
            template_paths: List[str] - список путей к файлам шаблонов

        Исключения:
            ValueError: если список пустой
            FileNotFoundError: если файл не существует
        """
        if not template_paths:
            raise ValueError("Необходимо указать хотя бы один шаблон")

        for path in template_paths:
            if not os.path.exists(path):
                raise FileNotFoundError(f"Файл шаблона не найден: {path}")

        self._templates = template_paths

    def _find_best_match(self, screen: np.ndarray) -> Optional[Tuple[Tuple[int, int], Dict]]:
        """
        Основной метод поиска шаблона на изображении экрана

        Параметры:
            screen: np.ndarray - скриншот в формате OpenCV

        Возвращает:
            Tuple[Tuple[int, int], Dict] - координаты центра и метаданные
            None - если совпадений не найдено
        """
        for template_path in self._templates:
            try:
                template = cv2.imread(template_path, cv2.IMREAD_COLOR)
                if template is None:
                    continue

                h, w = template.shape[:2]

                # Поиск по всем указанным масштабам
                for scale in self.scales:
                    scaled_w = int(w * scale)
                    scaled_h = int(h * scale)

                    # Пропускаем слишком маленькие шаблоны
                    if scaled_w < 5 or scaled_h < 5:
                        continue

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
                                'confidence': round(max_val, 4),
                                'scale': round(scale, 2),
                                'position': (center_x, center_y),
                                'size': (scaled_w, scaled_h)
                            }
                        )

            except Exception as e:
                print(f"Ошибка при обработке шаблона {template_path}: {str(e)}")
                continue

        return None

    def find_and_move(self, delay: float = 0, verbose: bool = True) -> Optional[Dict]:
        """
        Поиск шаблона и перемещение курсора

        Параметры:
            delay: float - задержка перед поиском в секундах
            verbose: bool - вывод подробной информации

        Возвращает:
            Dict - метаданные найденного шаблона
            None - если шаблон не найден
        """
        if not self._templates:
            raise ValueError("Список шаблонов не задан")

        if delay > 0:
            time.sleep(delay)

        try:
            # Делаем скриншот и конвертируем в OpenCV формат
            screenshot = pyautogui.screenshot()
            screen = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
        except Exception as e:
            print(f"Ошибка при создании скриншота: {str(e)}")
            return None

        result = self._find_best_match(screen)

        if result:
            (target_x, target_y), match_info = result
            current_x, current_y = pyautogui.position()

            # Рассчитываем параметры перемещения
            distance = math.sqrt((target_x - current_x)**2 + (target_y - current_y)**2)
            duration = min(max(0.1, distance / 1000), 0.3)  # Оптимальное время

            if verbose:
                print(f"\nНайден шаблон: {match_info['template']}")
                print(f"Уверенность: {match_info['confidence']*100:.1f}%")
                print(f"Масштаб: {match_info['scale']}x")
                print(f"Координаты: {match_info['position']}")
                print(f"Перемещение: {distance:.0f} px за {duration:.2f} сек")

            # Плавное перемещение курсора
            pyautogui.moveTo(target_x, target_y, duration=duration)

            return match_info

        if verbose:
            print("\nШаблоны не найдены:")
            print(" - " + "\n - ".join(os.path.basename(p) for p in self._templates))
            print(f"Порог: {self.threshold}, Масштабы: {self.scales}")

        return None


# template_finder.py
class BaitApplier:
    """Класс для применения наживки в Albion Online"""

    def __init__(self, threshold: float = 0.8):
        self.finder = TemplateFinder(threshold=threshold)

    def apply_bait(self) -> bool:
        """Полный процесс применения наживки"""
        try:
            # 1. Открываем окно инвентаря
            pyautogui.press('i')
            time.sleep(1)  # Даем время на открытие окна

            # 2. Поиск и клик по наживке
            self.finder.templates = [
                'img/bait.png',
                'img/bait_low.png',
                'img/bait_small.png',
                'img/bait_small_low.png'
            ]
            if not self.finder.find_and_move(delay=0.5):
                print("Не удалось найти наживку в инвентаре")
                return False

            pyautogui.click()
            time.sleep(0.5)

            # 3. Подтверждение использования
            self.finder.templates = [
                'img/use_bait.png',
                'img/use_bait_small.png'
            ]
            if not self.finder.find_and_move(delay=0.5):
                print("Не удалось найти окно подтверждения")
                return False

            # 4. Клик по кнопке использования
            self.finder.templates = [
                'img/use_the_bait.png',
                'img/use_the_bait_small.png'
            ]
            if not self.finder.find_and_move(delay=0.5):
                print("Не удалось найти кнопку применения")
                return False

            pyautogui.click()
            time.sleep(0.5)

            # 5. Закрываем окно
            pyautogui.press('esc')
            time.sleep(0.5)

            print("🪱 Наживка успешно применена!")
            return True

        except Exception as e:
            print(f"Ошибка при применении наживки: {str(e)}")
            return False


def main():
    """Демонстрация работы TemplateFinder и BaitApplier"""
    print("=== Демонстрация работы ===")

    # Демонстрация TemplateFinder
    finder = TemplateFinder(threshold=0.8)
    finder.templates = ['img/bait.png']
    result = finder.find_and_move()

    # Демонстрация BaitApplier
    bait_applier = BaitApplier()
    if bait_applier.apply_bait():
        print("Наживка успешно применена!")
    else:
        print("Не удалось применить наживку")


if __name__ == "__main__":
    main()