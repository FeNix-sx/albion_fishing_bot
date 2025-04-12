import logging
import time
import os
from datetime import datetime
import pyautogui


def setup_logging():
    """Настройка логирования в папку logs/"""
    if not os.path.exists('logs'):
        os.makedirs('logs')

    logging.basicConfig(
        filename=f'logs/bot_log_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log',
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s'
    )


def log_error(error_msg, screenshot=False):
    """Логирование ошибки с опциональным скриншотом"""
    logging.error(error_msg)
    if screenshot:
        try:
            screenshot = pyautogui.screenshot()
            screenshot.save(f'logs/error_{int(time.time())}.png')
        except Exception as e:
            logging.error(f"Failed to take screenshot: {e}")