'''
Этот скрипт представляет собой приложение для выбора фрагмента изображения и его сохранения.
Он позволяет пользователю открывать изображения, выбрать фрагмент с помощью мыши и сохранить его.

Инструкция по использованию:
Запустите программу

Нажмите "Открыть изображение" и выберите файл

Нажмите левую кнопку мыши на изображении и, не отпуская, выделите нужный фрагмент

Отпустите кнопку мыши - выделенный фрагмент увеличится для просмотра

Если фрагмент вас устраивает, нажмите "Сохранить фрагмент"

Если хотите выбрать другой фрагмент, нажмите "Выбрать заново"

'''
import sys
import cv2
import numpy as np
from PyQt5.QtWidgets import (QApplication, QMainWindow, QLabel, QVBoxLayout,
                             QWidget, QPushButton, QFileDialog, QMessageBox)
from PyQt5.QtGui import QPixmap, QImage, QPainter, QPen, QColor
from PyQt5.QtCore import Qt, QRect


class ImageSelector(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Выбор фрагмента изображения")
        self.setGeometry(100, 100, 800, 600)

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)

        self.layout = QVBoxLayout()
        self.central_widget.setLayout(self.layout)

        self.image_label = QLabel()
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setMouseTracking(True)
        self.layout.addWidget(self.image_label)

        self.button_layout = QVBoxLayout()
        self.layout.addLayout(self.button_layout)

        self.open_button = QPushButton("Открыть изображение")
        self.open_button.clicked.connect(self.open_image)
        self.button_layout.addWidget(self.open_button)

        self.save_button = QPushButton("Сохранить фрагмент")
        self.save_button.clicked.connect(self.save_cropped)
        self.save_button.setEnabled(False)
        self.button_layout.addWidget(self.save_button)

        self.retry_button = QPushButton("Выбрать заново")
        self.retry_button.clicked.connect(self.retry_selection)
        self.retry_button.setEnabled(False)
        self.button_layout.addWidget(self.retry_button)

        self.image = None
        self.display_image = None
        self.cropped_image = None
        self.selection_start = None
        self.selection_end = None
        self.drawing = False
        self.scale_factor = 1.0
        self.image_pos = QRect()  # Позиция и размер отображаемого изображения

    def open_image(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Открыть изображение", "",
                                                   "Image Files (*.png *.jpg *.jpeg *.bmp)")
        if file_path:
            self.image = cv2.imread(file_path)
            if self.image is not None:
                self.display_image = self.image.copy()
                self.show_image(self.display_image)
                self.save_button.setEnabled(False)
                self.retry_button.setEnabled(False)

    def show_image(self, image):
        height, width, channel = image.shape
        bytes_per_line = 3 * width
        q_img = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
        pixmap = QPixmap.fromImage(q_img)

        # Сохраняем масштаб и позицию изображения
        scaled_pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
        self.scale_factor = min(self.image_label.width() / width, self.image_label.height() / height)

        # Вычисляем позицию изображения по центру
        x = (self.image_label.width() - scaled_pixmap.width()) // 2
        y = (self.image_label.height() - scaled_pixmap.height()) // 2
        self.image_pos = QRect(x, y, scaled_pixmap.width(), scaled_pixmap.height())

        self.image_label.setPixmap(scaled_pixmap)

    def mousePressEvent(self, event):
        if self.image is not None and event.button() == Qt.LeftButton:
            if self.image_pos.contains(event.pos()):
                self.drawing = True
                # Преобразуем координаты мыши в координаты изображения
                x = int((event.pos().x() - self.image_pos.x()) / self.scale_factor)
                y = int((event.pos().y() - self.image_pos.y()) / self.scale_factor)
                self.selection_start = (x, y)
                self.selection_end = (x, y)
                self.draw_selection()

    def mouseMoveEvent(self, event):
        if self.drawing and self.image is not None:
            if self.image_pos.contains(event.pos()):
                # Преобразуем координаты мыши в координаты изображения
                x = int((event.pos().x() - self.image_pos.x()) / self.scale_factor)
                y = int((event.pos().y() - self.image_pos.y()) / self.scale_factor)
                self.selection_end = (x, y)
                self.draw_selection()

    def mouseReleaseEvent(self, event):
        if self.drawing and event.button() == Qt.LeftButton and self.image is not None:
            self.drawing = False
            if self.image_pos.contains(event.pos()):
                # Преобразуем координаты мыши в координаты изображения
                x = int((event.pos().x() - self.image_pos.x()) / self.scale_factor)
                y = int((event.pos().y() - self.image_pos.y()) / self.scale_factor)
                self.selection_end = (x, y)
                self.crop_image()

    def draw_selection(self):
        if self.selection_start and self.selection_end:
            img_copy = self.image.copy()
            cv2.rectangle(img_copy, self.selection_start, self.selection_end, (0, 255, 0), 2)

            # Создаем QPixmap с выделением
            height, width, channel = img_copy.shape
            bytes_per_line = 3 * width
            q_img = QImage(img_copy.data, width, height, bytes_per_line, QImage.Format_RGB888).rgbSwapped()
            pixmap = QPixmap.fromImage(q_img)

            # Масштабируем обратно к размеру виджета
            scaled_pixmap = pixmap.scaled(self.image_label.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)
            self.image_label.setPixmap(scaled_pixmap)

    def crop_image(self):
        if self.selection_start and self.selection_end:
            x1, y1 = self.selection_start
            x2, y2 = self.selection_end

            # Убедимся, что x1 < x2 и y1 < y2
            x1, x2 = min(x1, x2), max(x1, x2)
            y1, y2 = min(y1, y2), max(y1, y2)

            # Проверим, что выделение не нулевое
            if x2 - x1 > 0 and y2 - y1 > 0:
                self.cropped_image = self.image[y1:y2, x1:x2]
                self.show_cropped_image()
                self.save_button.setEnabled(True)
                self.retry_button.setEnabled(True)

    def show_cropped_image(self):
        if self.cropped_image is not None:
            # Увеличиваем изображение для лучшего просмотра
            height, width = self.cropped_image.shape[:2]
            scale = min(600 / width, 600 / height)
            resized = cv2.resize(self.cropped_image, (int(width * scale), int(height * scale)))
            self.show_image(resized)

    def save_cropped(self):
        if self.cropped_image is not None:
            file_path, _ = QFileDialog.getSaveFileName(self, "Сохранить фрагмент", "",
                                                       "PNG Image (*.png);;JPEG Image (*.jpg *.jpeg)")
            if file_path:
                cv2.imwrite(file_path, self.cropped_image)
                QMessageBox.information(self, "Сохранено", "Фрагмент успешно сохранен!")

    def retry_selection(self):
        if self.image is not None:
            self.show_image(self.image)
            self.save_button.setEnabled(False)
            self.retry_button.setEnabled(False)
            self.cropped_image = None
            self.selection_start = None
            self.selection_end = None


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ImageSelector()
    window.show()
    sys.exit(app.exec_())