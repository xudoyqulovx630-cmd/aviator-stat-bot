import os
import statistics
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

TOKEN = os.getenv("BOT_TOKEN")

if not TOKEN:
    raise RuntimeError("BOT_TOKEN topilmadi")

app = Flask(__name__)

@app.route("/")
def home():
    return "Aviator Stat Bot ishlayapti!"

def run_web():
    port = int(os.getenv("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

history = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎯 Aviator tahlil bot\n\n"
        "Har raunddan keyin faqat oxirgi koeffitsiyentni yuboring.\n"
        "Masalan: 1.47\n\n"
        "Bot keyingi raund uchun bitta taxminiy koeffitsiyent chiqaradi.\n\n"
        "/history — tarix\n"
        "/stats — statistika\n"
        "/clear — tarixni tozalash\n\n"
        "⚠️ Taxmin kafolatli bashorat emas."
    )

async def add_result(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global history

    text = update.message.text.strip().lower().replace("x", "").replace(",", ".")

    try:
        value = float(text)

        if value < 1:
            raise ValueError

        history.append(value)
        history = history[-1000:]

        if len(history) < 10:
            await update.message.reply_text(
                f"✅ {value:.2f}x saqlandi.\n"
                f"Yana {10 - len(history)} ta natija kerak."
            )
            return

        data = history[-100:]

        # Past qiymatlar haddan tashqari ta'sir qilmasligi uchun
        # median + o'rtacha + oxirgi natijalar
