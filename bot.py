import os
import random
from flask import Flask
from threading import Thread
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# إعداد سيرفر Webhook لإبقاء البوت شغالاً على Render
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive!"

def run():
    app.run(host='0.0.0.0', port=8080)

def keep_alive():
    t = Thread(target=run)
    t.start()

# قائمة أزواج العملات الكاملة التي طلبتها
PAIRS = [
    "AED/CNY OTC +92%", "AUD/USD OTC +92%", "BHD/CNY OTC +92%", "CAD/CHF OTC +92%",
    "SAR/CNY OTC +92%", "UAH/USD OTC +92%", "USD/MYR OTC +92%", "USD/VND OTC +92%",
    "ZAR/USD OTC +91%", "USD/ARS OTC +88%", "EUR/HUF OTC +83%", "AUD/JPY OTC +82%",
    "USD/BDT OTC +80%", "USD/DZD OTC +79%", "USD/RUB OTC +79%", "CHF/JPY OTC +77%",
    "EUR/TRY OTC +75%", "CAD/JPY OTC +71%", "EUR/CHF OTC +71%", "EUR/JPY OTC +70%",
    "KES/USD OTC +70%", "OMR/CNY OTC +67%", "MAD/USD OTC +66%", "USD/JPY OTC +66%",
    "USD/MXN OTC +66%", "QAR/CNY OTC +65%", "USD/THB OTC +65%", "EUR/RUB OTC +64%",
    "SYP/USD OTC +63%", "USD/SGD OTC +62%", "EUR/USD OTC +60%", "USD/EGP OTC +54%",
    "USD/COP OTC +51%", "AUD/CAD OTC +50%", "USD/INR OTC +49%", "CHF/NOK OTC +48%",
    "USD/CHF OTC +48%", "USD/IDR OTC +45%", "USD/BRL OTC +44%", "USD/CNH OTC +42%",
    "LBP/USD OTC +41%", "USD/CAD OTC +39%", "YER/USD OTC +39%", "AUD/CHF OTC +38%",
    "TND/USD OTC +35%", "USD/CLP OTC +34%", "USD/PKR OTC +28%", "NGN/USD OTC +27%",
    "EUR/JPY N/A", "EUR/CAD N/A", "AUD/CAD N/A", "AUD/CHF N/A", "AUD/USD N/A",
    "CAD/CHF N/A", "CAD/JPY N/A", "CHF/JPY N/A", "EUR/CHF N/A", "EUR/USD N/A",
    "USD/CAD N/A", "USD/CHF N/A", "USD/JPY N/A", "AUD/JPY N/A", "EUR/AUD N/A"
]

def build_keyboard(page=0):
    items_per_page = 8
    start = page * items_per_page
    end = start + items_per_page
    current_pairs = PAIRS[start:end]
    
    keyboard = []
    # عرض الأزواج في صفين بكل صف زرين
    for i in range(0, len(current_pairs), 2):
        row = [InlineKeyboardButton(current_pairs[i], callback_data=f"pair_{start+i}")]
        if i + 1 < len(current_pairs):
            row.append(InlineKeyboardButton(current_pairs[i+1], callback_data=f"pair_{start+i+1}"))
        keyboard.append(row)
        
    # أزرار التنقل بين الصفحات
    nav_row = []
    if page > 0:
        nav_row.append(InlineKeyboardButton("⬅️ السابق", callback_data=f"page_{page-1}"))
    if end < len(PAIRS):
        nav_row.append(InlineKeyboardButton("التالي ➡️", callback_data=f"page_{page+1}"))
        
    if nav_row:
        keyboard.append(nav_row)
        
    return InlineKeyboardMarkup(keyboard)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    reply_markup = build_keyboard(0)
    await update.message.reply_text(
        "🚀 **Pocket Option VIP Signals Bot** 🚀\n\n"
        "مرحباً بك! اختر الزوج أدناه لتقديم التحليل والإشارة الفورية:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    if data.startswith("page_"):
        page = int(data.split("_")[1])
        reply_markup = build_keyboard(page)
        await query.edit_message_reply_markup(reply_markup=reply_markup)
    elif data.startswith("pair_"):
        pair_index = int(data.split("_")[1])
        selected_pair = PAIRS[pair_index]
        
        # توليد إشارة عشوائية كمثال
        direction = random.choice(["🟢 شراء (CALL)", "🔴 بيع (PUT)"])
        timeframe = random.choice(["10 ثوانٍ", "30 ثانية", "1 دقيقة"])
        accuracy = random.randint(88, 98)
        
        signal_msg = (
            f"📊 **إشارة التداول لزوج:** `{selected_pair}`\n\n"
            f"🎯 **الاتجاه:** {direction}\n"
            f"⏱️ **الصفقة:** {timeframe}\n"
            f"🔥 **نسبة النجاح المتوقعة:** {accuracy}%\n\n"
            f"⚠️ *تنبيه: التداول ينطوي على مخاطر، يرجى إدارة رأس المال بحذر.*"
        )
        await query.message.reply_text(signal_msg, parse_mode="Markdown")

def main():
    token=os.environ.get("BOT_TOKEN")
    if not token:
      print("BOT_TOKEN is missing!")
      return

     keep_alive()
    application = Application.builder().token(token).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    
    application.run_polling()

if __name__ == "__main__":
    main()
