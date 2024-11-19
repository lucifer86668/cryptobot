import requests
import schedule
import time
from telegram import Bot, Update
from telegram.ext import Updater, CommandHandler, CallbackContext
import logging

# Settings
TELEGRAM_BOT_TOKEN = '7417257593:AAE75GK41akngDHtBbR8c8MciVwPlKMg6yQ'
CHAT_ID = '@QJyC8NbFDbhkYTk6'  # Channel link provided
CRYPTO_API_URL = 'https://api.coingecko.com/api/v3/coins/markets'
BTC_DOMINANCE_URL = 'https://api.coingecko.com/api/v3/global'
PARAMS = {
    'vs_currency': 'usd',
    'order': 'market_cap_desc',
    'per_page': 20,
    'page': 1,
}

# Logging setup
logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s - %(message)s"
)

logging.info("Bot starting...")

# Function to get crypto data
def get_crypto_data():
    response = requests.get(CRYPTO_API_URL, params=PARAMS)
    if response.status_code == 200:
        return response.json()
    return []

# Function to get Bitcoin dominance
def get_btc_dominance():
    response = requests.get(BTC_DOMINANCE_URL)
    if response.status_code == 200:
        return response.json()['data']['market_cap_percentage']['btc']
    return None

# Function to send updates to Telegram
def send_crypto_update():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    crypto_data = get_crypto_data()
    btc_dominance = get_btc_dominance()

    if crypto_data and btc_dominance is not None:
        message = f"🌍 Bitcoin Dominance: {btc_dominance:.2f}%\n\nTop 20 Cryptocurrencies:\n"
        for coin in crypto_data:
            message += f"{coin['symbol'].upper()} ({coin['name']}): ${coin['current_price']:.2f}\n"
        bot.send_message(chat_id=CHAT_ID, text=message)
        logging.info("Crypto update sent to channel.")
    else:
        bot.send_message(chat_id=CHAT_ID, text="Failed to fetch cryptocurrency data.")
        logging.error("Failed to fetch cryptocurrency data.")

# Function to handle the `/sendtop20` command
def handle_sendtop20(update: Update, context: CallbackContext):
    logging.info("Received /sendtop20 command.")
    crypto_data = get_crypto_data()
    btc_dominance = get_btc_dominance()

    if crypto_data and btc_dominance is not None:
        message = f"🌍 Bitcoin Dominance: {btc_dominance:.2f}%\n\nTop 20 Cryptocurrencies:\n"
        for coin in crypto_data:
            message += f"{coin['symbol'].upper()} ({coin['name']}): ${coin['current_price']:.2f}\n"
        update.message.reply_text("Sending update to channel...")
        bot = Bot(token=TELEGRAM_BOT_TOKEN)
        bot.send_message(chat_id=CHAT_ID, text=message)
        update.message.reply_text("Update sent to the channel.")
    else:
        update.message.reply_text("Failed to fetch cryptocurrency data.")
        logging.error("Failed to fetch cryptocurrency data.")

# Schedule the daily updates
schedule.every().day.at("10:00").do(send_crypto_update)

# Start the bot with command handler
def main():
    updater = Updater(TELEGRAM_BOT_TOKEN, use_context=True)
    dispatcher = updater.dispatcher

    # Add command handlers
    dispatcher.add_handler(CommandHandler("sendtop20", handle_sendtop20))

    # Start the bot
    updater.start_polling()

    logging.info("Bot started. Waiting for commands...")
    # Run the scheduler in the main loop
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    main()