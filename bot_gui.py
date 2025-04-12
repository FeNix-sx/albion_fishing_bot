from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout,
                             QWidget, QPushButton, QTextEdit, QLabel,
                             QGroupBox, QHBoxLayout, QFrame,
                             QSpinBox, QComboBox, QFormLayout,
                             QRadioButton, QButtonGroup, QStackedWidget,
                             QCheckBox, QProgressBar)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette
from PyQt5.QtWinExtras import QtWin
import ctypes
import random


class FishingBotGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.set_dark_title_bar()
        self.setup_ui()
        self.load_settings()

    def set_dark_title_bar(self):
        """Установка темной title bar для окна"""
        try:
            if hasattr(Qt, 'AA_UseStyleSheetsForTitleBar'):
                QApplication.setAttribute(Qt.AA_UseStyleSheetsForTitleBar, True)

            self.setStyleSheet("""
                QMainWindow {
                    background-color: #2b2b2b;
                    color: #ffffff;
                }
            """)

            try:
                QtWin.setCurrentProcessExplicitAppUserModelID('albion.fishing.bot')
                QtWin.enableDarkModeForWindow(self.winId(), True)
            except:
                pass

            try:
                DWMWA_USE_IMMERSIVE_DARK_MODE = 20
                hwnd = ctypes.windll.user32.GetParent(self.winId())
                value = ctypes.c_int(1)
                ctypes.windll.dwmapi.DwmSetWindowAttribute(
                    hwnd, DWMWA_USE_IMMERSIVE_DARK_MODE,
                    ctypes.byref(value), ctypes.sizeof(value)
                )
            except:
                pass
        except:
            pass

    def setup_ui(self):
        self.setWindowTitle("Albion Fishing Bot")
        self.setGeometry(100, 100, 900, 750)
        self.setup_styles()

        # Центральный виджет
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(15, 15, 15, 15)
        main_layout.setSpacing(15)

        # Контейнер настроек
        settings_container = QWidget()
        settings_layout = QHBoxLayout(settings_container)
        settings_layout.setContentsMargins(0, 0, 0, 0)
        settings_layout.setSpacing(15)

        # Общие настройки
        common_group = QGroupBox("Общие настройки")
        common_group.setMinimumWidth(400)
        common_layout = QVBoxLayout()
        common_layout.setContentsMargins(15, 20, 15, 20)

        # Разрешение экрана
        resolution_label = QLabel("Разрешение экрана:")
        resolution_label.setFont(QFont("Arial", 10, QFont.Bold))
        common_layout.addWidget(resolution_label)

        self.resolution_combo = QComboBox()
        self.resolution_combo.setFont(QFont("Arial", 10))
        self.resolution_combo.addItems([
            "1280x720 (HD)",
            "1920x1080 (Full HD)",
            "2560x1440 (2K)",
            "3840x2160 (4K)",
            "Другое..."
        ])
        common_layout.addWidget(self.resolution_combo)

        bottom_label = QLabel("выбор разрешения")
        bottom_label.setFont(QFont("Arial", 8))
        bottom_label.setAlignment(Qt.AlignRight)
        common_layout.addWidget(bottom_label)

        # Звуковое устройство с тестом
        audio_label = QLabel("Звуковое устройство:")
        audio_label.setFont(QFont("Arial", 10, QFont.Bold))
        common_layout.addWidget(audio_label)

        audio_control_layout = QHBoxLayout()

        self.audio_combo = QComboBox()
        self.audio_combo.setFont(QFont("Arial", 10))
        self.audio_combo.addItems([
            "По умолчанию",
            "Устройство 1",
            "Устройство 2",
            "Другое..."
        ])
        audio_control_layout.addWidget(self.audio_combo)

        self.test_audio_btn = QPushButton("Тест звука")
        self.test_audio_btn.setObjectName("testAudioButton")
        self.test_audio_btn.setFont(QFont("Arial", 9))
        self.test_audio_btn.setFixedWidth(100)
        audio_control_layout.addWidget(self.test_audio_btn)

        common_layout.addLayout(audio_control_layout)

        # Индикатор теста звука
        self.audio_level = QProgressBar()
        self.audio_level.setRange(0, 100)
        self.audio_level.setValue(0)
        self.audio_level.setTextVisible(False)
        self.audio_level.setFixedHeight(6)
        common_layout.addWidget(self.audio_level)

        audio_status_layout = QHBoxLayout()
        self.audio_status_label = QLabel("Устройство не проверено")
        self.audio_status_label.setFont(QFont("Arial", 8))
        self.audio_status_label.setStyleSheet("color: #aaaaaa;")

        audio_status_layout.addWidget(self.audio_status_label)
        audio_status_layout.addStretch()

        common_layout.addLayout(audio_status_layout)

        audio_bottom_label = QLabel("для распознавания звука")
        audio_bottom_label.setFont(QFont("Arial", 8))
        audio_bottom_label.setAlignment(Qt.AlignRight)
        common_layout.addWidget(audio_bottom_label)

        common_group.setLayout(common_layout)

        # Режим работы с дополнительными опциями
        mode_group = QGroupBox("Режим работы")
        mode_group.setMinimumWidth(350)
        mode_main_layout = QVBoxLayout()
        mode_main_layout.setContentsMargins(15, 20, 15, 20)

        mode_label = QLabel("Выбор режима:")
        mode_label.setFont(QFont("Arial", 10, QFont.Bold))
        mode_label.setAlignment(Qt.AlignLeft)
        mode_main_layout.addWidget(mode_label)

        mode_layout = QHBoxLayout()
        self.mode_group = QButtonGroup()
        self.mode_by_count = QRadioButton("По количеству")
        self.mode_by_time = QRadioButton("По времени")
        self.mode_by_count.setChecked(True)
        self.mode_by_count.setFont(QFont("Arial", 12))
        self.mode_by_time.setFont(QFont("Arial", 12))

        self.mode_group.addButton(self.mode_by_count, 0)
        self.mode_group.addButton(self.mode_by_time, 1)

        mode_layout.addWidget(self.mode_by_count)
        mode_layout.addWidget(self.mode_by_time)
        mode_main_layout.addLayout(mode_layout)

        type_label = QLabel("Количество/время")
        type_label.setFont(QFont("Arial", 8))
        type_label.setAlignment(Qt.AlignLeft)
        mode_main_layout.addWidget(type_label)

        self.settings_stack = QStackedWidget()

        # Настройки для режима по количеству
        self.count_settings = QWidget()
        count_layout = QFormLayout()
        self.fish_limit = QSpinBox()
        self.fish_limit.setFont(QFont("Arial", 10))
        self.fish_limit.setRange(1, 999)
        self.fish_limit.setValue(50)
        count_layout.addRow("Макс. количество:", self.fish_limit)
        self.count_settings.setLayout(count_layout)

        # Настройки для режима по времени
        self.time_settings = QWidget()
        time_layout = QFormLayout()
        self.time_limit = QSpinBox()
        self.time_limit.setFont(QFont("Arial", 10))
        self.time_limit.setRange(1, 600)
        self.time_limit.setValue(30)
        self.time_limit.setSuffix(" мин")
        time_layout.addRow("Время работы:", self.time_limit)
        self.time_settings.setLayout(time_layout)

        self.settings_stack.addWidget(self.count_settings)
        self.settings_stack.addWidget(self.time_settings)
        mode_main_layout.addWidget(self.settings_stack)

        # Дополнительные опции с красивыми галочками
        options_label = QLabel("Дополнительные опции:")
        options_label.setFont(QFont("Arial", 10, QFont.Bold))
        mode_main_layout.addWidget(options_label)

        # Чекбоксы для наживки и пирога с зелеными галочками
        self.use_bait_checkbox = QCheckBox("Использовать наживку")
        self.use_bait_checkbox.setFont(QFont("Arial", 10))
        self.use_bait_checkbox.setChecked(True)
        mode_main_layout.addWidget(self.use_bait_checkbox)

        self.use_food_checkbox = QCheckBox("Использовать пирог (кнопка 2)")
        self.use_food_checkbox.setFont(QFont("Arial", 10))
        self.use_food_checkbox.setChecked(False)
        mode_main_layout.addWidget(self.use_food_checkbox)

        mode_group.setLayout(mode_main_layout)

        # Устанавливаем соотношение ширины
        settings_layout.addWidget(common_group, stretch=6)
        settings_layout.addWidget(mode_group, stretch=4)

        # Лог работы
        log_group = QGroupBox("Лог работы")
        log_layout = QVBoxLayout()
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setFont(QFont("Consolas", 10))
        log_layout.addWidget(self.log_output)
        log_group.setLayout(log_layout)

        # Панель управления
        control_group = QGroupBox("Управление ботом")
        control_layout = QHBoxLayout()
        control_layout.setContentsMargins(15, 15, 15, 15)

        self.start_btn = QPushButton("▶ Старт рыбалки")
        self.start_btn.setObjectName("startButton")
        self.start_btn.setMinimumHeight(40)
        self.start_btn.setFont(QFont("Arial", 10, QFont.Bold))

        self.stop_btn = QPushButton("■ Остановить")
        self.stop_btn.setObjectName("stopButton")
        self.stop_btn.setEnabled(False)
        self.stop_btn.setMinimumHeight(40)
        self.stop_btn.setFont(QFont("Arial", 10, QFont.Bold))

        control_layout.addWidget(self.start_btn)
        control_layout.addWidget(self.stop_btn)
        control_group.setLayout(control_layout)

        main_layout.addWidget(settings_container)
        main_layout.addWidget(log_group)
        main_layout.addWidget(control_group)

        # Подключаем сигналы
        self.start_btn.clicked.connect(self.on_start_clicked)
        self.stop_btn.clicked.connect(self.on_stop_clicked)
        self.mode_group.buttonClicked.connect(self.on_mode_changed)
        self.resolution_combo.currentTextChanged.connect(self.on_resolution_changed)
        self.audio_combo.currentTextChanged.connect(self.on_audio_changed)
        self.use_bait_checkbox.stateChanged.connect(self.on_bait_changed)
        self.use_food_checkbox.stateChanged.connect(self.on_food_changed)
        self.test_audio_btn.clicked.connect(self.on_test_audio)

    def setup_styles(self):
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2b2b2b;
            }
            QGroupBox {
                border: 1px solid #3e3e3e;
                border-radius: 5px;
                margin-top: 10px;
                padding-top: 15px;
                color: #aaaaaa;
                font-weight: bold;
                font-size: 12px;
            }
            QTextEdit {
                background-color: #1e1e1e;
                color: #dcdcdc;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                padding: 8px;
                font-family: Consolas;
                min-height: 200px;
            }
            QPushButton {
                background-color: #3a3a3a;
                color: white;
                border: 1px solid #4a4a4a;
                border-radius: 4px;
                padding: 8px 16px;
                font-size: 14px;
            }
            QPushButton#startButton {
                background-color: #2d7d2d;
            }
            QPushButton#startButton:hover {
                background-color: #3d8d3d;
            }
            QPushButton#startButton:pressed {
                background-color: #1d6d1d;
            }
            QPushButton#stopButton {
                background-color: #7d2d2d;
            }
            QPushButton#stopButton:hover {
                background-color: #8d3d3d;
            }
            QPushButton#stopButton:pressed {
                background-color: #6d1d1d;
            }
            QPushButton#testAudioButton {
                background-color: #3a5a7a;
                padding: 5px 10px;
            }
            QPushButton#testAudioButton:hover {
                background-color: #4a6a8a;
            }
            QPushButton#testAudioButton:pressed {
                background-color: #2a4a6a;
            }
            QPushButton:disabled {
                background-color: #2a2a2a;
                color: #6a6a6a;
            }
            QComboBox, QSpinBox {
                background-color: #1e1e1e;
                color: #dcdcdc;
                border: 1px solid #3e3e3e;
                border-radius: 4px;
                padding: 5px;
                min-width: 150px;
            }
            QLabel {
                color: #aaaaaa;
                font-size: 14px;
            }
            QRadioButton {
                color: #dcdcdc;
                font-size: 14px;
                padding: 5px;
            }
            QCheckBox {
                color: #dcdcdc;
                font-size: 14px;
                padding: 5px;
                spacing: 5px;
            }
            QCheckBox::indicator {
                width: 16px;
                height: 16px;
                border: 1px solid #3e3e3e;
                border-radius: 3px;
                background: #1e1e1e;
            }
            QCheckBox::indicator:checked {
                background: #2d7d2d;
                image: url(:/qss_icons/rc/checkbox_checked.png);
            }
            QCheckBox::indicator:unchecked {
                background: #1e1e1e;
            }
            QProgressBar {
                border: 1px solid #3e3e3e;
                border-radius: 3px;
                background: #1e1e1e;
            }
            QProgressBar::chunk {
                background-color: #2d7d2d;
                border-radius: 2px;
            }
        """)

    def on_test_audio(self):
        """Тестирование звукового устройства"""
        device = self.audio_combo.currentText()
        self.log_output.append(f"Тестирование звука: {device}")

        # Симуляция теста звука
        self.audio_status_label.setText("Идет проверка звука...")
        self.audio_status_label.setStyleSheet("color: #dcdcaa;")
        self.test_audio_btn.setEnabled(False)

        # Создаем таймер для анимации индикатора
        self.test_timer = QTimer(self)
        self.test_timer.timeout.connect(self.update_audio_level)
        self.test_counter = 0
        self.test_timer.start(100)  # Обновление каждые 100 мс

        # Завершение теста через 3 секунды
        QTimer.singleShot(3000, self.finish_audio_test)

    def update_audio_level(self):
        """Обновление индикатора уровня звука"""
        self.test_counter += 1
        if self.test_counter % 10 == 0:
            # Каждую секунду меняем цвет индикатора
            color = "#dcdcaa" if (self.test_counter // 10) % 2 else "#2d7d2d"
            self.audio_status_label.setStyleSheet(f"color: {color};")

        # Случайное значение для имитации звука
        value = random.randint(0, 100)
        self.audio_level.setValue(value)

    def finish_audio_test(self):
        """Завершение теста звука"""
        self.test_timer.stop()
        self.audio_level.setValue(0)
        self.test_audio_btn.setEnabled(True)

        # Случайный результат для демонстрации
        if random.random() > 0.2:  # 80% успешных тестов
            self.audio_status_label.setText("Устройство работает нормально")
            self.audio_status_label.setStyleSheet("color: #2d7d2d;")
            self.log_output.append("Тест звука: успешно")
        else:
            self.audio_status_label.setText("Проблемы с устройством!")
            self.audio_status_label.setStyleSheet("color: #7d2d2d;")
            self.log_output.append("Тест звука: обнаружены проблемы")

    def on_mode_changed(self, button):
        """Переключение между режимами работы"""
        if button == self.mode_by_count:
            self.settings_stack.setCurrentIndex(0)
            self.log_output.append("Выбран режим: По количеству улова")
        else:
            self.settings_stack.setCurrentIndex(1)
            self.log_output.append("Выбран режим: По времени работы")

    def on_audio_changed(self, text):
        """Изменение звукового устройства"""
        self.log_output.append(f"Выбрано звуковое устройство: {text}")
        self.audio_status_label.setText("Устройство не проверено")
        self.audio_status_label.setStyleSheet("color: #aaaaaa;")

    def on_bait_changed(self, state):
        """Изменение состояния наживки"""
        status = "включена" if state == Qt.Checked else "выключена"
        self.log_output.append(f"Наживка: {status}")

    def on_food_changed(self, state):
        """Изменение состояния пирога"""
        status = "включен" if state == Qt.Checked else "выключен"
        self.log_output.append(f"Пирог: {status} (кнопка 2)")

    def load_settings(self):
        """Загрузка сохранённых настроек"""
        self.log_output.append("Настройки загружены")

    def save_settings(self):
        """Сохранение настроек"""
        mode = "По количеству" if self.mode_by_count.isChecked() else "По времени"
        resolution = self.resolution_combo.currentText()
        audio = self.audio_combo.currentText()
        bait = "Вкл" if self.use_bait_checkbox.isChecked() else "Выкл"
        food = "Вкл" if self.use_food_checkbox.isChecked() else "Выкл"

        if self.mode_by_count.isChecked():
            limit = f"Лимит: {self.fish_limit.value()} рыб"
        else:
            limit = f"Время: {self.time_limit.value()} мин"

        self.log_output.append(
            f"Сохранены настройки:\n"
            f"- Режим: {mode}\n"
            f"- {limit}\n"
            f"- Разрешение: {resolution}\n"
            f"- Звук: {audio}\n"
            f"- Наживка: {bait}\n"
            f"- Пирог: {food}"
        )

    def on_resolution_changed(self, text):
        if text == "Другое...":
            self.log_output.append("Выбрано пользовательское разрешение")

    def on_start_clicked(self):
        """Обработка нажатия кнопки Старт"""
        resolution = self.resolution_combo.currentText().split(" ")[0]
        audio = self.audio_combo.currentText()
        bait = "Да" if self.use_bait_checkbox.isChecked() else "Нет"
        food = "Да" if self.use_food_checkbox.isChecked() else "Нет"

        self.log_output.append("=== НАСТРОЙКИ РЫБАЛКИ ===")
        self.log_output.append(f"Разрешение: {resolution}")
        self.log_output.append(f"Звуковое устройство: {audio}")
        self.log_output.append(f"Наживка: {bait}")
        self.log_output.append(f"Пирог: {food}")

        if self.mode_by_count.isChecked():
            self.log_output.append(f"Режим: По количеству улова ({self.fish_limit.value()} рыб)")
        else:
            self.log_output.append(f"Режим: По времени работы ({self.time_limit.value()} мин)")

        self.log_output.append("▶ Бот запущен (заглушка)")

        # Блокируем все настройки
        self.start_btn.setEnabled(False)
        self.stop_btn.setEnabled(True)
        self.mode_by_count.setEnabled(False)
        self.mode_by_time.setEnabled(False)
        self.fish_limit.setEnabled(False)
        self.time_limit.setEnabled(False)
        self.resolution_combo.setEnabled(False)
        self.audio_combo.setEnabled(False)
        self.use_bait_checkbox.setEnabled(False)
        self.use_food_checkbox.setEnabled(False)
        self.test_audio_btn.setEnabled(False)

        self.save_settings()

    def on_stop_clicked(self):
        """Обработка нажатия кнопки Стоп"""
        self.log_output.append("■ Бот остановлен (заглушка)")

        # Разблокируем все настройки
        self.start_btn.setEnabled(True)
        self.stop_btn.setEnabled(False)
        self.mode_by_count.setEnabled(True)
        self.mode_by_time.setEnabled(True)
        self.fish_limit.setEnabled(True)
        self.time_limit.setEnabled(True)
        self.resolution_combo.setEnabled(True)
        self.audio_combo.setEnabled(True)
        self.use_bait_checkbox.setEnabled(True)
        self.use_food_checkbox.setEnabled(True)
        self.test_audio_btn.setEnabled(True)


if __name__ == "__main__":
    import sys

    app = QApplication(sys.argv)
    app.setStyle('Fusion')

    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(43, 43, 43))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(30, 30, 30))
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    app.setPalette(palette)

    window = FishingBotGUI()
    window.show()
    sys.exit(app.exec_())