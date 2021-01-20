import os
from telegram import ParseMode
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import html
import json
import traceback

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = '1584064876:AAGmhdL48OZ8MZwYyYn36TlJg19pozBX70g'
URL = 'https://immense-fjord-98048.herokuapp.com/'
PORT = int(os.environ.get('PORT', '8443'))
DEVELOPER_CHAT_ID = 123456789

def error_handler(update, context):
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    tb_list = traceback.format_exception(None, context.error, context.error.__traceback__)
    tb_string = ''.join(tb_list)

    # Build the message with some markup and additional information about what happened.
    # You might need to add some logic to deal with messages longer than the 4096 character limit.
    message = (
        f'An exception was raised while handling an update\n'
        f'<pre>update = {html.escape(json.dumps(update.to_dict(), indent=2, ensure_ascii=False))}'
        '</pre>\n\n'
        f'<pre>context.chat_data = {html.escape(str(context.chat_data))}</pre>\n\n'
        f'<pre>context.user_data = {html.escape(str(context.user_data))}</pre>\n\n'
        f'<pre>{html.escape(tb_string)}</pre>'
    )

    # Finally, send the message
    context.bot.send_message(chat_id=DEVELOPER_CHAT_ID, text=message, parse_mode=ParseMode.HTML)


def start(update, context):
    update.message.reply_text("Hello I'm a telegram bot")

def echo(update, context):
    update.message.reply_text(update.message.text)


def help(update, context):
    update.message.reply_text("This is the help menu")


def main():

    updater = Updater(TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))

    # on noncommand i.e message - echo the message on Telegram
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))
    updater.start_webhook(listen="0.0.0.0",
                      port=PORT,
                      url_path=TOKEN)
    updater.bot.set_webhook("{URL}" + TOKEN)

    updater.idle()

if __name__ == '__main__':
    main()