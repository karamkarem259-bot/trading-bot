import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes
import yfinance as yf
import pandas as pd
import ta

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=10)

# ضع توكين بوتك هنا بين القوسين المفردين بدلاً من النص الموجود
TOKEN ='8843005132:AAFrNruMqfsL1zhwpzJi-y1NKlLiR10U2yM'

PAIRS = {
    "EUR/USD": "EURUSD=X",
    "GBP/USD": "GBPUSD=X",
    "USD/JPY": "JPY=X",
    "Bitcoin (BTC)": "BTC-USD",
    "Ethereum (ETH)": "ETH-USD"
}

def analyze_market(ticker_symbol):
    try:
        data = yf.download(tickers=ticker_symbol, period="1d", interval="1m", progress=False)
        if data.empty or len(data) < 15:
            return None, "تعذر جلب البيانات الكافية."

        if isinstance(data.columns, pd.MultiIndex):
            data.columns = data.columns.get_level_values(0)

        data['RSI'] = ta.momentum.rsi(data['Close'], window=14)
        data['EMA9'] = ta.trend.ema_indicator(data['Close'], window=9)
        data['EMA21'] = ta.trend.ema_indicator(data['Close'], window=21)

        last_rsi = data['RSI'].iloc[-1]
        last_close = data['Close'].iloc[-1]
        last_ema9 = data['EMA9'].iloc[-1]
        last_ema21 = data['EMA21'].iloc[-1]

        if last_rsi < 35 or (last_ema9 > last_ema21 and last_rsi < 60):
            signal = "🟢 صعود (CALL / BUY)"
            reason = "مؤشر RSI في منطقة تشبع بيعي أو تقاطع إيجابي للمتوسطات."
        elif last_rsi > 65 or (last_ema9 < last_ema21 and last_rsi > 40):
            signal = "🔴 هبوط (PUT / SELL)"
            reason = "مؤشر RSI في منطقة تشبع شرائي أو تقاطع سلبي للمتوسطات."
        else:
            signal = "⚪ محايد (NEUTRAL / WAITING)"
            reason = "السوق في اتجاه عرضي، يُفضل الانتظار."

        return {
            "signal": signal,
            "price": round(last_close, 5),
            "rsi": round(last_rsi, 2),
            "reason": reason
        }, None
    except Exception as e:
        return None, str(e)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = []
    for pair_name in PAIRS.keys():
        keyboard.append([InlineKeyboardButton(pair_name, callback_data=pair_name)])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("مرحباً بك! اختر زوج العملات للحصول على توصية فريم (1 دقيقة):", reply_markup=reply_markup)

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    pair_name = query.data
    ticker = PAIRS.get(pair_name)

    await query.edit_message_text(f"⏳ جاري تحليل زوج {pair_name} على فريم 1 دقيقة...")

    result, error = analyze_market(ticker)

    if error:
        await query.message.reply_text(f"❌ حدث خطأ أثناء التحليل: {error}")
        return

    text = (
        f"📊 **تحليل الزوج:** {pair_name}\n"
        f"⏱ **الفريم:** 1 دقيقة\n"
        f"💵 **السعر الحالي:** {result['price']}\n"
        f"📈 **مؤشر RSI:** {result['rsi']}\n\n"
        f"🎯 **التوصية:** {result['signal']}\n"
        f"💡 **السبب:** {result['reason']}"
    )

    keyboard = [[InlineKeyboardButton(p, callback_data=p)] for p in PAIRS.keys()]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.message.reply_text(text, parse_mode="Markdown", reply_markup=reply_markup)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))

    print("البوت يعمل الآن...")
    app.run_polling()
