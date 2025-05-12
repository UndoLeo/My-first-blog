from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters, CallbackContext
import random

# Хранилище игроков: {user_id: {"name": "имя", "god": "бог", "role": "god/imposter"}}
players = {}
imposter = None  # ID импостера

# Список всех богов с заданиями
GODS = {
    "Зевс": {
        "emoji": "⚡️",
        "task": (
            "*«Громовержец, прими волю судьбы!»*\n\n"
            "Ты — царь богов, и твой долг — вершить правосудие, но не сегодня!\n"
            "- Ты **просишь дать себе задание у других**, не отлыниваешь — если сказал «сделаю», значит, брось молнию в того, кто усомнится!\n"
            "- Фиксируй выполненные квесты на свитке (или в телефоне), как истинный бюрократ Олимпа.\n\n"
            "_Девиз:_ *«Мне сказали — значит, будет так!»*"
        )
    },
    "Афродита": {
        "emoji": "🌹",
        "task": (
            "*«Богиня, чьи чары решают судьбы»*\n\n"
            "Ты — владычица любви, а значит, контролируешь эмоции.\n"
            "- Ты проверяешь, выполнены ли задания.\n"
            "- Веди список (красивый, с завитушками) и отмечай успехи/провалы.\n"
            "- Если кто-то не справился — напомни ему взглядом, что он тебе нравился... пока не разочаровал.\n\n"
            "_Девиз:_ *«Красота требует порядка!»*"
        )
    },
    "Деметра": {
        "emoji": "🌾",
        "task": (
            "*«Нежданная гостья с дарами»*\n\n"
            "Ты — богиня неожиданностей, как внезапный дождь в ясный день.\n"
            "- В течение дня тебе будут приходить спонтанные задания\n"
            "- Выполняй их без вопросов — таков закон природы.\n\n"
            "_Девиз:_ *«Жизнь — это поле, а я — её сеятель!»*"
        )
    },
    "Аид": {
        "emoji": "💀",
        "task": (
            "*«Владыка мудрости тьмы»*\n\n"
            "Ты — бог опыта, и твоя задача — поддержать 5 смертных перед экзаменами.\n"
            "- Дай совет.\n"
            "- Успокой паникёра.\n"
            "- Напомни, что даже в аду есть выход.\n"
            "- Если кто-то сдал — возьми с него символическую «монету Харона» (например, конфету).\n\n"
            "_Девиз:_ *«Смертные боятся тьмы, пока не увидят её властелина!»*"
        )
    },
    "Арес": {
        "emoji": "⚔️",
        "task": (
            "*«Бог, который не ходит один»*\n\n"
            "Ты — воин без права на одиночество.\n"
            "- Ты не можешь перемещаться сам — только если тебя ведут (как пленника, союзника или тень).\n"
            "- Если хочешь куда-то пойти — найди проводника и скажи: *«Веди меня, смертный!»*\n\n"
            "_Девиз:_ *«Даже война — это командная работа!»*"
        )
    },
    "Персефона": {
        "emoji": "🌸",
        "task": (
            "*«Царица, чей голос — дар»*\n\n"
            "Ты — богиня тишины и мудрости, но только когда тебе разрешают.\n"
            "- В обычной жизни молчи, пока не спросят.\n"
            "- Но на уроках/совещаниях ты обязана быть активной — иначе Аид разочаруется.\n\n"
            "_Девиз:_ *«Молчание — золото, но знание — бриллиант!»*"
        )
    },
    "Дионис": {
        "emoji": "🍷",
        "task": (
            "*«УЛЬТРА-МУЖИК»*\n\n"
            "Ты — бог решительности и виноградного сока.\n"
            "- Все твои фразы должны звучать как приказ олимпийской важности:\n"
            "  - *«Это моё решение!»*\n"
            "  - *«Потому что я так сказал!»*\n"
            "  - *«Сомневаешься? Выпей и согласись!»*\n"
            "- Никаких «может быть» — только абсолютная уверенность.\n\n"
            "_Девиз:_ *«Жизнь — пир, а я в ней — хозяин!»*"
        )
    },
    "Эрида": {
        "emoji": "🔥",
        "task": (
            "*«Сеятельница харизмы»*\n\n"
            "Ты — богиня небанальных комплиментов.\n"
            "- В течение дня сделай 5+ комплиментов, но не просто «ты красивая», а что-то вроде:\n"
            "  - *«Твой смех звучит, как победа над скукой!»*\n"
            "  - *«Ты носишь эту одежду, будто она соткана из твоей ауры!»*\n"
            "- Если кто-то смутился — ты победила.\n\n"
            "_Девиз:_ *«Раздор — это когда комплиментов слишком мало!»*"
        )
    },
    "Гестия": {
        "emoji": "🏡",
        "task": (
            "*«Богиня, которая должна кричать»*\n\n"
            "Ты — хранительница очага, но сегодня очаг — это твоя смелость.\n"
            "1. Взойди на возвышенность (стол, лестницу, подоконник).\n"
            "2. Прокричи фразу, чтобы услышали 10+ человек (например: *«Люди! Я запрещаю вам скучать сегодня!»*).\n"
            "3. Публично поспорь с кем-то (даже если не права) — главное, страсть!\n\n"
            "_Девиз:_ *«Даже тихий огонь может стать пожаром!»*"
        )
    },
    "Артемида": {
        "emoji": "🏹",
        "task": (
            "🌙 *«Поцелуй Артемиды» (Гипноз)*\n\n"
            "Ты — Импостер! Шепчи жертве:\n"
            "*«Ты хочешь уснуть...»* 👏 *[два хлопка]*\n"
            "⚠️ Главное условие: рядом не должно быть никого — иначе ритуал прервётся!\n\n"
            "---\n\n"
            "🏹 *Задание для Охотницы за смехом*\n"
            "Твоя миссия — распространять анекдоты, как заразные стрелы, но так, чтобы никто не заподозрил, что ты — Импостер!\n\n"
            "🔪 *Механика «Травли анекдотов»*\n"
            "🎯 Условия активации:\n"
            "1. Рядом должно быть минимум 5 человек *(иначе анекдот не засчитывается!)*.\n"
            "2. У тебя есть 30 секунд, чтобы выстрелить шуткой! ⏳\n\n"
            "🎭 *Правила маскировки:*\n"
            "- Шути естественно, но не переигрывай — иначе тебя раскроют!\n"
            "- Если кто-то заподозрит тебя, игра окончена...\n\n"
            "💀 *Последствия провала:*\n"
            "Придётся признаться: *«Меня убили... 💀»*\n\n"
            "🌟 *Совет от Артемиды:*\n"
            "_«Смех — лучшая тень для коварства. Пусть твои шутки будут острее стрел, а подозрения — тише лунного света...»_"
        ),
        "role": "imposter"
    }
}

def start(update: Update, context: CallbackContext):
    start_button = [[KeyboardButton("Начать игру")]]
    reply_markup = ReplyKeyboardMarkup(start_button, resize_keyboard=True)
    update.message.reply_text(
        "Добро пожаловать в игру «Тени Богов»!",
        reply_markup=reply_markup
    )

def handle_start_game(update: Update, context: CallbackContext):
    global imposter
    if not players:
        # Выбираем случайного импостера при первом запуске игры
        imposter = update.message.from_user.id
    
    update.message.reply_text(
        """🌌 Тени прошлого оживают... Боги обращают взор на смертных...

Только мудрейшие и доблестные смогут предотвратить хаос, что надвигается. 🔥⚡  

🔍 Ищите знаки в местах силы— там, где когда-то правили небожители.  

✨ Ваши действия :  
1. Введите своё Имя Бога (то самое, что открылось вам в видениях).  
2. Получите персональное испытание — лишь его выполнение откроет путь к спасению.  

⚠️ Но будьте осторожны! Среди вас есть предатель... 👁️  

Введите своё Имя Бога... и никому не доверяйте.🔮""",
        parse_mode="Markdown"
    )

def handle_god_name(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    god_name = update.message.text.strip()
    
    if god_name in GODS:
        # Определяем роль
        role = GODS[god_name].get("role", "god")
        
        # Сохраняем игрока
        players[user_id] = {
            "name": update.message.from_user.first_name,
            "god": god_name,
            "role": role,
            "alive": True
        }
        
        # Отправляем персонализированное задание
        god_data = GODS[god_name]
        header = "🕵️‍♂️ *ТЫ — ИМПОСТЕР!* 🕵️‍♂️\n\n" if role == "imposter" else "🏛 *Задания для Олимпийцев* 🏛\n\n"
        
        task_text = (
            f"{header}"
            f"{god_data['emoji']} *{update.message.from_user.first_name} ({god_name})*\n"
            f"{god_data['task']}"
        )
        
        update.message.reply_text(
            task_text,
            parse_mode="Markdown"
        )
        
        # Добавляем кнопки
        buttons = [
            [KeyboardButton("Меня убили... 💀")],
            [KeyboardButton("Проверить живых")]
        ]
        reply_markup = ReplyKeyboardMarkup(buttons, resize_keyboard=True)
        update.message.reply_text(
            "Выберите действие:",
            reply_markup=reply_markup
        )
    else:
        update.message.reply_text("⚠️ Это имя не значится в свитках богов! Попробуйте ещё раз.")

def handle_death(update: Update, context: CallbackContext):
    user_id = update.message.from_user.id
    if user_id in players and players[user_id]["alive"]:
        player = players[user_id]
        player["alive"] = False
        
        # Уведомляем всех живых игроков
        alive_players = [uid for uid, p in players.items() if p["alive"]]
        for uid in alive_players:
            try:
                context.bot.send_message(
                    chat_id=uid,
                    text=f"⚰️ *{player['name']} ({player['god']})* пал(а) жертвой {'предателя' if player['role'] == 'imposter' else 'хаоса'}...",
                    parse_mode="Markdown"
                )
            except:
                continue
        
        # Проверяем условия победы
        check_win_condition(context)
        
        update.message.reply_text("Вы выбыли из игры. Призраки не страдают! 👻")

def handle_check_alive(update: Update, context: CallbackContext):
    alive_list = [f"{p['name']} ({p['god']})" for p in players.values() if p["alive"]]
    dead_list = [f"{p['name']} ({p['god']})" for p in players.values() if not p["alive"]]
    
    response = "✨ *Живые боги:*\n" + "\n".join(alive_list) if alive_list else "Все боги мертвы... 💀"
    response += "\n\n☠️ *Павшие:*\n" + "\n".join(dead_list) if dead_list else "\n\nНикто не погиб... пока что."
    
    update.message.reply_text(
        response,
        parse_mode="Markdown"
    )

def check_win_condition(context: CallbackContext):
    alive_gods = sum(1 for p in players.values() if p["alive"] and p["role"] == "god")
    alive_imposters = sum(1 for p in players.values() if p["alive"] and p["role"] == "imposter")
    
    if alive_imposters == 0:
        # Импостер убит
        for uid, player in players.items():
            if player["alive"]:
                context.bot.send_message(
                    chat_id=uid,
                    text="✨ *Боги победили!* Хаос отступил, а предатель повержен. ⚡",
                    parse_mode="Markdown"
                )
    elif alive_gods < 5:
        # Импостер победил
        for uid, player in players.items():
            if player["alive"] and player["role"] == "imposter":
                context.bot.send_message(
                    chat_id=uid,
                    text="🎭 *Импостер побеждает!* Тьма поглотила Олимп... 🌑",
                    parse_mode="Markdown"
                )

def main():
    updater = Updater("7679825815:AAEQlaugFqXFPuCjpDXXsr5-476YwS1PZDc", use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(MessageHandler(Filters.regex("^Начать игру$"), handle_start_game))
    dp.add_handler(MessageHandler(Filters.regex("^Проверить живых$"), handle_check_alive))
    dp.add_handler(MessageHandler(Filters.regex("^Меня убили"), handle_death))
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_god_name))

    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
