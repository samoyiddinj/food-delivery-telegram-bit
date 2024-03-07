from telegram import (Update, KeyboardButton, ReplyKeyboardMarkup,
                      InlineKeyboardButton, InlineKeyboardMarkup)
from telegram.ext import (ApplicationBuilder, CommandHandler, ContextTypes,
                          MessageHandler, filters, CallbackQueryHandler)
async def start(update, context):
    user = update.message.from_user
    print(user, user.username, user.id)
    buttons = [
        [
            KeyboardButton("Share contact", request_contact=True),
            KeyboardButton("Share location", request_location=True),
            KeyboardButton("share poll", request_poll=True)

        ],
        [
            KeyboardButton("buyurtma qilish"),
            KeyboardButton("tolov sozlamalari"),
            KeyboardButton("Biz haqimizda")
        ],
        [
            KeyboardButton("Manzillarimiz")
        ]
    ]
    await update.message.reply_text(f'to\'lov sozlamalari{update.effective_user.first_name}',
                                    reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True))
    # await context.bot.send_message(1779578835, f"Hello Rahmatullo")


async def get(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(f'Salom {update.effective_user.first_name}')


async def get_student_list(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.message.text
    user = update.message.from_user
    print(user.username, msg)
    if msg == "buyurtma qilish":
        buttons = [
            [
                InlineKeyboardButton(text="weeest", callback_data="menu11"),
                InlineKeyboardButton(text="menu2", callback_data="menu22"),
            ],
            [
                InlineKeyboardButton(text="kanalga azo boling", url="https://t.me/samoyiddin6265")
            ]
        ]



async def callback_handler(update, context):
    query = update.callback_query.message
    print(update.callback_query.data)
    if update.callback_query.data == 'menu11':
        await update.callback_query.message.reply_text("Siz menu1 ni bosdingiz")
    else:
        await update.callback_query.message.reply_text("Siz boshqasini bosdingiz")


app = ApplicationBuilder().token("6740760413:AAE8wyGtR2CpRq_Lex6ZH_qI5GlVl2mF678").build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("reply", get))
app.add_handler(MessageHandler(filters=filters.TEXT, callback=get_student_list))
app.add_handler(CallbackQueryHandler(callback_handler))

app.run_polling()






