import os
import requests
from flask import Flask, request

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = '1584064876:AAGmhdL48OZ8MZwYyYn36TlJg19pozBX70g'
bot = telebot.TeleBot(TOKEN)
server = Flask(__name__)

def get_products():
    res = requests.get("https://api.hackathon.tchibo.com/api/v1/products?per_page=2")
    return res.json()["data"]

def gen_product_markup(products):
    markup = InlineKeyboardMarkup()
    markup.row_width = 1
    for product in products:
        markup.add(InlineKeyboardButton(product['title'], callback_data=product['product_id']))
    return markup

@bot.callback_query_handler(func=lambda call:True)
def callback_query(call):
    bot.answer_callback_query(call.id, call.data)

@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, f'Hello, {message.from_user.first_name}. Welcome to Tchibo Coffee, can I take your order?')

@bot.message_handler(commands=['products'])
def products(message):
    try:
        products = get_products()
        text = ""
        for product in products:
            text += f" {product['title']}\n{product['price']['currency']} {product['price']['amount']}\n"
        bot.send_message(message.chat.id, text, reply_markup=gen_product_markup(products))
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, e)

@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    bot.reply_to(message, message.text)


@server.route(f'/{TOKEN}', methods=['POST'])
def getMessage():
    bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200


@server.route("/")
def webhook():
    bot.remove_webhook()
    bot.set_webhook(url=f'https://immense-fjord-98048.herokuapp.com/{TOKEN}')
    return "!", 200

if __name__ == "__main__":
    server.run(host="0.0.0.0", port=int(os.environ.get('PORT', 5000)))