import sys
import sqlite3
import unicodedata
from telethon import TelegramClient, events
from rich.console import Console
from rich import print

# تنظیم UTF-8 برای نمایش صحیح متون فارسی
sys.stdout.reconfigure(encoding='utf-8')

# تنظیمات تلگرام
api_id = 11111111  # مقدار را از my.telegram.org بگیر
api_hash = '1111111111111111111'  # مقدار را از my.telegram.org بگیر
session_name = 'forwarder_session'  # فایل سشن ذخیره می‌شود

# لیست کانال‌ها و گروه‌های مبدا و مقصد
source_chats = [-1111111111111]  # آی‌دی کانال‌های مبدا
destination_chats = [-11111111111]  # آی‌دی کانال مقصد

# لیست کلمات ممنوعه (Blacklist)
blacklist_words = ["کلاهبرداری", "غیرمجاز", "اسپم"]

# تنظیمات نمایش رنگی
console = Console()

# اتصال به تلگرام
client = TelegramClient(session_name, api_id, api_hash)


# تابع بررسی پیام تکراری
def is_duplicate(message_id):
    conn = sqlite3.connect('forwarder.db')
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM messages WHERE message_id=?", (message_id,))
    result = cursor.fetchone()
    conn.close()
    return result is not None


# ذخیره پیام در دیتابیس
def save_message(message_id, from_chat, to_chat):
    conn = sqlite3.connect('forwarder.db')
    cursor = conn.cursor()
    cursor.execute("INSERT INTO messages (message_id, from_chat, to_chat) VALUES (?, ?, ?)",
                   (message_id, from_chat, to_chat))
    conn.commit()
    conn.close()


# تابع نرمال‌سازی متن برای جلوگیری از مشکل در نمایش
def normalize_text(text):
    return unicodedata.normalize("NFC", text)


# هندلر دریافت پیام از کانال‌های مبدا
@client.on(events.NewMessage(chats=source_chats))
async def handler(event):
    message = event.message

    # بررسی پیام تکراری
    if is_duplicate(message.id):
        console.print(f"[yellow]⏩ پیام {message.id} قبلا ارسال شده است، نادیده گرفته شد.[/]")
        return

    # متن پیام اصلی
    text = normalize_text(message.text or message.caption or '')

    # بررسی لیست سیاه
    if any(word in text for word in blacklist_words):
        console.print(f"[red]⛔ پیام {message.id} شامل کلمه ممنوعه است و ارسال نمی‌شود.[/]")
        return

    # اضافه کردن متن اضافی به پیام
    additional_text = "\n@filtersniper"
    new_text = text + additional_text

    # ارسال پیام به کانال مقصد
    for dest in destination_chats:
        if message.media:
            sent = await client.send_file(dest, message.media, caption=new_text)
        else:
            sent = await client.send_message(dest, new_text)

        # ذخیره پیام در دیتابیس
        save_message(message.id, event.chat_id, dest)
        console.print(f"[bold green]✅ پیام {message.id} به {dest} ارسال شد.[/]")

# شروع کلاینت
console.print("[bold cyan]📡 در حال اجرا ...[/]")
client.start()
client.run_until_disconnected()
