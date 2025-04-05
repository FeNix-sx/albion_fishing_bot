import os
import random
import time
import pyautogui
from PIL import Image, ImageDraw, ImageFont, ImageGrab
from datetime import datetime


class ScreenDivider:
    def __init__(self, save_folder="divided_screens"):
        self.save_folder = save_folder
        os.makedirs(self.save_folder, exist_ok=True)
        self.options = {
            1: (9, 3, 3),
            2: (12, 3, 4),
            3: (15, 3, 5),
            4: (16, 4, 4),
            5: (20, 4, 5),
            6: (24, 4, 6),
            7: (25, 5, 5),
            8: (30, 5, 6)
        }
        self.centers = {}  # Будет хранить центры областей

    def capture_screen(self):
        """Делает скриншот всего экрана (для тестирования)"""
        return ImageGrab.grab()

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

    def show_areas_scheme(self, num_parts):
        """Показывает красивую схему областей с правильным выравниванием"""
        rows, cols = self.get_grid_size(num_parts)
        print("\nСхема областей:")

        max_num_length = len(str(num_parts))
        cell_width = max(4, max_num_length + 2)  # Минимальная ширина 4 символа

        def make_border(connector):
            return connector[0] + (("─" * cell_width) + connector[1]) * (cols - 1) + ("─" * cell_width) + connector[2]

        print(make_border("┌┬┐"))

        for i in range(rows):
            row = []
            for j in range(cols):
                num = i * cols + j + 1
                if num <= num_parts:
                    num_str = f"{num:^{cell_width}}"
                else:
                    num_str = " " * cell_width
                row.append(num_str)
            print("│" + "│".join(row) + "│")

            if i < rows - 1:
                print(make_border("├┼┤"))

        print(make_border("└┴┘"))

    def get_areas_to_scan(self, num_parts):
        """Запрашивает у пользователя какие области сканировать"""
        self.show_areas_scheme(num_parts)
        print("\nВведите номера областей через пробел (например: 1 3 5)")
        print("Или нажмите Enter для сканирования всех областей")

        while True:
            try:
                choice = input("Выберите области: ").strip()
                if not choice:
                    return list(range(1, num_parts + 1))

                areas = list(map(int, choice.split()))
                if all(1 <= a <= num_parts for a in areas):
                    return areas

                print(f"Ошибка: номера должны быть от 1 до {num_parts}")
            except ValueError:
                print("Ошибка: введите числа через пробел")

    def scan_areas(self, areas):
        """Перемещает курсор по указанным областям один раз"""
        print("\nНачинаем сканирование областей...")

        # Перемешиваем области для случайного порядка
        random.shuffle(areas)

        for area in areas:
            x, y = self.centers[area]
            pyautogui.moveTo(x, y, duration=0.5)
            print(f"Область {area}: ({int(x)}, {int(y)})")
            time.sleep(1)

        print("\nВсе выбранные области были посещены.")
        print("Программа завершает работу.")

    def save_screenshot_with_grid(self, num_parts):
        """Создает скриншот с разметкой (для тестирования)"""
        screenshot = self.capture_screen()
        draw = ImageDraw.Draw(screenshot)
        width, height = screenshot.size
        rows, cols = self.get_grid_size(num_parts)

        font_size = min(width, height) // 25
        try:
            font = ImageFont.truetype("arial.ttf", font_size)
        except:
            font = ImageFont.load_default()

        # Рисуем границы
        border_width = max(1, int(min(width, height) / 500))
        part_width = width / cols
        part_height = height / rows

        for i in range(1, cols):
            x = i * part_width
            draw.line([(x, 0), (x, height)], fill="red", width=border_width)

        for i in range(1, rows):
            y = i * part_height
            draw.line([(0, y), (width, y)], fill="red", width=border_width)

        # Номера областей
        for num, (x, y) in self.centers.items():
            draw.text((x, y), str(num), fill="red", font=font, anchor="mm")

        # Сохраняем
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"screen_{num_parts}parts_{timestamp}.png"
        save_path = os.path.join(self.save_folder, filename)
        screenshot.save(save_path)
        print(f"\nСкриншот с разметкой сохранен: {save_path}")

    def run(self):
        """Основной метод"""
        print("Программа разделения экрана на области")

        # Выбор количества областей
        print("\nДоступные варианты разделения:")
        for key, (parts, rows, cols) in self.options.items():
            print(f"{key}. {parts} частей ({rows}x{cols})")

        while True:
            try:
                choice = int(input("Выберите вариант (1-8): "))
                if 1 <= choice <= 8:
                    num_parts = self.options[choice][0]
                    break
                print("Пожалуйста, введите число от 1 до 8")
            except ValueError:
                print("Ошибка: введите корректное число")

        # Вычисляем центры областей
        self.calculate_areas(num_parts)

        # Запрос областей для сканирования
        areas_to_scan = self.get_areas_to_scan(num_parts)

        # Дополнительная функция: сохранение скриншота с разметкой
        save = input("\nСоздать скриншот с разметкой? (y/n): ").lower()
        if save == 'y':
            self.save_screenshot_with_grid(num_parts)

        # Начинаем сканирование
        input("\nНажмите Enter чтобы начать сканирование...")
        self.scan_areas(areas_to_scan)


if __name__ == "__main__":
    try:
        divider = ScreenDivider()
        divider.run()
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        print("\nПрограмма завершена")