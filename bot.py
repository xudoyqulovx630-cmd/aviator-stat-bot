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
        "👋 Salom!\n\n"
        "Aviator statistik botiga xush kelibsiz.\n\n"
        "Koeffitsientlarni yuboring:\n"
        "1.24 2.15 1.03 5.40\n\n"
        "/stats — statistika\n"
        "/history — tarix\n"
        "/clear — tarixni tozalash"
    )

async def add_results(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global history

    parts = update.message.text.replace(",", " ").split()
    added = []

    for part in parts:
        try:
            value = float(part.lower().replace("x", ""))
            if value >= 1:
                history.append(value)
                added.append(value)
        except ValueError:
            pass

    history = history[-200:]

    if added:
        await update.message.reply_text(
            f"✅ {len(added)} ta natija qo‘shildi.\n"
            f"Jami: {len(history)} ta\n\n"
            "📊 /stats"
        )
    else:
        await update.message.reply_text(
            "❌ Koeffitsient topilmadi.\n"
            "Masalan: 1.24 2.15 1.03 5.40"
        )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not history:
        await update.message.reply_text("Hali natija yo‘q.")
        return

    data = history[-50:]
    avg = statistics.mean(data)
    median = statistics.median(data)

    low = sum(x < 2 for x in data)
    medium = sum(2 <= x < 10 for x in data)
    high = sum(x >= 10 for x in data)

    await update.message.reply_text(
        "📊 OXIRGI 50 NATIJA\n\n"
        f"Natijalar: {len(data)}\n"
        f"O‘rtacha: {avg:.2f}x\n"
        f"Median: {median:.2f}x\n\n"
        f"🔴 2x dan past: {low} ta\n"
        f"🟡 2x–10x: {medium} ta\n"
        f"🟢 10x+: {high} ta\n\n"
        f"⬇️ Eng past: {min(data):.2f}x\n"
        f"⬆️ Eng yuqori: {max(data):.2f}x\n\n"
        "⚠️ Bu tarixiy statistika, keyingi natijani kafolatli "
        "bashorat qilmaydi."
    )

async def show_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not history:
        await update.message.reply_text("Tarix bo‘sh.")
        return

    text = "📜 Oxirgi natijalar:\n\n"
    for i, value in enumerate(history[-20:], 1):
        text += f"{i}. {value:.2f}x\n"

    await update.message.reply_text(text)

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    history.clear()
    await update.message.reply_text("🗑 Tarix tozalandi.")

def main():
    Thread(target=run_web, daemon=True).start()

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("history", show_history))
    application.add_handler(CommandHandler("clear", clear))
    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, add_results)
    )

    print("Bot ishga tushdi!")
    application.run_polling()

if __name__ == "__main__":
    main()

