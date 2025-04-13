"""
Разделение экрана на зоны:
1. Определение рабочих областей для рыбалки
2. Случайный выбор зоны для клика
3. Настройка под разные разрешения экрана
Позволяет избежать детекта бота.
"""
import os
import random
import time
import pyautogui
import tkinter as tk
from PIL import Image, ImageTk, ImageGrab, ImageDraw, ImageFont


class ScreenDivider:
    def __init__(self, rows=7, cols=8):
        self.rows = rows
        self.cols = cols
        self.centers = {}
        self.scan_areas = []
        self.selected_areas = set()
        self.rectangles = {}
        self.scale_factor = 1.0
        self.colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF']
        self.screen_width, self.screen_height = pyautogui.size()
        self.window_closed = False
        self.screen_center = (self.screen_width // 2, self.screen_height // 2)
        self.max_distance = None
        self.current_delay = 0.3  # Базовая задержка

    def calculate_areas(self):
        """Разделение экрана на rows x cols равных частей с расчетом удаленности"""
        part_width = self.screen_width / self.cols
        part_height = self.screen_height / self.rows

        # Рассчитываем максимальное расстояние (до угловой зоны)
        corner_x = self.screen_width
        corner_y = 0
        self.max_distance = ((corner_x - self.screen_center[0]) ** 2 +
                             (corner_y - self.screen_center[1]) ** 2) ** 0.5

        self.centers = {}
        counter = 1
        for i in range(self.rows):
            for j in range(self.cols):
                center_x = j * part_width + part_width / 2
                center_y = i * part_height + part_height / 2

                # Рассчитываем расстояние от центра экрана до центра зоны
                distance = ((center_x - self.screen_center[0]) ** 2 +
                            (center_y - self.screen_center[1]) ** 2) ** 0.5

                # Сохраняем центр и расстояние
                self.centers[counter] = {
                    'center': (center_x, center_y),
                    'distance': distance
                }
                counter += 1

    def show_interactive_window(self):
        """Окно выбора зон с сохранением выбранных областей"""
        screenshot = ImageGrab.grab()

        self.root = tk.Tk()
        self.root.title("Выберите области для рыбалки")
        self.root.attributes('-topmost', True)
        self.root.protocol("WM_DELETE_WINDOW", self.on_window_close)

        # Масштабирование
        self.scale_factor = min(800 / self.screen_width, 600 / self.screen_height)
        preview_size = (int(self.screen_width * self.scale_factor),
                        int(self.screen_height * self.scale_factor))

        self.photo = ImageTk.PhotoImage(screenshot.resize(preview_size, Image.LANCZOS))
        self.canvas = tk.Canvas(self.root, width=preview_size[0], height=preview_size[1], cursor="hand2")
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.canvas.pack()

        # Размеры ячеек в preview
        cell_width = preview_size[0] / self.cols
        cell_height = preview_size[1] / self.rows

        # Рисуем сетку и запоминаем прямоугольники
        self.rectangles = {}
        for num in self.centers:
            col = (num - 1) % self.cols
            row = (num - 1) // self.cols

            x1 = col * cell_width
            y1 = row * cell_height
            x2 = x1 + cell_width
            y2 = y1 + cell_height

            rect = self.canvas.create_rectangle(x1, y1, x2, y2, outline='red', width=2)
            self.rectangles[num] = rect
            self.canvas.create_text((x1 + x2) / 2, (y1 + y2) / 2,
                                    text=str(num),
                                    fill='white',
                                    font=('Arial', 10, 'bold'))

        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        tk.Button(btn_frame,
                  text="Готово",
                  command=self.on_done,
                  bg='green',
                  fg='white',
                  padx=20).pack()

        self.canvas.bind("<Button-1>", self.on_click)
        self.root.mainloop()

        return sorted(self.selected_areas)

    def on_click(self, event):
        """Обработка кликов с выделением выбранных зон"""
        col = int(event.x / ((self.screen_width / self.cols) * self.scale_factor))
        row = int(event.y / ((self.screen_height / self.rows) * self.scale_factor))
        num = row * self.cols + col + 1

        if 1 <= num <= self.rows * self.cols:
            if num in self.selected_areas:
                self.selected_areas.remove(num)
                self.canvas.itemconfig(self.rectangles[num], outline='red', width=2)
            else:
                self.selected_areas.add(num)
                color = self.colors[len(self.selected_areas) % len(self.colors)]
                self.canvas.itemconfig(self.rectangles[num], outline=color, width=4)

    def on_done(self):
        """Сохранение выбранных зон при закрытии"""
        self.window_closed = True
        self.root.quit()
        self.root.destroy()

    def on_window_close(self):
        """Обработчик закрытия окна"""
        self.window_closed = True
        self.root.quit()
        self.root.destroy()

    def move_to_random_area(self):
        """Перемещение в случайную ВЫБРАННУЮ зону с расчетом задержки"""
        if not self.scan_areas:
            return None

        area = random.choice(self.scan_areas)
        zone_data = self.centers[area]
        x, y = zone_data['center']

        # Рассчитываем задержку на основе удаленности
        distance_percent = zone_data['distance'] / self.max_distance
        self.current_delay = 1.1 if distance_percent * 1.5 > 1.1 else distance_percent * 1.5  # Умножаем на коэффициент

        pyautogui.moveTo(x, y, duration=0.2)
        time.sleep(0.3)

        return self.current_delay

    def setup(self):
        """Инициализация с сохранением выбранных зон"""
        self.calculate_areas()
        print(f"\nОткрывается окно для выбора областей ({self.rows}x{self.cols})...")
        self.scan_areas = self.show_interactive_window()

        if not self.scan_areas and not self.window_closed:
            self.scan_areas = list(range(1, self.rows * self.cols + 1))
            print("Используются все области")
        elif self.scan_areas:
            print(f"Выбрано областей: {len(self.scan_areas)}")
        else:
            print("Окно закрыто без выбора, используются все области")
            self.scan_areas = list(range(1, self.rows * self.cols + 1))

        return self