import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import json

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# 🔴 توکن‌های شما (آپدیت شده)
TELEGRAM_TOKEN = "8459107126:AAFLeuphF2ZgfD9FwhBo1LS_WSXsS0B0Akk"
HF_TOKEN = "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"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    await update.message.reply_text(
        f"👋 سلام {user.first_name}!\n"
        "🤖 ربات هوش مصنوعی شما فعال شد\n\n"
        "✨ می‌توانید:\n"
        "• متن بفرستید\n"
        "• عکس بفرستید\n"
        "• ویس بفرستید\n\n"
        "⚡ آماده دریافت پیام!"
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📚 راهنما:\n"
        "/start - شروع کار\n"
        "/help - این راهنما\n\n"
        "📨 ارسال پیام:\n"
        "• هر متنی بنویسید\n"
        "• عکس بفرستید\n"
        "• پیام صوتی ارسال کنید"
    )

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        user_text = update.message.text
        
        # نشان‌دهنده تایپ کردن
        await update.message.chat.send_action(action="typing")
        
        # استفاده از مدل DialoGPT برای چت بهتر
        API_URL = "https://api-inference.huggingface.co/models/microsoft/DialoGPT-small"
        headers = {"Authorization": f"Bearer {HF_TOKEN}"}
        
        payload = {"inputs": user_text}
        
        response = requests.post(API_URL, headers=headers, json=payload, timeout=30)
        
        if response.status_code == 200:
            result = response.json()
            
            if isinstance(result, list) and len(result) > 0:
                if 'generated_text' in result[0]:
                    generated = result[0]['generated_text']
                    # حذف متن تکراری
                    if user_text in generated:
                        reply = generated[len(user_text):].strip()
                    else:
                        reply = generated
                else:
                    reply = str(result[0])[:500]
            else:
                reply = "🤔 لطفاً دوباره بپرسید"
        elif response.status_code == 503:
            reply = "⏳ مدل در حال لود شدن است... ۱۰ ثانیه دیگر تلاش کنید"
        else:
            reply = f"⚠️ خطا: کد {response.status_code}"
        
        # محدودیت طول پیام
        if len(reply) > 4000:
            reply = reply[:4000] + "..."
        
        if not reply.strip():
            reply = "🌀 پاسخی دریافت نشد"
            
        await update.message.reply_text(reply)
        
    except Exception as e:
        logger.error(f"خطا: {e}")
        await update.message.reply_text("❌ خطا در پردازش. لطفاً دوباره تلاش کنید")

def main():
    # چک کردن توکن‌ها
    print("="*50)
    print("🤖 در حال راه‌اندازی ربات...")
    print(f"📱 توکن تلگرام: {TELEGRAM_TOKEN[:15]}...")
    print(f"🧠 توکن HuggingFace: {HF_TOKEN[:15]}...")
    print("="*50)
    
    try:
        application = Application.builder().token(TELEGRAM_TOKEN).build()
        
        # اضافه کردن دستورات
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("help", help_command))
        
        # اضافه کردن هندلر متن
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
        
        # شروع ربات
        logger.info("✅ ربات شروع به کار کرد")
        print("\n✅ ربات فعال شد!")
        print("📲 به تلگرام بروید و با ربات چت کنید")
        print("🔗 آدرس ربات: https://t.me/your_bot_username")
        print("\nبرای توقف: Ctrl+C")
        print("="*50)
        
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        
    except Exception as e:
        logger.error(f"خطای اصلی: {e}")
        print(f"\n❌ خطا: {e}")
        print("\n🔧 عیب‌یابی:")
        print("1. توکن تلگرام را بررسی کنید")
        print("2. اینترنت را چک کنید")
        print("3. پورت‌ها باز هستند؟")

if __name__ == '__main__':
    main()
