from telebot import TeleBot, types

import config
from keyboards.inline_keyboards import catalog_keyboard
from keyboards.reply_keyboards import main_keyboard, phone_request_keyboard
from database.database import create_connection, execute_query, fetch_all, fetch_one, close_connection
from utils.cart_data import cart  # Імпортуємо словник кошика

user_states = {}
WAITING_PHONE = 1

def register_handlers(bot: TeleBot):
    @bot.message_handler(func=lambda message: message.text == 'Каталог' or message.text == '/catalog')
    def catalog_command(message):
        conn = create_connection()
        if conn:
            cursor = execute_query(conn, "SELECT id, name FROM products")
            products = fetch_all(cursor)
            close_connection(conn)
            if products:
                markup = catalog_keyboard([{'id': p[0], 'name': p[1]} for p in products])
                bot.send_message(message.chat.id, "Оберіть товар:", reply_markup=markup)
            else:
                bot.send_message(message.chat.id, "Товари відсутні.")
        else:
            bot.send_message(message.chat.id, "Помилка підключення до бази даних.")

    @bot.callback_query_handler(func=lambda call: call.data.startswith('product_'))
    def product_detail_callback(call):
        product_id_str = call.data.split('_')[1]
        try:
            product_id = int(product_id_str)
        except ValueError:
            bot.answer_callback_query(call.id, "Помилка обробки товару.")
            return
        conn = create_connection()
        if conn:
            cursor = execute_query(conn, "SELECT name, description, price FROM products WHERE id = ?", (product_id,))
            product = fetch_one(cursor)
            close_connection(conn)
            if product:
                name, description, price = product
                markup = types.InlineKeyboardMarkup()
                btn_add_to_cart = types.InlineKeyboardButton('Додати в кошик', callback_data=f'add_to_cart_{product_id}')
                markup.add(btn_add_to_cart)
                bot.send_message(call.message.chat.id, f"<b>{name}</b>\n\n{description}\nЦіна: {price} грн.",
                                 parse_mode='html', reply_markup=markup)
            else:
                bot.answer_callback_query(call.id, "Інформацію про товар не знайдено.")

    @bot.callback_query_handler(func=lambda call: call.data.startswith('add_to_cart_'))
    def add_to_cart_callback(call):
        item_id_str = call.data.split('_')[3]
        try:
            item_id = int(item_id_str)
        except ValueError:
            bot.answer_callback_query(call.id, "Помилка обробки товару.")
            return
        conn = create_connection()
        if conn:
            cursor = execute_query(conn, "SELECT name FROM products WHERE id = ?", (item_id,))
            product = fetch_one(cursor)
            close_connection(conn)
            if product:
                user_id = call.from_user.id
                if user_id not in cart:
                    cart[user_id] = {}
                if item_id not in cart[user_id]:
                    cart[user_id][item_id] = 1
                    bot.answer_callback_query(call.id, f"Товар '{product[0]}' додано до кошика!")
                else:
                    cart[user_id][item_id] += 1
                    bot.answer_callback_query(call.id, f"Кількість товару '{product[0]}' у кошику збільшено!")
            else:
                bot.answer_callback_query(call.id, "Товар не знайдено.")

    @bot.message_handler(func=lambda message: message.text == 'Кошик')
    def view_cart_command(message):
        user_id = message.from_user.id
        if user_id in cart and cart[user_id]:
            cart_items = cart[user_id]
            cart_text = "Ваш кошик:\n"
            total_price = 0
            conn = create_connection()
            if conn:
                for product_id, quantity in cart_items.items():
                    try:
                        product_id_int = int(product_id)
                        cursor = execute_query(conn, "SELECT name, price FROM products WHERE id = ?", (product_id_int,))
                        product = fetch_one(cursor)
                        if product:
                            name, price = product
                            item_total = price * quantity
                            cart_text += f"- {name} (кількість: {quantity}) - {item_total} грн\n"
                            total_price += item_total
                        else:
                            cart_text += f"- Невідомий товар (id: {product_id}, кількість: {quantity})\n"
                    except ValueError:
                        cart_text += f"- Помилка ID товару: {product_id} (кількість: {quantity})\n"
                close_connection(conn)
                cart_text += f"\nЗагальна сума: {total_price} грн"
                bot.send_message(user_id, cart_text)
            else:
                bot.send_message(user_id, "Помилка підключення до БД при отриманні інформації про товари в кошику.")
        else:
            bot.send_message(user_id, "Ваш кошик порожній.")

    @bot.message_handler(func=lambda message: message.text == 'Очистити кошик')
    def clear_cart_command(message):
        user_id = message.from_user.id
        if user_id in cart:
            del cart[user_id]
            bot.send_message(user_id, "Ваш кошик очищено.")
        else:
            bot.send_message(user_id, "Ваш кошик і так порожній.")

    @bot.message_handler(func=lambda message: message.text == 'Зробити замовлення')
    def checkout_command(message):
        user_id = message.from_user.id
        if user_id in cart and cart[user_id]:
            bot.send_message(user_id, "Будь ласка, поділіться своїм номером телефону для зв'язку з менеджером.",
                             reply_markup=phone_request_keyboard())
            user_states[user_id] = WAITING_PHONE
        else:
            bot.send_message(user_id, "Ваш кошик порожній. Неможливо зробити замовлення.")

    @bot.message_handler(content_types=['contact', 'text'],
                         func=lambda message: user_states.get(message.from_user.id) == WAITING_PHONE)
    def process_phone_number(message):
        user_id = message.from_user.id
        phone_number = None

        if message.content_type == 'contact':
            phone_number = message.contact.phone_number
        elif message.content_type == 'text':
            phone_number = message.text

        if phone_number:
            bot.send_message(user_id, "Дякуємо за ваше замовлення! Менеджер зв'яжеться з вами найближчим часом.")
            del user_states[user_id]
            if user_id in cart:
                del cart[user_id]
        elif message.text == '⬅️ Назад до каталогу':  # Оновлена умова
            del user_states[user_id]
            conn = create_connection()
            if conn:
                cursor = execute_query(conn, "SELECT id, name FROM products")
                products = fetch_all(cursor)
                close_connection(conn)
                if products:
                    markup = catalog_keyboard([{'id': p[0], 'name': p[1]} for p in products])
                    bot.send_message(user_id, "Оберіть товар:", reply_markup=markup)
                else:
                    bot.send_message(user_id, "Товари відсутні.")
            else:
                bot.send_message(user_id, "Помилка підключення до бази даних.")
        else:
            bot.send_message(user_id, "Будь ласка, надішліть свій номер телефону коректно.")


    @bot.callback_query_handler(func=lambda call: call.data.startswith('order_product_'))
    def order_product_callback(call):
        product_id = call.data.split('_')[2]
        conn = create_connection()
        if conn:
            cursor = execute_query(conn, "SELECT name FROM products WHERE id = ?", (product_id,))
            product = fetch_one(cursor)
            close_connection(conn)
            if product:
                markup = types.InlineKeyboardMarkup()
                btn_add_to_cart = types.InlineKeyboardButton('Додати в кошик', callback_data=f'add_to_cart_{product_id}')
                markup.add(btn_add_to_cart)
                bot.send_message(call.message.chat.id, f"Ви бажаєте додати '{product[0]}' до кошика?", reply_markup=markup)
            else:
                bot.answer_callback_query(call.id, "Товар не знайдено.")

    @bot.callback_query_handler(func=lambda call: call.data == 'cancel_order')
    def cancel_order_callback(call):
        bot.send_message(call.message.chat.id, "Замовлення скасовано.")
        bot.answer_callback_query(call.id, "Замовлення скасовано.")

    @bot.message_handler(func=lambda message: message.text == 'Допомога')
    def help_command(message):
        bot.send_message(message.chat.id, "Тут буде інформація про допомогу.")

    @bot.message_handler(func=lambda message: message.text == 'Залишити відгук' or message.text == '/feedback')
    def feedback_command(message):
        bot.send_message(message.chat.id, "Будь ласка, напишіть ваш відгук:")
        bot.register_next_step_handler(message, process_feedback)

    @bot.message_handler(func=lambda message: message.text == '⬅️ Назад')
    def back_to_main_menu(message):
        bot.send_message(message.chat.id, "Головне меню", reply_markup=main_keyboard())

    def process_feedback(message):
        feedback_text = f"Відгук від користувача {message.from_user.id} ({message.from_user.username}):\n{message.text}"
        for admin_id in config.ADMIN_IDS:
            bot.send_message(admin_id, feedback_text)
        bot.send_message(message.chat.id, "Дякуємо за ваш відгук!")


    def register_user_handlers(bot):
        register_handlers(bot)