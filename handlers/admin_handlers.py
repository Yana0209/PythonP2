from telebot import TeleBot, types
from config import ADMIN_IDS
from keyboards.reply_keyboards import admin_keyboard, main_keyboard
from utils.validators import is_float
from database.database import create_connection, execute_query, fetch_all, fetch_one, close_connection

ADD_ITEM_STATES = {}

def is_admin(user_id):
    return user_id in ADMIN_IDS

def register_handlers(bot: TeleBot):
    @bot.message_handler(commands=['admin'])
    def admin_command(message):
        user_id = message.from_user.id
        if is_admin(user_id):
            bot.send_message(user_id, "Адмін-панель:", reply_markup=admin_keyboard())
        else:
            bot.send_message(user_id, "Ви не є адміністратором.")

    @bot.message_handler(func=lambda message: message.text == 'Додати товар', chat_types=['private'])
    def add_item_command(message):
        user_id = message.from_user.id
        if is_admin(user_id):
            bot.send_message(user_id, "Введіть назву товару:")
            ADD_ITEM_STATES[user_id] = 'waiting_for_name'
        else:
            bot.send_message(user_id, "Немає доступу.")

    @bot.message_handler(func=lambda message: message.chat.type == 'private' and ADD_ITEM_STATES.get(message.from_user.id) == 'waiting_for_name')
    def get_item_name(message):
        user_id = message.from_user.id
        ADD_ITEM_STATES[user_id] = {'name': message.text}
        bot.send_message(user_id, "Введіть опис товару:")
        ADD_ITEM_STATES[user_id]['state'] = 'waiting_for_description'

    @bot.message_handler(func=lambda message: message.chat.type == 'private' and ADD_ITEM_STATES.get(message.from_user.id, {}).get('state') == 'waiting_for_description')
    def get_item_description(message):
        user_id = message.from_user.id
        ADD_ITEM_STATES[user_id]['description'] = message.text
        bot.send_message(user_id, "Введіть ціну товару:")
        ADD_ITEM_STATES[user_id]['state'] = 'waiting_for_price'

    @bot.message_handler(func=lambda message: message.chat.type == 'private' and ADD_ITEM_STATES.get(message.from_user.id, {}).get('state') == 'waiting_for_price')
    def get_item_price(message):
        user_id = message.from_user.id
        price = message.text
        if is_float(price):
            ADD_ITEM_STATES[user_id]['price'] = float(price)
            save_new_item(bot, user_id)
        else:
            bot.send_message(user_id, "Будь ласка, введіть коректну ціну (число).")
            ADD_ITEM_STATES[user_id]['state'] = 'waiting_for_price'

    def save_new_item(bot, user_id):
        conn = create_connection()
        if conn:
            cursor = execute_query(conn, "INSERT INTO products (name, description, price) VALUES (?, ?, ?)",
                                   (ADD_ITEM_STATES[user_id]['name'], ADD_ITEM_STATES[user_id]['description'],
                                    ADD_ITEM_STATES[user_id]['price']))
            close_connection(conn)
            if cursor:
                bot.send_message(user_id, f"Товар '{ADD_ITEM_STATES[user_id]['name']}' додано до каталогу.", reply_markup=admin_keyboard())
            else:
                bot.send_message(user_id, "Помилка при додаванні товару.", reply_markup=admin_keyboard())
        else:
            bot.send_message(user_id, "Помилка підключення до БД.", reply_markup=admin_keyboard())
        del ADD_ITEM_STATES[user_id]

    @bot.message_handler(func=lambda message: message.text == 'Видалити товар', chat_types=['private'])
    def remove_item_command(message):
        user_id = message.from_user.id
        if is_admin(user_id):
            bot.send_message(user_id, "Введіть ID товару, який потрібно видалити:")
            bot.register_next_step_handler(message, process_remove_item)
        else:
            bot.send_message(user_id, "Немає доступу.")

    def process_remove_item(message):
        user_id = message.from_user.id
        if is_admin(user_id):
            item_id = message.text
            if item_id.isdigit():
                conn = create_connection()
                if conn:
                    cursor = execute_query(conn, "DELETE FROM products WHERE id = ?", (item_id,))
                    close_connection(conn)
                    if cursor and cursor.rowcount > 0:
                        bot.send_message(user_id, f"Товар з ID '{item_id}' видалено.", reply_markup=admin_keyboard())
                    else:
                        bot.send_message(user_id, f"Товар з ID '{item_id}' не знайдено.", reply_markup=admin_keyboard())
                else:
                    bot.send_message(user_id, "Помилка підключення до БД.", reply_markup=admin_keyboard())
            else:
                bot.send_message(user_id, "Будь ласка, введіть коректний ID товару (число).")
                bot.register_next_step_handler(message, process_remove_item)

    @bot.message_handler(func=lambda message: message.text == 'Переглянути замовлення', chat_types=['private'])
    def view_orders_command(message):
        user_id = message.from_user.id
        if is_admin(user_id):
            conn = create_connection()
            if conn:
                cursor = execute_query(conn, """
                    SELECT o.id, u.telegram_id, p.name, o.quantity, o.order_date
                    FROM orders o
                    JOIN users u ON o.user_id = u.id
                    JOIN products p ON o.product_id = p.id
                """)
                orders = fetch_all(cursor)
                close_connection(conn)
                if orders:
                    orders_text = "Список замовлень:\n"
                    for order in orders:
                        orders_text += f"- ID замовлення: {order[0]}, Користувач ID: {order[1]}, Товар: {order[2]}, Кількість: {order[3]}, Дата: {order[4]}\n"
                    bot.send_message(user_id, orders_text, reply_markup=admin_keyboard())
                else:
                    bot.send_message(user_id, "Немає жодних замовлень.", reply_markup=admin_keyboard())
            else:
                bot.send_message(user_id, "Помилка підключення до БД.", reply_markup=admin_keyboard())
        else:
            bot.send_message(user_id, "Немає доступу.")

    @bot.message_handler(func=lambda message: message.text == 'Назад' or message.text == '⬅️ Назад',
                         chat_types=['private'])
    def admin_back_to_main_menu(message):
        user_id = message.from_user.id
        if is_admin(user_id):
            from keyboards.reply_keyboards import \
                main_keyboard  # Імпортуємо main_keyboard тут, щоб уникнути циклічних імпортів
            bot.send_message(user_id, "Головне меню:", reply_markup=main_keyboard())
        else:
            bot.send_message(user_id, "Ви не є адміністратором.")

def register_admin_handlers(bot):
    register_handlers(bot)