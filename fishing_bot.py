"""
Основная логика рыбалки:
1. Поиск поплавка на экране
2. Определение момента подсечки
3. Подсчет количества пойманной рыбы
Работает с шаблоном изображения поплавка (float_small.jpg).
"""

import cv2
import numpy as np
from random import uniform, randint
from mss.windows import MSS as mss
import time
import pyautogui as pg
from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass
class ScreenResolution:
    width: int
    height: int

    @classmethod
    def get_current(cls) -> 'ScreenResolution':
        """Получение текущего разрешения экрана"""
        return cls(width=pg.size().width, height=pg.size().height)

    def get_scale_factor(self, reference_width: int = 2560, reference_height: int = 1440) -> Tuple[float, float]:
        """Получение коэффициентов масштабирования относительно референсного разрешения"""
        return (self.width / reference_width, self.height / reference_height)


@dataclass
class MonitorConfig:
    top: int
    left: int
    width: int
    height: int

    @classmethod
    def create_for_resolution(cls, screen_resolution: ScreenResolution) -> 'MonitorConfig':
        """Создание конфигурации монитора с учетом текущего разрешения"""
        scale_x, scale_y = screen_resolution.get_scale_factor()

        # Базовые значения для разрешения 2560x1440
        base_top = 700
        base_left = 1100
        base_width = 350
        base_height = 100

        return cls(
            top=int(base_top * scale_y),
            left=int(base_left * scale_x),
            width=int(base_width * scale_x),
            height=int(base_height * scale_y)
        )


class FishingBot:
    def __init__(self, template_path: str):
        self.template = cv2.imread(template_path, cv2.IMREAD_GRAYSCALE)
        self.w, self.h = self.template.shape[::-1]
        self.screen_resolution = ScreenResolution.get_current()
        self.monitor_config = MonitorConfig.create_for_resolution(self.screen_resolution)
        self.screen_capture = mss()
        self.time_list = []
        self.btn_click = False
        self.last_position: Optional[int] = None
        self.catches = 0
        self.was_float_visible = False
        self.last_float_time = None  # Время последнего обнаружения поплавка

        # Базовые значения для диапазонов нажатия (для 2560x1440)
        self.base_press_range = (190, 215)
        self.base_release_range = (220, 235)

        # print("\n🎣 Инициализация бота для рыбалки")
        # print(f"📺 Разрешение экрана: {self.screen_resolution.width}x{self.screen_resolution.height}")
        # print(f"🔍 Область поиска: {self.monitor_config.__dict__}")
        # print("-" * 50)

    def get_screen(self) -> np.ndarray:
        """Получение скриншота указанной области экрана"""
        return np.array(self.screen_capture.grab(self.monitor_config.__dict__))

    def find_float_position(self, frame: np.ndarray) -> Optional[int]:
        """Поиск позиции поплавка на кадре"""
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        res = cv2.matchTemplate(gray_frame, self.template, cv2.TM_CCOEFF_NORMED)
        loc = np.where(res >= 0.7)

        if np.size(loc) == 0:
            return None

        # Берем только первую найденную позицию
        return loc[1][0] if len(loc[1]) > 0 else None

    def get_scaled_ranges(self) -> Tuple[int, int]:
        """Получение масштабированных диапазонов для текущего разрешения"""
        scale_x, _ = self.screen_resolution.get_scale_factor()

        press_min = int(self.base_press_range[0] * scale_x)
        press_max = int(self.base_press_range[1] * scale_x)
        release_min = int(self.base_release_range[0] * scale_x)
        release_max = int(self.base_release_range[1] * scale_x)

        return (randint(press_min, press_max), randint(release_min, release_max))

    def handle_float_position(self, position: int) -> None:
        """Обработка позиции поплавка и управление кнопкой мыши"""
        self.last_position = position
        self.time_list.append(time.time())
        self.was_float_visible = True
        self.last_float_time = time.time()  # Обновляем время последнего обнаружения

        # Получаем масштабированные диапазоны
        press_range, release_range = self.get_scaled_ranges()

        if position < press_range:
            pg.mouseDown(button="left")
            self.btn_click = True
        elif position > release_range and self.btn_click:
            pg.mouseUp(button='left')
            self.btn_click = False

        time.sleep(uniform(0.02, 0.05))

    def handle_float_disappearance(self) -> None:
        """Обработка исчезновения поплавка"""
        if self.was_float_visible:
            self.catches += 1
            print(f"\n🎣 Поймал! Всего улов: {self.catches} 🐟")
            self.was_float_visible = False
            if self.btn_click:
                pg.mouseUp(button='left')
                self.btn_click = False

    def check_float_timeout(self) -> bool:
        """Проверка, не прошло ли 3 секунды с момента последнего обнаружения поплавка"""
        if self.last_float_time is None:
            self.last_float_time = time.time()  # Инициализация при первом вызове
            return False

        return (time.time() - self.last_float_time) > 3

    def run(self) -> None:
        """Основной цикл работы бота"""
        try:
            while True:
                start_time = time.time()

                # Получаем и обрабатываем кадр
                frame = self.get_screen()
                position = self.find_float_position(frame)

                # Выводим только FPS и позицию поплавка
                fps = 1 / (time.time() - start_time)
                # position_indicator = "🎯" if position is not None else "❌"
                # bite_status = "🎣 КЛЮЁТ!!!" if self.btn_click else ""

                # print(f"\rFPS: {fps:.2f} | "
                #       f"Позиция: {position_indicator} {position if position is not None else 'не найдена'} | "
                #       f"{bite_status}", end="")

                # Обрабатываем позицию поплавка или его исчезновение
                if position is not None:
                    self.handle_float_position(position)
                else:
                    self.handle_float_disappearance()
                    # Проверяем таймаут поплавка
                    if self.check_float_timeout():
                        # print("\n\n⏳ Поплавок не обнаружен более 3 секунд. Завершение работы...")
                        break
                    # Если рыба поймана, завершаем работу
                    if self.catches > 0:
                        break

                # Проверяем выход
                if cv2.waitKey(25) & 0xFF == ord("q"):
                    print("\n\n👋 Завершение работы бота...")
                    break

        finally:
            cv2.destroyAllWindows()
            self.screen_capture.close()

    def stop(self):
        """Просто устанавливает флаг для остановки (если у вас есть цикл while)."""
        self._running = False  # Предполагая, что у вас есть такой флаг

def main():
    # Создаем и запускаем бота
    bot = FishingBot("img/float_small.jpg")
    bot.run()


if __name__ == "__main__":
    main()