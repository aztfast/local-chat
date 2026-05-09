import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLineEdit,
    QTextEdit, QPushButton, QMessageBox, QLabel, QHBoxLayout, QFormLayout
)
from PyQt6.QtCore import pyqtSignal
import requests


class Client(QWidget):
    def __init__(self,):
        super().__init__()
        self.for_connect = None
        self.is_connect = None
        self.user = "Aztfast"
        self.init_ui()
        self.connect_to_server()

    def init_ui(self):
        layout = QVBoxLayout()

        # Заголовок
        title = QLabel("Клиент для общения с сервером")
        title.setStyleSheet("font-weight: bold; font-size: 14px;")
        layout.addWidget(title)

        # Форма для ввода хоста и порта
        config_layout = QFormLayout()
        
        self._input = QLineEdit(self)
        self._input.setPlaceholderText("Введите сервер")
        config_layout.addRow("Хост:", self._input)

        layout.addLayout(config_layout)

        # Статус соединения
        self.status_label = QLabel("Статус: не подключено")
        self.status_label.setStyleSheet("color: red;")
        layout.addWidget(self.status_label)

        # Поле ввода сообщения
        input_layout = QHBoxLayout()
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText("Введите сообщение и нажмите Enter или «Отправить»")
        self.input_field.returnPressed.connect(self.send_message)
        input_layout.addWidget(self.input_field)

        self.send_button = QPushButton("Отправить")
        self.send_button.clicked.connect(self.send_message)
        input_layout.addWidget(self.send_button)
        layout.addLayout(input_layout)

        # Область вывода сообщений
        self.output_field = QTextEdit()
        self.output_field.setReadOnly(True)
        self.output_field.setPlaceholderText("История сообщений...\n(подключения, сообщения, ошибки)")
        self.output_field.setMinimumHeight(200)
        layout.addWidget(self.output_field)


        # Кнопки управления
        btn_layout = QHBoxLayout()
        
        self.connect_btn = QPushButton("Подключить")
        self.connect_btn.clicked.connect(self.connect_to_server)
        btn_layout.addWidget(self.connect_btn)


        self.reconnect_btn = QPushButton("Переподключиться")
        self.reconnect_btn.clicked.connect(self.reconnect)
        self.reconnect_btn.setEnabled(False)
        btn_layout.addWidget(self.reconnect_btn)

        layout.addLayout(btn_layout)


        self.setLayout(layout)
        self.setWindowTitle("Клиент")
        self.resize(500, 450)

        # Стили
        self.setStyleSheet("""
            QPushButton { min-width: 100px; padding: 5px; }
            QLineEdit { padding: 3px; }
            QFormLayout { margin-bottom: 10px; }
        """)

    def connect_to_server(self):
        try:
            if self._input.text() == "":
                return
            self.for_connect = f"{self._input.text()}"
            self.is_connect = requests.get(self.for_connect + "/try_connect")
            if self.is_connect.status_code == 200: #http://192.168.0.102:5050
                self.status_label.setStyleSheet("color: green;")
                self.status_label.setText("Статус: подключено")
                self.get_message()
            else:
                self.status_label.setStyleSheet("color: red;")
                self.status_label.setText("Статус: не подключено")
        except Exception as e:
            print(e, 11)
            self.status_label.setStyleSheet("color: red;")
            self.status_label.setText("Статус: не подключено")

    
    def get_message(self):
        if not self.is_connect:
            return
        try:
            response = requests.get(self.for_connect, timeout=5)
            if response.status_code == 200:
                messages_data = response.json()
                print(messages_data)
                self.output_field.clear()
                for nickname, text in messages_data:
                    self.output_field.append(f"{nickname}: {text}")
            else:
                self.output_field.append(f"Ошибка получения сообщений: код {response.status_code}")
        except requests.exceptions.RequestException as e:
            self.output_field.append(f"Ошибка сети при получении сообщений: {e}")
            self.reconnect()
        except Exception as e:
            self.output_field.append(f"Неожиданная ошибка при получении сообщений: {e}")

    def reconnect(self):
        print("Переподключение...")
        pass

    def send_message(self):
        if not self.is_connect:
            QMessageBox.warning(self, "Ошибка", "Сначала подключитесь к серверу")
            return
        try:
            text = self.input_field.text().strip()
            if not text:
                return
            response = requests.post(
                url=self.for_connect,
                json={"nickname": self.user, "text": text},
                timeout=5
            )
            if response.status_code == 200:
                self.input_field.clear()
                self.get_message()
            else:
                QMessageBox.critical(
                    self,
                    "Ошибка отправки",
                    f"Сервер вернул код ошибки: {response.status_code}"
                )
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Ошибка сети", f"Не удалось отправить сообщение: {e}")
            self.reconnect()
        except Exception as e:
            QMessageBox.critical(self, "Ошибка", f"Неожиданная ошибка: {e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    client = Client()
    client.show()
    sys.exit(app.exec())
