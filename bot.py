
import pandas as pd
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters, ConversationHandler

# 🔐 توکن ربات از BotFather
TOKEN ="7759395171:AAEMff19DBEdpDt3RflXA5X3I5ZF1Ju8Hwo"

# 📄 بارگذاری داده‌ها از فایل اکسل
df = pd.read_excel("Book22.xlsx")

# مرحله‌های مکالمه
GET_TAFSILI, GET_NATIONAL = range(2)

# ذخیره داده‌های موقت کاربر
user_data = {}

# شروع
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ ربات به پیام شما پاسخ داد!")
    return ConversationHandler.END


# دریافت کد تفصیلی
async def get_tafsili(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_data[update.effective_user.id] = {'taf': update.message.text.strip()}
    await update.message.reply_text("حالا لطفاً کد ملی خود را وارد کنید:")
    return GET_NATIONAL

# دریافت کد ملی و بررسی
async def get_national(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    national = update.message.text.strip()
    tafsili = user_data[user_id]['taf']

    match = df[(df['تفصیلی'].astype(str) == tafsili) & (df['شماره ملی'].astype(str) == national)]
    
    if not match.empty:
        try:
            file_path = f"{tafsili}.pdf"
            with open(file_path, "rb") as f:
                await update.message.reply_document(f)
        except FileNotFoundError:
            await update.message.reply_text("فایل PDF مربوط به کد تفصیلی شما پیدا نشد.")
    else:
        await update.message.reply_text("کد تفصیلی و کد ملی با هم تطابق ندارند یا در سیستم نیستند.")
    
    return ConversationHandler.END

# اگر کاربر خواست مکالمه رو قطع کنه
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("مکالمه لغو شد.")
    return ConversationHandler.END

# تنظیم ربات
def main():
    app = ApplicationBuilder().token(TOKEN).build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            GET_TAFSILI: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_tafsili)],
            GET_NATIONAL: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_national)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(conv_handler)

    print("🤖 Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
