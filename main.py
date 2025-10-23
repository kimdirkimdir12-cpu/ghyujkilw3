from flask import Flask
from telethon import TelegramClient, events
import asyncio
import threading
import datetime
import random
import requests
import os

# === TELETHON SOZLAMALARI ===
API_ID = 25501859
API_HASH = "3794184d222264f05dbc4622f3962b5f"
SESSION_NAME = "userbot_session"

# === KANAL SOZLAMALARI ===
WATCHED_CHANNEL = "wkjefdckewnc"
AUTO_COMMENT_TEXTS = ["9860350149462219"]

# === ODDIY JAVOBLAR LUG‘ATI ===
RESPONSES = {
    "salom": "Va alaykum assalom!",
    "assalomu alaykum": "Va alaykum assalom, yaxshimisiz?",
    "qalesan": "Yaxshi, o‘zingchi?",
    "nima gap": "Hammasi joyida 😎",
    "kim bu": "Men avtomatik yordamchiman 🤖",
    "nima qilayapsan": "Ishlayapman, sizchi?",
    "rahmat": "Doim xizmatda 😊",
    "ha": "Ha, eshitaman!",
    "yo‘q": "Mayli, keyin gaplashamiz.",
    "qayerdansan": "Internetdanman 😅",
}

DEFAULT_REPLY = "Bir soniya... fikrlayapman 🤔"

# === HUGGING FACE AI FUNKSIYASI ===
def ai_response(prompt: str) -> str:
    HF_TOKEN = os.getenv("HF_TOKEN")
    if not HF_TOKEN:
        return "AI ishlashi uchun HF_TOKEN o‘rnatilmagan!"

    model = "google/flan-t5-small"  # yengil va tez model
    url = f"https://api-inference.huggingface.co/models/{model}"
    headers = {"Authorization": f"Bearer {HF_TOKEN}"}
    payload = {"inputs": prompt, "options": {"wait_for_model": True}}

    try:
        resp = requests.post(url, headers=headers, json=payload, timeout=30)
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list) and len(data) > 0 and "generated_text" in data[0]:
                return data[0]["generated_text"].strip()
            else:
                return "Javobni tahlil qilib bo‘lmadi."
        else:
            return f"AI xato: {resp.status_code} - {resp.text[:100]}"
    except Exception as e:
        return f"AI so‘rovda xato: {e}"

# === FLASK SERVER (Replit uchun doimiy ishlash) ===
app = Flask('')

@app.route('/')
def home():
    return "✅ Userbot ishlayapti! AI bilan javob beradi."

def run_web():
    app.run(host='0.0.0.0', port=8080)

# === TELEGRAM USERBOT ===
async def start_userbot():
    client = TelegramClient(SESSION_NAME, API_ID, API_HASH)

    @client.on(events.NewMessage(incoming=True))
    async def reply_private(event):
        if event.is_private:
            try:
                text = event.raw_text.lower().strip()
                reply = None

                # 1️⃣ Avval lug‘atdan izlash
                for key, val in RESPONSES.items():
                    if key in text:
                        reply = val
                        break

                # 2️⃣ Agar topilmasa — AI ishlaydi
                if not reply:
                    reply = ai_response(text)

                await event.reply(reply)
                sender = await event.get_sender()
                print(f"[{datetime.datetime.now()}] 💬 {sender.first_name}: {text} → {reply}")

            except Exception as e:
                print(f"⚠️ Xatolik (javob): {e}")

    # --- KANAL POSTLARINI KUZATISH ---
    async def watch_channel():
        last_id = 0
        try:
            entity = await client.get_entity(WATCHED_CHANNEL)
            print(f"📡 Kanal kuzatish boshlandi: {entity.title}")
        except Exception as e:
            print(f"⚠️ Kanalni topishda xato: {e}")
            return

        while True:
            try:
                posts = await client.get_messages(entity, limit=1)
                if posts and posts[0].id != last_id:
                    last_id = posts[0].id
                    msg_id = posts[0].id
                    text = random.choice(AUTO_COMMENT_TEXTS)
                    await client.send_message(entity=entity, message=text, comment_to=msg_id)
                    print(f"[{datetime.datetime.now()}] ⚡ Komment yozildi: {text}")
                await asyncio.sleep(1)
            except Exception as e:
                print(f"⚠️ Kuzatishda xatolik: {e}")
                await asyncio.sleep(3)

    async with client:
        print("🤖 Userbot ishga tushdi — AI bilan real-time javob va kommentlar faol.")
        await asyncio.gather(client.run_until_disconnected(), watch_channel())

# === BARCHASINI ISHGA TUSHURISH ===
if __name__ == "__main__":
    threading.Thread(target=run_web).start()
    asyncio.run(start_userbot())  
