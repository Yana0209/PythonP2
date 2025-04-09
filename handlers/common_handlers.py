from telebot import TeleBot
from keyboards.reply_keyboards import main_keyboard

def register_handlers(bot: TeleBot):
    @bot.message_handler(commands=['start'])
    def start(message):
        user_id = message.from_user.id
        bot.send_message(user_id, f"Вітаю, {message.from_user.first_name}! 👋\nЯ бот для замовлення корму для ваших улюбленців.\nОберіть дію:", reply_markup=main_keyboard())

    @bot.message_handler(func=lambda message: message.text == 'Допомога' or message.text == '/help')
    def help_command(message):
        help_text = """
Доступні команди:
/start - Початок роботи з ботом
/help - Список доступних команд
/info - Інформація про бота
/catalog - Переглянути каталог товарів
Мої замовлення - Переглянути історію замовлень
Залишити відгук - Надіслати відгук адміністраторам
/admin - Меню адміністратора (для адміністраторів)
        """
        bot.send_message(message.chat.id, help_text)

    @bot.message_handler(func=lambda message: message.text == 'Інфо' or message.text == '/info')
    def info_command(message):
        info_text = "Я чат-бот для замовлення кормів для домашніх тварин. Розроблений на Python з використанням бібліотеки TelebotAPI."
        bot.send_message(message.chat.id, info_text)

    @bot.message_handler(func=lambda message: message.text == '/hello')
    def hello_command(message):
        bot.send_message(message.chat.id, f"Привіт, {message.from_user.first_name}!")

