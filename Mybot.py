from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, CallbackContext

TOKEN = "7227514540:AAEquCHU_rNdCJisY2fZgA0MHFbPMmV-DDc"

# Данные для Маяка
beacon_colors = {
    "цвет морской волны": "https://t.me/+PZd4QJ2fucVmZTky",
    "лайм": "https://t.me/+Q5ONlS_qUx83MzIy",
    "золотой": "https://t.me/+56rE7E2rLso5M2Fi",
    "фиолетовый": "https://t.me/+l6keDJRh22lmNGIy",
    "оранжевый": "https://t.me/+eofyLX9SQUFhMTk6",
    "розовый металлик": "https://t.me/+jYlgDiLOV8hhZDYy",
    "желтый неон": "https://t.me/+4frnD2bwreQzNWQy",
    "белый": "https://t.me/+9u3RdULBAR4yZjRi",
    "розовый неон": "https://t.me/+CFV5B-tn2B8yY2Qy",
    "красный неон": "https://t.me/+ZZvN0GTa9sg0NDgy"
}

# Данные для Причала
pier_colors = {
    "черный": "https://t.me/+O3Zg_KnEeXdiYjJi",
    "серебро": "https://t.me/+pnt1roIIrJ83YjIy",
    "сиреневый": "https://t.me/+yJKnbcoMJO42MzUy",
    "красный": "https://t.me/+YYQx9W3SvsZjZTky",
    "фиолетовый неон": "https://t.me/+uu-q7K_v2K45YmZi",
    "голубой": "https://t.me/+N32Z7TrOSLYxMmFi",
    "синий": "https://t.me/+HryiBRzhAvU4Yzcy",
    "желтый": "https://t.me/+zK2qj5pG_PthNWNi",
    "зеленый": "https://t.me/+XnIhC5RBFJplNDRi",
    "розовый неон": "https://t.me/+QZyg0w5mYQQ2ODIy"
}

def start(update: Update, context: CallbackContext) -> None:
    keyboard = [
        [InlineKeyboardButton("Маяк", callback_data='beacon')],
        [InlineKeyboardButton("Причал", callback_data='pier')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    update.message.reply_text('Выберите тип:', reply_markup=reply_markup)

def button(update: Update, context: CallbackContext) -> None:
    query = update.callback_query
    query.answer()

    if query.data in ['beacon', 'pier']:
        context.user_data['type'] = query.data
        colors = beacon_colors if query.data == 'beacon' else pier_colors
        buttons = [[InlineKeyboardButton(color, callback_data=color)] for color in colors]
        reply_markup = InlineKeyboardMarkup(buttons)
        query.edit_message_text(text="Выберите цвет:", reply_markup=reply_markup)
    else:
        selected_type = context.user_data.get('type')
        colors_dict = beacon_colors if selected_type == 'beacon' else pier_colors
        link = colors_dict.get(query.data)
        if link:
            query.edit_message_text(text=f"Ваша ссылка: {link}")
        else:
            query.edit_message_text(text="Ошибка: цвет не найден")

def main() -> None:
    updater = Updater(TOKEN)
    dispatcher = updater.dispatcher
    dispatcher.add_handler(CommandHandler('start', start))
    dispatcher.add_handler(CallbackQueryHandler(button))
    updater.start_polling()
    updater.idle()

if __name__ == '__main__':
    main()
