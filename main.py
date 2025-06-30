from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from tinydb import TinyDB, Query

db = TinyDB('mnux_users.json')
User = Query()

TAP_REWARD = 2
REF_BONUS = 50
TAP_BOOST_COUNT = 5
BOOST_REWARD = 10

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    ref_code = context.args[0] if context.args else None

    if not db.search(User.id == user_id):
        db.insert({'id': user_id, 'coins': 0, 'taps': 0})
        if ref_code and ref_code.isdigit():
            ref_id = int(ref_code)
            if ref_id != user_id and db.search(User.id == ref_id):
                db.update(lambda u: u.update({'coins': u['coins'] + REF_BONUS}), User.id == ref_id)
                await context.bot.send_message(chat_id=ref_id, text=f"🎉 You've earned {REF_BONUS} Mnux from a referral!")

    keyboard = [["🪙 Mine Mnux"], ["💼 Balance", "👥 Refer"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("🚀 Welcome to Mnux Miner!\nTap below to earn coins:", reply_markup=reply_markup)

async def tap(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    user = db.get(User.id == user_id)
    if user:
        new_taps = user['taps'] + 1
        reward = TAP_REWARD
        if new_taps % TAP_BOOST_COUNT == 0:
            reward += BOOST_REWARD
        db.update({'coins': user['coins'] + reward, 'taps': new_taps}, User.id == user_id)
        await update.message.reply_text(f"🛠 You mined {reward} Mnux!\n🖱 Total taps: {new_taps}")

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = db.get(User.id == update.effective_user.id)
    coins = user['coins'] if user else 0
    await update.message.reply_text(f"💼 Your Mnux Balance: {coins} coins")

async def refer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id
    refer_link = f"https://t.me/mnuxminerbot?start={uid}"
    await update.message.reply_text(f"👥 Invite friends & earn {REF_BONUS} coins!\nYour link:\n{refer_link}")

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🪙 Mine Mnux":
        await tap(update, context)
    elif text == "💼 Balance":
        await balance(update, context)
    elif text == "👥 Refer":
        await refer(update, context)
    else:
        await update.message.reply_text("❌ Unknown command.")

TOKEN = "7905434373:AAFrz-NINI93RXIsxJraVLpiPoSSXRzFijU"

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.run_polling()
  
