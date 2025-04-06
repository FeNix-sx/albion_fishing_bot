import os
import random
import time
import pyautogui
import tkinter as tk
from PIL import Image, ImageTk, ImageGrab, ImageDraw, ImageFont


class ScreenDivider:
    def __init__(self):
        self.centers = {}
        self.scan_areas = []
        self.selected_areas = set()
        self.rectangles = {}
        self.scale_factor = 1.0
        self.colors = ['#FF0000', '#00FF00', '#0000FF', '#FFFF00', '#FF00FF', '#00FFFF']
        self.screen_width, self.screen_height = pyautogui.size()
        self.window_closed = False  # Флаг для отслеживания состояния окна

    def calculate_areas(self):
        """Фиксированное разделение на 56 частей (7x8)"""
        rows, cols = 7, 8
        part_width = self.screen_width / cols
        part_height = self.screen_height / rows

        self.centers = {}
        counter = 1

        for i in range(rows):
            for j in range(cols):
                center_x = j * part_width + part_width / 2
                center_y = i * part_height + part_height / 2
                self.centers[counter] = (center_x, center_y)
                counter += 1

    def show_interactive_window(self):
        """Окно для выбора областей с правильным закрытием"""
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

        # Рисуем сетку
        part_width = self.screen_width / 8 * self.scale_factor
        part_height = self.screen_height / 7 * self.scale_factor

        for num, (center_x, center_y) in self.centers.items():
            x1 = (center_x - self.screen_width / 16) * self.scale_factor
            y1 = (center_y - self.screen_height / 14) * self.scale_factor
            x2 = (center_x + self.screen_width / 16) * self.scale_factor
            y2 = (center_y + self.screen_height / 14) * self.scale_factor

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

    def on_done(self):
        """Обработчик кнопки Готово"""
        self.window_closed = True
        self.root.quit()
        self.root.destroy()

    def on_window_close(self):
        """Обработчик закрытия окна"""
        self.window_closed = True
        self.root.quit()
        self.root.destroy()

    def on_click(self, event):
        """Обработка кликов по областям"""
        x = event.x / self.scale_factor
        y = event.y / self.scale_factor

        part_width = self.screen_width / 8
        part_height = self.screen_height / 7

        for num, (center_x, center_y) in self.centers.items():
            if (center_x - part_width / 2 <= x <= center_x + part_width / 2 and
                    center_y - part_height / 2 <= y <= center_y + part_height / 2):

                if num in self.selected_areas:
                    self.selected_areas.remove(num)
                    self.canvas.itemconfig(self.rectangles[num], outline='red', width=2)
                else:
                    self.selected_areas.add(num)
                    color = self.colors[len(self.selected_areas) % len(self.colors)]
                    self.canvas.itemconfig(self.rectangles[num], outline=color, width=4)
                break

    def move_to_random_area(self):
        """Перемещение в случайную область"""
        if not self.scan_areas:
            return
        area = random.choice(self.scan_areas)
        x, y = self.centers[area]
        pyautogui.moveTo(x, y, duration=0.2)
        time.sleep(0.3)

    def setup(self):
        """Настройка с фиксированной сеткой 7x8"""
        self.calculate_areas()
        print("\nОткрывается окно для выбора областей...")
        self.scan_areas = self.show_interactive_window()

        if not self.scan_areas and not self.window_closed:
            self.scan_areas = list(range(1, 57))
            print("Используются все области")
        elif self.scan_areas:
            print(f"Выбрано областей: {len(self.scan_areas)}")
        else:
            print("Окно закрыто без выбора, используются все области")
            self.scan_areas = list(range(1, 57))

        return self