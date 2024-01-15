import logging
import redis

from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Filters, Updater
from telegram.ext import CallbackQueryHandler, CommandHandler, MessageHandler
from environs import Env

from strapi import Strapi

_database = None

logger = logging.getLogger(__name__)


def get_chat_id_message_id(update, context):
    if update.message:
        chat_id = update.message.chat.id
        message_id = update.message.message_id
    else:
        chat_id = update.callback_query.message.chat.id
        message_id = update.callback_query.message.message_id
    return chat_id, message_id


def start(update, context):
    return "HANDLE_MENU"


def handle_menu(update, context):
    strapi = context.bot_data['strapi']
    chat_id, message_id = get_chat_id_message_id(update, context)
    if update.callback_query:
        query = update.callback_query.data
        if query == "/go_cart":
            return handle_cart(update, context)
        if query == '/pay':
            return handle_pay(update, context)
        if query == '/del_products':
            return handle_empty_cart(update, context)
    products = strapi.get_products()
    keyboard = [
        [InlineKeyboardButton(
            products["data"][product]["attributes"]["title"],
            callback_data=products["data"][product]["id"],)]
        for product in range(len(products["data"]))]
    reply_markup = InlineKeyboardMarkup(keyboard)
    keyboard.append([InlineKeyboardButton(
            "Моя корзина  🛒",
            callback_data="/go_cart")])
    if update.message:
        update.message.reply_text(
            "Please choose:",
            reply_markup=reply_markup)
    else:
        context.bot.send_message(
            chat_id=chat_id,
            text="Please choose:",
            reply_markup=reply_markup)
    return "HANDLE_DESCRIPTION"


def handle_description(update, context):
    strapi = context.bot_data['strapi']
    chat_id, message_id = get_chat_id_message_id(update, context)
    query = update.callback_query.data
    if query == '/go_cart':
        return handle_cart(update, context)
    if query == '/del_products':
        return handle_empty_cart(update, context)
    pic = strapi.get_picture(query)
    pic_url = pic["data"]["attributes"]["picture"]['data'][0]['attributes']['url']
    image_data = strapi.get_img(pic_url)
    product = strapi.get_product(query)
    title = product["data"]["attributes"]["title"]
    price = product["data"]["attributes"]["price"]
    description = product["data"]["attributes"]["description"]

    keyboard = [
        [InlineKeyboardButton(
            "Добавить в корзину",
            callback_data=f"{query}")],
        [InlineKeyboardButton(
            "Назад",
            callback_data="/back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_photo(
        chat_id=chat_id,
        photo=image_data,
        caption=f"{title} ({price} руб.):\n\n{description}",
        reply_markup=reply_markup)
    context.bot.delete_message(
        chat_id=chat_id,
        message_id=message_id)
    return "HANDLE_CART"


def handle_add_to_cart(update, context):
    strapi = context.bot_data['strapi']
    chat_id, message_id = get_chat_id_message_id(update, context)
    if update.callback_query:
        data = update.callback_query.data
    order = strapi.create_order(data)
    product = strapi.get_product(data)
    cart = strapi.get_or_create_cart(str(chat_id), order)
    query = update.callback_query
    query.answer(text=f'''{product['data']['attributes']['title']} добавлен в корзину''',
                 show_alert=True)
    context.bot.delete_message(
        chat_id=chat_id,
        message_id=message_id)
    return handle_menu(update, context)


def handle_cart(update, context):
    strapi = context.bot_data['strapi']
    chat_id, message_id = get_chat_id_message_id(update, context)
    query = update.callback_query.data
    if query.isdigit():
        return handle_add_to_cart(update, context)

    orders = strapi.get_orders(chat_id)
    message = ""
    for order in orders:
        message += "".join(
            f"""{order['attributes']['product']['data']['attributes']['title']}
            цена: {order['attributes']['product']['data']['attributes']['price']}
            вес: {order['attributes']['weight']}\n\n""")
    keyboard = [
        [InlineKeyboardButton(
            "В меню",
            callback_data="/back_to_menu")],
        [InlineKeyboardButton(
            "Оплатить",
            callback_data="/pay")],
        [InlineKeyboardButton(
            "Отказ от товаров",
            callback_data="/del_products")]]
    reply_markup = InlineKeyboardMarkup(keyboard)

    context.bot.send_message(
        chat_id=chat_id,
        text=message if message else "Корзина пуста",
        reply_markup=reply_markup)
    context.bot.delete_message(
        chat_id=chat_id,
        message_id=message_id)
    return "HANDLE_MENU"


def handle_empty_cart(update, context):
    strapi = context.bot_data['strapi']
    chat_id, message_id = get_chat_id_message_id(update, context)
    orders = strapi.get_orders(chat_id)
    for order in orders:
        strapi.del_order(order["id"])
    keyboard = [
        [InlineKeyboardButton(
            "В меню",
            callback_data="/back_to_menu")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    context.bot.send_message(
        chat_id=chat_id,
        text="Корзина пуста",
        reply_markup=reply_markup)
    context.bot.delete_message(
        chat_id=chat_id,
        message_id=message_id)
    return "HANDLE_MENU"


def handle_pay(update, context):
    chat_id, message_id = get_chat_id_message_id(update, context)
    context.bot.send_message(
        chat_id=chat_id,
        text="Отправьте свою почту для оплаты.")
    context.bot.delete_message(
        chat_id=chat_id,
        message_id=message_id)
    return "WAITING_EMAIL"


def handle_email(update, context):
    strapi = context.bot_data['strapi']
    chat_id, message_id = get_chat_id_message_id(update, context)
    username = update.effective_user.username
    if update.message:
        users_reply = update.message.text
    else:
        users_reply = update.callback_query.data
    cart = strapi.add_user_to_cart(
        chat_id,
        users_reply,
        username)
    update.message.reply_text("Пользователь сохранен в CMS.")
    context.bot.delete_message(
        chat_id=chat_id,
        message_id=message_id)
    return handle_empty_cart(update, context)


def handle_users_reply(update, context):
    db = get_database_connection()
    if update.message:
        user_reply = update.message.text
        chat_id = str(update.message.chat_id)
    elif update.callback_query:
        user_reply = update.callback_query.data
        chat_id = str(update.callback_query.message.chat_id)
    else:
        return
    if user_reply == "/start" or user_reply == "/back_to_menu":
        user_state = "HANDLE_MENU"
    else:
        user_state = db.get(chat_id).decode("utf-8")
    states_functions = {
        "HANDLE_MENU": handle_menu,
        "HANDLE_DESCRIPTION": handle_description,
        "HANDLE_CART": handle_cart,
        "HANDLE_EMPTY_CART": handle_empty_cart,
        "WAITING_EMAIL": handle_email,
    }
    state_handler = states_functions[user_state]
    try:
        next_state = state_handler(
            update,
            context)
        db.set(chat_id, next_state)
    except Exception as err:
        print(err)
        logger.exception(err)


def get_database_connection():
    global _database
    if _database is None:
        _database = redis.Redis()
    return _database


def main():
    env = Env()
    env.read_env()
    bot_token = env('BOT_TOKEN')
    api_token = env('API_TOKEN')
    main_url = env('MAIN_URL')
    headers = {"Authorization": f"Bearer {api_token}"}

    start = Strapi(main_url, headers)

    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
        filename='fish_bot.log'
    )
    updater = Updater(bot_token)
    dispatcher = updater.dispatcher
    dispatcher.bot_data['strapi'] = start
    dispatcher.add_handler(CallbackQueryHandler(handle_users_reply))
    dispatcher.add_handler(MessageHandler(Filters.text, handle_users_reply))
    dispatcher.add_handler(CommandHandler("start", handle_users_reply))
    updater.start_polling()
    updater.idle()


if __name__ == "__main__":
    main()

