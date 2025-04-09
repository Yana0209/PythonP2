from telebot import types

def main_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_catalog = types.KeyboardButton('Каталог')
    btn_cart = types.KeyboardButton('Кошик')
    btn_order = types.KeyboardButton('Зробити замовлення')
    btn_help = types.KeyboardButton('Допомога')
    btn_feedback = types.KeyboardButton('Залишити відгук')
    btn_clear_cart = types.KeyboardButton('Очистити кошик')
    markup.row(btn_catalog, btn_cart)
    markup.row(btn_order, btn_help)
    markup.row(btn_feedback, btn_clear_cart)
    return markup

def get_catalog_keyboard():
    """Створює Reply Keyboard для переходу назад до головного меню."""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_back = types.KeyboardButton('⬅️ Назад')
    markup.add(btn_back)
    return markup

def admin_keyboard():
    """Створює Reply Keyboard для адміністраторів."""
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_add_item = types.KeyboardButton('Додати товар')
    btn_remove_item = types.KeyboardButton('Видалити товар')
    btn_view_orders = types.KeyboardButton('Переглянути замовлення')
    btn_back = types.KeyboardButton('⬅️ Назад')
    markup.add(btn_add_item, btn_remove_item, btn_view_orders)
    markup.add(btn_back)
    return markup

def phone_request_keyboard():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    btn_phone = types.KeyboardButton('Поділитися номером телефону', request_contact=True)
    markup.add(btn_phone)
    btn_back = types.KeyboardButton('⬅️ Назад') # Використовуємо визначену змінну btn_back
    markup.add(btn_back)
    return markup