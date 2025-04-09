from telebot import types

def catalog_keyboard(products):
    """Створює Inline Keyboard з переліком товарів."""
    markup = types.InlineKeyboardMarkup()
    for product in products:
        markup.add(types.InlineKeyboardButton(product['name'], callback_data=f'product_{product["id"]}'))
    return markup

def product_detail_keyboard(product_id):
    """Створює Inline Keyboard з кнопкою "Замовити" для товару."""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Замовити', callback_data=f'order_product_{product_id}'))
    return markup

def confirm_order_keyboard(product_id):
    """Створює Inline Keyboard для підтвердження замовлення."""
    markup = types.InlineKeyboardMarkup()
    markup.add(types.InlineKeyboardButton('Підтвердити', callback_data=f'confirm_order_{product_id}'))
    markup.add(types.InlineKeyboardButton('Відмінити', callback_data='cancel_order'))
    return markup