import os
import requests
from flask import Flask, request
from wit import Wit

import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

TOKEN = '1584064876:AAGmhdL48OZ8MZwYyYn36TlJg19pozBX70g'
bot = telebot.TeleBot(TOKEN)
client = Wit("3DKWHQ3ZTNK27BOYH6DMFWG3WLQ7DXUW")
server = Flask(__name__)

def get_products(n):
    res = requests.get(f"https://api.hackathon.tchibo.com/api/v1/products?per_page={n}")
    return res.json()["data"]

def get_articles(n):
    res = requests.get(f"https://api.hackathon.tchibo.com/api/v1/articles?per_page={n}")
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
    num = message.text.split(' ')
    try:
        n = int(num[1])
    except Exception as e:
        n = 2
    try:
        products = get_products(n)
        # text = ""
        for product in products:
            text = f"{product['title']}\n{product['price']['currency']} {product['price']['amount']}\n"
            bot.send_photo(message.chat.id, product['image']['default'], caption=text)
        bot.send_message(message.chat.id, "Pick your poison", reply_markup=gen_product_markup(products))
    except Exception as e:
        print(e)
        bot.send_message(message.chat.id, e)

@bot.message_handler(commands=['articles'])
def articles(message):
    print(message)
    num = message.text.split(' ')
    try:
        n = int(num[1])
    except Exception as e:
        n = 2
    try:
        articles = get_articles(n)
        for article in articles:
            text = f""
            bot.send_photo(message.chat.id, article['image']['default'], caption=article['title'])
            bot.send_message(message.chat.id, article['description']['long'])
    except Exception as e:
        print(e)

@bot.message_handler(func=lambda message: True, content_types=['text'])
def echo_message(message):
    resp = client.message(message.text)
    bot.reply_to(message, str(resp))


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