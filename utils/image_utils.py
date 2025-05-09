"""
Утилиты для работы с изображениями:
1. Поиск шаблонов на скриншоте (OpenCV)
2. Расчет схожести изображений
3. Обработка исключений при распознавании
Используется для детекта поплавка и улова.
"""

import cv2
import numpy as np
import pyautogui


def find_image_on_screen(template_path, threshold=0.8):
    screenshot = pyautogui.screenshot()
    screenshot = cv2.cvtColor(np.array(screenshot), cv2.COLOR_RGB2BGR)
    template = cv2.imread(template_path)

    result = cv2.matchTemplate(screenshot, template, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)

    if max_val >= threshold:
        return max_loc
    return None