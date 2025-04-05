import os
import random
import time
import pyautogui
import tkinter as tk
from PIL import Image, ImageTk, ImageGrab, ImageDraw, ImageFont


class ScreenDivider:
    def __init__(self, save_folder="divided_screens"):
        self.save_folder = save_folder
        os.makedirs(self.save_folder, exist_ok=True)
        self.options = {
            1: (36, 6, 6),
            2: (42, 6, 7),
            3: (48, 6, 8),
            4: (49, 7, 7),
            5: (56, 7, 8)
        }
        self.centers = {}
        self.scan_areas = []
        self.root = None
        self.canvas = None
        self.photo = None
        self.selected_areas = set()
        self.rectangles = {}
        self.scale_factor = 1.0

    def get_grid_size(self, num_parts):
        """Определяет размеры сетки (rows x cols)"""
        for key, (parts, rows, cols) in self.options.items():
            if parts == num_parts:
                return rows, cols
        return 3, 3

    def calculate_areas(self, num_parts):
        """Вычисляет центры всех областей"""
        width, height = pyautogui.size()
        rows, cols = self.get_grid_size(num_parts)

        part_width = width / cols
        part_height = height / rows

        self.centers = {}
        counter = 1

        for i in range(rows):
            for j in range(cols):
                if counter > num_parts:
                    break
                center_x = j * part_width + part_width / 2
                center_y = i * part_height + part_height / 2
                self.centers[counter] = (center_x, center_y)
                counter += 1

    def on_click(self, event):
        """Обработчик клика по области"""
        # Находим номер области по координатам клика
        x = event.x / self.scale_factor
        y = event.y / self.scale_factor

        for num, (center_x, center_y) in self.centers.items():
            width, height = pyautogui.size()
            rows, cols = self.get_grid_size(len(self.centers))
            part_width = width / cols
            part_height = height / rows

            left = center_x - part_width / 2
            right = center_x + part_width / 2
            top = center_y - part_height / 2
            bottom = center_y + part_height / 2

            if left <= x <= right and top <= y <= bottom:
                if num in self.selected_areas:
                    self.selected_areas.remove(num)
                    self.canvas.itemconfig(self.rectangles[num], outline='red', width=2)
                else:
                    self.selected_areas.add(num)
                    self.canvas.itemconfig(self.rectangles[num], outline='green', width=4)
                break

    def show_interactive_window(self, num_parts):
        """Показывает интерактивное окно для выбора областей"""
        # Делаем скриншот
        screenshot = ImageGrab.grab()
        width, height = screenshot.size
        rows, cols = self.get_grid_size(num_parts)

        # Создаем окно просмотра
        self.root = tk.Tk()
        self.root.title("Выберите области для рыбалки (кликните по ним)")

        # Масштабируем изображение для окна
        self.scale_factor = min(800 / width, 600 / height)
        preview_size = (int(width * self.scale_factor), int(height * self.scale_factor))
        screenshot = screenshot.resize(preview_size, Image.LANCZOS)

        self.photo = ImageTk.PhotoImage(screenshot)
        self.canvas = tk.Canvas(self.root, width=preview_size[0], height=preview_size[1])
        self.canvas.create_image(0, 0, anchor=tk.NW, image=self.photo)
        self.canvas.pack()

        # Рисуем сетку и номера областей
        # part_width = width / cols * self.scale_factor
        # part_height = height / rows * self.scale_factor

        for num, (center_x, center_y) in self.centers.items():
            x1 = (center_x - width / cols / 2) * self.scale_factor
            y1 = (center_y - height / rows / 2) * self.scale_factor
            x2 = (center_x + width / cols / 2) * self.scale_factor
            y2 = (center_y + height / rows / 2) * self.scale_factor

            # Рисуем прямоугольник области
            rect = self.canvas.create_rectangle(
                x1, y1, x2, y2,
                outline='red', width=2
            )
            self.rectangles[num] = rect

            # Добавляем номер области
            self.canvas.create_text(
                (x1 + x2) / 2, (y1 + y2) / 2,
                text=str(num),
                fill='red',
                font=('Arial', 12, 'bold')
            )

        # Кнопка подтверждения
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=10)

        tk.Label(btn_frame, text="Выберите области кликом, затем нажмите Готово").pack()

        def on_done():
            self.root.quit()
            self.root.destroy()

        tk.Button(btn_frame, text="Готово", command=on_done, bg='green', fg='white').pack(pady=6)

        # Назначаем обработчик кликов
        self.canvas.bind("<Button-1>", self.on_click)

        self.root.mainloop()

        return sorted(self.selected_areas)

    def move_to_random_area(self):
        """Перемещает курсор в случайную выбранную область"""
        if not self.scan_areas:
            return

        area = random.choice(self.scan_areas)
        x, y = self.centers[area]
        pyautogui.moveTo(x, y, duration=0.3)
        print(f"Перемещение в область {area}: ({int(x)}, {int(y)})")
        time.sleep(0.5)

    def setup(self):
        """Основная настройка областей для рыбалки"""
        print("\nДоступные варианты разделения:")
        for key, (parts, rows, cols) in self.options.items():
            print(f"{key}. {parts} частей ({rows}x{cols})")

        while True:
            try:
                choice = int(input("Выберите вариант (1-8): "))
                if 1 <= choice <= 5:
                    num_parts = self.options[choice][0]
                    break
                print("Пожалуйста, введите число от 1 до 8")
            except ValueError:
                print("Ошибка: введите корректное число")

        self.calculate_areas(num_parts)

        # Показываем интерактивное окно
        print("\nОткрывается окно для выбора областей...")
        self.scan_areas = self.show_interactive_window(num_parts)

        if not self.scan_areas:
            print("Ни одна область не выбрана, будут использованы все области")
            self.scan_areas = list(range(1, num_parts + 1))

        print(f"\nВыбранные области: {self.scan_areas}")
        return self


if __name__ == "__main__":
    try:
        divider = ScreenDivider().setup()
        divider.move_to_random_area()
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        print("\nПрограмма завершена")