import sys
import asyncio
import random
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel,
    QLineEdit, QPushButton, QFileDialog
)
from telethon import TelegramClient

class CommentBot(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Telegram Комментатор")
        self.resize(400, 300)

        self.api_id = 13959415
        self.api_hash = '3f02e6c5a0d9c7438fc27153a8d70a92'
        self.session_name = "comment_session"
        self.comments = []

        layout = QVBoxLayout()

        self.link_input = QLineEdit()
        self.link_input.setPlaceholderText("Ссылка на пост Telegram")
        layout.addWidget(self.link_input)

        self.interval_input = QLineEdit()
        self.interval_input.setPlaceholderText("Интервал (например 5-10 секунд)")
        layout.addWidget(self.interval_input)

        self.load_btn = QPushButton("Загрузить comments.txt")
        self.load_btn.clicked.connect(self.load_comments)
        layout.addWidget(self.load_btn)

        self.start_btn = QPushButton("Старт")
        self.start_btn.clicked.connect(self.start_bot)
        layout.addWidget(self.start_btn)

        self.status_label = QLabel("Ожидание запуска...")
        layout.addWidget(self.status_label)

        self.setLayout(layout)

    def load_comments(self):
        path, _ = QFileDialog.getOpenFileName(self, "Выбери файл comments.txt", "", "Text Files (*.txt)")
        if path:
            with open(path, "r", encoding="utf-8") as f:
                self.comments = [line.strip() for line in f if line.strip()]
            self.status_label.setText(f"Загружено {len(self.comments)} комментариев")

    def start_bot(self):
        post_url = self.link_input.text().strip()
        interval = self.interval_input.text().strip()

        if not post_url or not interval or not self.comments:
            self.status_label.setText("Заполни все поля и загрузи комментарии")
            return

        if '-' in interval:
            parts = interval.split('-')
            try:
                delay_range = (int(parts[0]), int(parts[1]))
            except:
                self.status_label.setText("Ошибка интервала")
                return
        else:
            try:
                delay = int(interval)
                delay_range = (delay, delay)
            except:
                self.status_label.setText("Ошибка интервала")
                return

        asyncio.run(self._run_bot(self.api_id, self.api_hash, post_url, delay_range))

    async def _run_bot(self, api_id, api_hash, post_url, delay_range):
        self.status_label.setText("Авторизация...")

        proxy = ('socks5', '51.158.68.133', 1080, True, 'user_test', 'pass_test')
        client = TelegramClient(self.session_name, api_id, api_hash, proxy=proxy)

        await client.start()
        self.status_label.setText("Бот запущен")
        self.client = client

        try:
            print("[DEBUG] Получаю канал и ID поста...")
            parts = post_url.strip().split("/")
            channel = parts[-2]
            message_id = int(parts[-1])

            print(f"[DEBUG] Канал: {channel}, Пост ID: {message_id}")
            msg = await client.get_messages(channel, ids=message_id)

            print("[DEBUG] Получено сообщение. Проверяю replies...")
            if not msg.replies or not msg.replies.comments:
                self.status_label.setText("У поста нет комментариев")
                print("[ERROR] У поста нет комментариев")
                return

            chat_id = msg.replies.replies.chat_id
            print(f"[DEBUG] chat_id комментариев: {chat_id}")

            used = set()
            for comment in self.comments:
                if comment in used:
                    continue
                print(f"[DEBUG] Отправляю: {comment}")
                await client.send_message(chat_id, comment)
                used.add(comment)
                self.status_label.setText(f"Отправлено: {comment}")
                await asyncio.sleep(random.randint(*delay_range))

            self.status_label.setText("Готово. Все комментарии отправлены.")
            print("[DEBUG] Готово. Все комментарии отправлены.")
        except Exception as e:
            self.status_label.setText(f"Ошибка: {e}")
            print(f"[ERROR] {e}")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CommentBot()
    window.show()
    sys.exit(app.exec_())
