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
signals = []

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎯 Aviator tahlil bot\n\n"
        "Natijalarni yuboring:\n"
        "1.24 1.08 2.15 3.40 1.12\n\n"
        "/signal — taxminiy ehtimol\n"
        "/stats — batafsil statistika\n"
        "/history — oxirgi natijalar\n"
        "/accuracy — signal aniqligi\n"
        "/clear — tarixni tozalash\n\n"
        "⚠️ Signal kafolatli bashorat emas."
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

    history = history[-1000:]

    if added:
        await update.message.reply_text(
            f"✅ {len(added)} ta natija qo‘shildi.\n"
            f"Jami tarix: {len(history)} ta\n\n"
            "🎯 Signal uchun /signal bosing."
        )
    else:
        await update.message.reply_text(
            "❌ Natija topilmadi.\n"
            "Masalan: 1.24 2.15 1.03 5.40"
        )

async def signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(history) < 30:
        await update.message.reply_text(
            f"📊 Hozircha {len(history)} ta natija bor.\n"
            "Kamida 30 ta natija yuboring."
        )
        return

    data = history[-100:]

    over2 = sum(x >= 2 for x in data) / len(data)
    over5 = sum(x >= 5 for x in data) / len(data)
    over10 = sum(x >= 10 for x in data) / len(data)

    # So‘nggi 20 natijaga biroz ko‘proq ahamiyat beriladi
    recent = data[-20:]
    recent_over2 = sum(x >= 2 for x in recent) / len(recent)

    probability_2x = (over2 * 0.6 + recent_over2 * 0.4) * 100
    probability_5x = over5 * 100
    probability_10x = over10 * 100

    confidence = abs(probability_2x - 50)

    if confidence >= 15:
        level = "🟢 nisbatan kuchli"
    elif confidence >= 7:
        level = "🟡 o‘rtacha"
    else:
        level = "🔴 noaniq"

    await update.message.reply_text(
        "🎯 TAXMINIY SIGNAL\n\n"
        f"2x+ ehtimol: {probability_2x:.1f}%\n"
        f"5x+ ehtimol: {probability_5x:.1f}%\n"
        f"10x+ ehtimol: {probability_10x:.1f}%\n\n"
        f"Ishonchlilik: {level}\n"
        f"Tahlil qilingan: {len(data)} ta raund\n\n"
        "⚠️ Bu statistik model. Keyingi raundni "
        "kafolatli bashorat qilmaydi."
    )

async def stats(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not history:
        await update.message.reply_text("Hali natijalar yo‘q.")
        return

    data = history[-100:]

    low = sum(x < 2 for x in data)
    medium = sum(2 <= x < 5 for x in data)
    high = sum(x >= 5 for x in data)

    await update.message.reply_text(
        "📊 OXIRGI 100 RAUND\n\n"
        f"🔴 2x dan past: {low}\n"
        f"🟡 2x–5x: {medium}\n"
        f"🟢 5x+: {high}\n\n"
        f"Eng past: {min(data):.2f}x\n"
        f"Eng yuqori: {max(data):.2f}x"
    )

async def show_history(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not history:
        await update.message.reply_text("Tarix bo‘sh.")
        return

    text = "📜 Oxirgi 20 natija:\n\n"

    for i, value in enumerate(history[-20:], 1):
        text += f"{i}. {value:.2f}x\n"

    await update.message.reply_text(text)

async def accuracy(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not signals:
        await update.message.reply_text(
            "Hali signal natijalari yig‘ilmadi."
        )
        return

    correct = sum(signals)
    total = len(signals)
    percent = correct / total * 100

    await update.message.reply_text(
        "📈 SIGNAL ANIQLIGI\n\n"
        f"Jami signal: {total}\n"
        f"To‘g‘ri: {correct}\n"
        f"Xato: {total - correct}\n"
        f"Natija: {percent:.1f}%"
    )

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE):
    history.clear()
    signals.clear()

    await update.message.reply_text(
        "🗑 Tarix va signal statistikasi tozalandi."
    )

def main():
    Thread(target=run_web, daemon=True).start()

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("signal", signal))
    application.add_handler(CommandHandler("stats", stats))
    application.add_handler(CommandHandler("history", show_history))
    application.add_handler(CommandHandler("accuracy", accuracy))
    application.add_handler(CommandHandler("clear", clear))

    application.add_handler(
        MessageHandler(filters.TEXT & ~filters.COMMAND, add_results)
    )

    print("Bot ishga tushdi!")
    application.run_polling()

if __name__ == "__main__":
    main()
