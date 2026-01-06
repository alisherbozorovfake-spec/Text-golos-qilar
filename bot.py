from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
from gtts import gTTS
import os

# --- Telegram bot token va kanal nomlari ---
TOKEN = "8347566760:AAGPd4YsNZDKvu2pvVyrAV1ghZN8sTPiMmk"
CHANNELS = ["@UzAniVoice", "@alishern1_youtuber"]  # majburiy obuna bo'lishi kerak bo'lgan kanallar
MAX_TEXTS = 4  # foydalanuvchi necha matn yuborishidan keyin obuna so‘raydi

# Foydalanuvchi holatlarini saqlash
user_text_count = {}  # user_id -> matn yuborilgan soni

# /start handler
def start(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id

    user_text_count[user_id] = 0  # foydalanuvchi sonini reset qilamiz
    update.message.reply_text(
        "🎤 Salom! 4 ta matn yuboring, men ularni O‘zbekcha ovozga aylantiraman."
    )

# Matnni ovozga aylantirish
def text_to_voice(update: Update, context: CallbackContext):
    user_id = update.effective_user.id
    chat_id = update.effective_chat.id
    text = update.message.text.strip()

    if not text:
        return

    # Foydalanuvchi matn yuborish sonini hisoblaymiz
    if user_id not in user_text_count:
        user_text_count[user_id] = 0

    if user_text_count[user_id] < MAX_TEXTS:
        # Google TTS bilan o'zbekcha ovoz
        filename = f"{chat_id}_output.mp3"
        tts = gTTS(text=text, lang='uz')
        tts.save(filename)
        context.bot.send_audio(chat_id=chat_id, audio=open(filename, "rb"))
        os.remove(filename)

        user_text_count[user_id] += 1

        remaining = MAX_TEXTS - user_text_count[user_id]
        update.message.reply_text(f"✅ {remaining} ta matn qoldi ovozlash uchun.")

        # Agar foydalanuvchi 4 ta matn yuborgan bo‘lsa, majburiy obuna so‘raymiz
        if user_text_count[user_id] == MAX_TEXTS:
            update.message.reply_text(
                "📢 Endi quyidagi kanallarga obuna bo‘ling va qaytadan /start bosing:\n" +
                "\n".join(CHANNELS)
            )
    else:
        update.message.reply_text(
            "❌ Siz 4 matndan oshdingiz. Iltimos, kanallarga obuna bo‘ling va /start bosing."
        )

def main():
    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, text_to_voice))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
