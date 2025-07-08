import os
import sys
import asyncio
import random
from telethon import TelegramClient
from telethon.errors import SessionPasswordNeededError

async def main():
    print("=== Telegram Авто Комментатор ===")

    # Получаем данные из переменных окружения
    api_id = int(os.environ.get("API_ID"))
    api_hash = os.environ.get("API_HASH")
    session_name = os.environ.get("SESSION_NAME", "comment_session")
    post_url = os.environ.get("POST_URL", "")
    delay_min = int(os.environ.get("DELAY_MIN", 5))
    delay_max = int(os.environ.get("DELAY_MAX", 10))
    proxy_host = os.environ.get("PROXY_HOST")
    proxy_port = int(os.environ.get("PROXY_PORT", 1080))
    proxy_user = os.environ.get("PROXY_USER", None)
    proxy_pass = os.environ.get("PROXY_PASS", None)

    # Прокси
    proxy = None
    if proxy_host:
        proxy = ('socks5', proxy_host, proxy_port, True, proxy_user, proxy_pass)

    client = TelegramClient(session_name, api_id, api_hash, proxy=proxy)
    await client.start()
    print("[+] Авторизация прошла успешно")

    # Получаем канал и ID поста
    try:
        parts = post_url.strip().split("/")
        channel = parts[-2]
        message_id = int(parts[-1])
        msg = await client.get_messages(channel, ids=message_id)

        if not msg.replies or not msg.replies.comments:
            print("[!] У поста отключены комментарии")
            return

        chat_id = msg.replies.replies.chat_id
    except Exception as e:
        print(f"[!] Ошибка при получении post_url: {e}")
        return

    # Загружаем комментарии
    try:
        with open("comments.txt", "r", encoding="utf-8") as f:
            comments = [line.strip() for line in f if line.strip()]
    except Exception as e:
        print(f"[!] Не удалось открыть comments.txt: {e}")
        return

    used = set()
    for comment in comments:
        if comment in used:
            continue
        try:
            await client.send_message(chat_id, comment)
            print(f"[✔] Отправлено: {comment}")
            used.add(comment)
            await asyncio.sleep(random.randint(delay_min, delay_max))
        except Exception as e:
            print(f"[!] Ошибка при отправке: {e}")

    print("✅ Все комментарии успешно отправлены.")
    await client.disconnect()

if __name__ == "__main__":
    asyncio.run(main())
