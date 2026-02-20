import re
import logging
from telegram import Update
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext

# Set up logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# Phone number validation function

def is_valid_phone_number(phone_number: str) -> bool:
    """Check if the phone number is valid."
    pattern = re.compile(r'^\+\d{10,15}$')  # Updated pattern to match +1234567890
    return pattern.match(phone_number) is not None

# Command handler for '/start'

def start(update: Update, context: CallbackContext) -> None:
    update.message.reply_text('Welcome to the OTP Bot! Please provide your phone number in the format +1234567890.') 

# Command handler for handling messages

def handle_message(update: Update, context: CallbackContext) -> None:
    text = update.message.text
    if is_valid_phone_number(text):
        update.message.reply_text('Phone number is valid.')
    else:
        update.message.reply_text('Invalid phone number format. Please use +1234567890.')

# Main function to run the bot

def main() -> None:
    updater = Updater('YOUR_TOKEN_HERE')  # Please replace YOUR_TOKEN_HERE with your bot's API token
    dispatcher = updater.dispatcher

    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_message))

    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()