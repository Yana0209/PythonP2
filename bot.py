from database import database as db
import telebot
from config import BOT_TOKEN
from database.database import initialize_database
from handlers import common_handlers, user_handlers, admin_handlers

bot = telebot.TeleBot(BOT_TOKEN)



if __name__ == '__main__':
    db.initialize_database()
    initialize_database()
    common_handlers.register_handlers(bot)
    user_handlers.register_handlers(bot)
    admin_handlers.register_handlers(bot)
    bot.polling(none_stop=True)

