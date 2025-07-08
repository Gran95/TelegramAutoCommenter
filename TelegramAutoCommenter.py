import sys
import asyncio
import random

from telethon import TelegramClient

API_ID = 13959415
API_HASH = '3f02e6c5a0d9c7438fc27153a8d70a92'
SESSION_NAME = "comment_session"

# Прокси (SOCKS5)
PROXY = ('socks5', '51.158.68.133', 1080, True, 'user_test', 'pass_test')

def load_comments(file_path="comments.txt"):
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            return [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print("[ERROR] Файл comments.txt не найден.")
        return []

async def run_bot(api_id, api_hash, post_url, delay_range, comments):
    print("[INFO] Авторизация...")
    client = TelegramClient(SESSION_NAME, api_id, api_hash, proxy=PROXY)
    await client.start()

    try:
        print("[INFO] Получаю канал и ID поста...")
        parts = post_url.strip().split("/")
        channel = parts[-2]
        message_id = int(parts[-1])

        msg = await client.get_messages(channel, ids=message_id)

        if not msg.replies or not msg.replies.comments:
            print("[ERROR] У поста нет комментариев.")
            return

        chat_id = msg.replies.replies.chat_id
        print(f"[INFO] chat_id комментариев: {chat_id}")

        used = set()
        for comment in comments:
            if comment in used:
                continue
            print(f"[SEND] {comment}")
            await client.send_message(chat_id, comment)
            used.add(comment)
            await asyncio.sleep(random.randint(*delay_range))

        print("[DONE] Все комментарии отправлены.")

    except Exception as e:
        print(f"[ERROR] {e}")
    finally:
        await client.disconnect()

def main():
    print("=== Telegram Auto Commenter ===")

    post_url = input("Вставь ссылку на пост: ").strip()
    interval = input("Интервал (например 5-10): ").strip()

    if '-' in interval:
        parts = interval.split('-')
        try:
            delay_range = (int(parts[0]), int(parts[1]))
        except:
            print("[ERROR] Неверный формат интервала.")
            return
    else:
        try:
            delay = int(interval)
            delay_range = (delay, delay)
        except:
            print("[ERROR] Неверный формат интервала.")
            return

    comments = load_comments()
    if not comments:
        print("[ERROR] Нет комментариев для отправки.")
        return

    asyncio.run(run_bot(API_ID, API_HASH, post_url, delay_range, comments))

if __name__ == "__main__":
    main()
