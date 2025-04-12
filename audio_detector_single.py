"""
Детектирование поклевки по звуку:
1. Анализ аудиопотока в реальном времени
2. Сравнение с шаблоном звука (template_mono.json)
3. Определение момента подсечки
Использует пороговые значения для фильтрации шумов.
"""

import sounddevice as sd
import numpy as np
import librosa
from scipy import signal
import queue
import threading
import time
import pyautogui
import json


class AudioDetectorEnhanced:
    def __init__(self, template_json_path):
        # Ищем VB-CABLE среди устройств
        devices = sd.query_devices()
        self.device = None

        for i, device in enumerate(devices):
            if device['max_input_channels'] > 0:
                name = device['name'].lower()
                if 'cable' in name or 'vb-audio' in name:
                    self.device = i
                    print(f"Найдено виртуальное устройство: {device['name']}")
                    break

        if self.device is None:
            raise RuntimeError("VB-CABLE не найден! Проверьте установку и настройки.")

        # Загружаем шаблон из JSON
        with open(template_json_path, 'r') as f:
            template_data = json.load(f)

        self.template_audio = np.array(template_data['audio'])
        self.template_sample_rate = template_data['sample_rate']
        self.template_mfcc = np.array(template_data['mfcc'])
        self.n_fft = template_data['n_fft']
        self.hop_length = template_data['hop_length']

        print(f"Загружен шаблон из: {template_json_path}")
        print(f"Длительность шаблона: {len(self.template_audio) / self.template_sample_rate:.2f} сек")

        self.audio_queue = queue.Queue()
        self.threshold = 0.5
        self.volume_history = []
        self.detection_buffer = np.array([])
        self.buffer_size = int(self.template_sample_rate * 2)
        self.last_detection_score = 0
        self.max_detection_score = 0
        self.detection_history = []
        self.found_template = False
        self.bite_detected = False
        self.running = False
        self.stream = None
        self.process_thread = None
        self.initialized = False

        # Выводим инструкции один раз при создании объекта
        # self._print_instructions()

    def _print_instructions(self):
        """Выводим справочную информацию один раз"""
        print("\n🎣 Автоматическая рыбалка активирована!")
        print("Индикаторы в реальном времени:")
        print("Звук:   🔴 нет   🟡 слабый   🟢 хороший")
        print("Сигнал: ❌ нет   🔍 поиск    ✅ найден")
        print("Клёв:   🎣 КЛЮЁТ!!! - при обнаружении")
        print("-" * 50)

    def get_volume_indicator(self, volume):
        if volume < 0.05:
            return "🔴"
        elif volume < 0.2:
            return "🟡"
        else:
            return "🟢"

    def get_detection_indicator(self, score):
        if score == 0:
            return "❌"
        elif score > self.threshold:
            return "✅"
        else:
            return "🔍"

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(f"Статус: {status}")
            return

        volume_norm = np.linalg.norm(indata) * 10
        self.volume_history.append(volume_norm)
        self.volume_history = self.volume_history[-10:]

        has_sound = volume_norm > 0.05
        volume_indicator = self.get_volume_indicator(volume_norm)
        detection_indicator = self.get_detection_indicator(self.last_detection_score)

        # print(f"\rЗвук: {volume_indicator} | "
        #       f"Сигнал: {detection_indicator} | "
        #       f"Громкость: {volume_norm:.2f} | "
        #       f"Схожесть: {self.last_detection_score:.3f} | "
        #       f"Макс: {self.max_detection_score:.3f}", end='')

        if has_sound:
            # audio_data = indata[:, 0] if len(indata.shape) > 1 else indata  # Берётся только левый канал
            audio_data = np.mean(indata, axis=1) if len(indata.shape) > 1 else indata  # Среднее между L и R
            self.audio_queue.put(audio_data)

    def detect_template_sound(self, audio_data):
        try:
            if len(audio_data.shape) > 1:
                audio_data = np.mean(audio_data, axis=1)

            mfcc = librosa.feature.mfcc(
                y=audio_data,
                sr=self.sample_rate,
                n_mfcc=13,
                n_fft=self.n_fft,
                hop_length=self.hop_length
            )

            min_width = min(mfcc.shape[1], self.template_mfcc.shape[1])
            mfcc = mfcc[:, :min_width]
            template_mfcc = self.template_mfcc[:, :min_width]

            distance = np.mean(np.abs(mfcc - template_mfcc))
            correlation = signal.correlate(audio_data, self.template_audio, mode='valid')
            correlation_max = np.max(np.abs(correlation))

            detection_score = (1 / (distance + 1e-6)) * correlation_max * 100

            self.last_detection_score = detection_score
            self.max_detection_score = max(self.max_detection_score, detection_score)
            self.detection_history.append(detection_score)
            self.detection_history = self.detection_history[-50:]

            current_volume = np.mean(self.volume_history) if self.volume_history else 0
            return detection_score > self.threshold and current_volume > 6

        except Exception as e:
            print(f"\nОшибка при анализе звука: {str(e)}")
            return False

    def initialize(self):
        try:
            if not self.initialized:
                device_info = sd.query_devices(self.device)
                self.sample_rate = int(device_info['default_samplerate'])

                if self.template_sample_rate != self.sample_rate:
                    samples_count = int(len(self.template_audio) * self.sample_rate / self.template_sample_rate)
                    self.template_audio = signal.resample(self.template_audio, samples_count)

                    self.template_mfcc = librosa.feature.mfcc(
                        y=self.template_audio,
                        sr=self.sample_rate,
                        n_mfcc=13,
                        n_fft=self.n_fft,
                        hop_length=self.hop_length
                    )
                    self.template_sample_rate = self.sample_rate

                # print(f"\nИнициализация устройства: {device_info['name']}")
                # print(f"Частота дискретизации: {self.sample_rate} Hz")
                self.initialized = True
            return True

        except Exception as e:
            print(f"Ошибка инициализации: {str(e)}")
            return False

    def process_audio(self):
        while self.running:
            try:
                new_audio = self.audio_queue.get(timeout=1)

                if len(self.detection_buffer) == 0:
                    self.detection_buffer = new_audio
                else:
                    self.detection_buffer = np.concatenate([self.detection_buffer, new_audio])

                if len(self.detection_buffer) > self.buffer_size:
                    self.detection_buffer = self.detection_buffer[-self.buffer_size:]

                if len(self.detection_buffer) >= len(self.template_audio):
                    if self.detect_template_sound(self.detection_buffer):
                        self.found_template = True
                        self.bite_detected = True
                    else:
                        self.found_template = False

            except queue.Empty:
                continue

    def start(self):
        if not self.initialized:
            if not self.initialize():
                return False

        self.running = True
        self.process_thread = threading.Thread(target=self.process_audio)
        self.process_thread.start()

        try:
            self.stream = sd.InputStream(
                channels=2,
                samplerate=self.sample_rate,
                device=self.device,
                callback=self.audio_callback,
                blocksize=8192
            )
            self.stream.start()
            return True
        except Exception as e:
            print(f"\nОшибка запуска потока: {str(e)}")
            self.stop()
            return False

    def stop(self):
        self.running = False

        if self.stream is not None:
            self.stream.stop()
            self.stream.close()
            self.stream = None

        if self.process_thread is not None:
            self.process_thread.join()
            self.process_thread = None

        self.last_detection_score = 0
        self.bite_detected = False
        self.found_template = False
        self.detection_buffer = np.array([])
        self.volume_history = []

    def run(self):
        if not self.start():
            return False

        try:
            while self.running:
                time.sleep(0.08)
                if self.last_detection_score > 0.6:
                    print(f"\n🎣 КЛЮЁТ!!!")
                    self.stop()
                    pyautogui.mouseDown(button='left')
                    time.sleep(0.25)
                    pyautogui.mouseUp(button='left')
                    break

        except KeyboardInterrupt:
            self.stop()
        except Exception as e:
            print(f"\nОшибка: {str(e)}")
            self.stop()

        return self.bite_detected


if __name__ == "__main__":
    # Пример использования (можно тестировать прямо из файла)
    print("Запуск тестового режима...")
    detector = AudioDetectorEnhanced("template_mono.json")
    detector.run()