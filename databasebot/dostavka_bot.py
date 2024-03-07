from db import Database
from datetime import datetime
from telegram import (Update, InlineKeyboardButton, InlineKeyboardMarkup,
                      KeyboardButton, ReplyKeyboardMarkup)
from telegram.ext import (ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, CallbackQueryHandler,
                          filters)
from globals import TEXT

db = Database()


async def main_menu(update, context, id, message):
    lang = int(db.get_user(id)['lang'])
    db.add_log(user_id=id, log=4)
    mainbuttons = [
        [
            KeyboardButton(text="Buyurtma berish")
        ],
        [
            KeyboardButton(text="Buyurtmalar tarixi")
        ],
        [
            KeyboardButton(text="Biz haqimizda"),
            KeyboardButton(text="Sozalamalar")
        ]
    ]
    await update.message.reply_text(message,
                                    reply_markup=ReplyKeyboardMarkup(mainbuttons, resize_keyboard=True,
                                                                     one_time_keyboard=True))


async def start(update, context):
    user = update.message.from_user
    today = datetime.now()
    id = user.id
    user_data = db.get_user(id)

    if not user_data:
        db.add_user(chat_id=user.id, tg_firstname=user.first_name, tg_username=user.username, joined_date=str(today))
        user_data = db.get_user(user.id)
    db.add_log(user_data["id"], log="1")
    con = db.add_basket(id)
    print(con)
    db.add_basket(user_data['id'])
    bucket_id = db.get_bucket(user_data["id"])
    print(bucket_id['id'])
    db.clear_bucket(bucket_id['id'])

    if not user_data["lang"]:
        buttons = [
            [
                InlineKeyboardButton(text="O'zbekcha🇺🇿", callback_data="lang_1"),
                InlineKeyboardButton(text="English🇬🇧", callback_data="lang_2"),
                InlineKeyboardButton(text="Русский🇷🇺", callback_data="lang_3"),
            ]
        ]

        await update.message.reply_text(
            "<i>🇺🇿Tilni tanlang\n🇬🇧Choose language\n🇷🇺Выберите язык</i>",
            reply_markup=InlineKeyboardMarkup(buttons),
            parse_mode="HTML"
        )

    elif not user_data["fullname"]:
        db.add_log(user_data["id"], log="2")
        await update.message.reply_text(
            TEXT["TEXT_FULLNAME"][user_data["lang"]],
            reply_markup=None
        )
    elif not user_data["phone_number"]:
        db.add_log(user_data["id"], log="3")
        button = [
            [KeyboardButton(TEXT["BTN_CONTACT"][user_data["lang"]], request_contact=True)]
        ]
        await update.message.reply_text(TEXT["TEXT_CONTACT"][user_data["lang"]],
                                        reply_markup=ReplyKeyboardMarkup(button, resize_keyboard=True))

    else:
        buttons = [
            [
                KeyboardButton("Menu")
            ],
            [
                KeyboardButton("Buyurtmalar tarixi"),
                KeyboardButton("Manzillarimiz")
            ],
            [
                KeyboardButton("Sozlamalar"),
                KeyboardButton("Biz haqimizda")
            ]

        ]
        db.add_log(user_id=user_data["id"], log=4)
        await update.message.reply_text("Assalomu alaykum",
                                        reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True,
                                                                         one_time_keyboard=True))


async def callback_handler(update, context):
    data = update.callback_query.data
    print('dataaaaaa', data)
    user = update.callback_query.from_user
    message_id = update.callback_query.message.message_id
    data = data.split('_')
    user_data = db.get_user(user.id)
    stage = db.get_log(user_data["id"])

    if data[0] == "lang":
        db.add_user(chat_id=user.id, lang=int(data[1]))
        db.add_log(user_data["id"], log="2")
        await context.bot.delete_message(chat_id=user.id, message_id=message_id)
        await update.callback_query.message.reply_text(
            TEXT["TEXT_FULLNAME"][int(data[1])],
            reply_markup=None
        )
    elif data[0] == "category":
        db.add_log(user_id=user_data["id"], log='101')
        products = db.get_products(int(data[1]))
        product_button = []
        temp_button = []
        for product in products:
            temp_button.append(InlineKeyboardButton(text=f"{product['name']}",
                                                    callback_data=f"product_{product['id']}"))
            if len(temp_button) == 2:
                product_button.append(temp_button)
                temp_button = []
        if len(temp_button) == 1:
            product_button.append(temp_button)

        product_button.append([InlineKeyboardButton(text="Orqaga", callback_data="product_back")])

        if products:
            category_photo = products[0]["category_photo"]
            category_name = products[0]["category_name"]

            await context.bot.delete_message(chat_id=user.id, message_id=message_id)
            await update.callback_query.message.reply_photo(photo=open(f"{category_photo}", "rb"),
                                                            caption=category_name,
                                                            reply_markup=InlineKeyboardMarkup(product_button))
    elif data[0] == "product":
        if data[1] == "back":
            await context.bot.delete_message(chat_id=user.id, message_id=message_id)
            db.add_log(user_id=user_data["id"], log="100")
            categories = db.get_category()
            category_button = []
            temp_button = []
            for category in categories:

                temp_button.append(InlineKeyboardButton(text=f"{category['name']}",
                                                        callback_data=f"category_{category['id']}"))

                if len(temp_button) == 2:
                    category_button.append(temp_button)

                    temp_button = []

            if len(temp_button) == 1:
                category_button.append(temp_button)

            category_button.append([InlineKeyboardButton(text="Asosiy menyu",
                                                         callback_data="main_menu")])

            category_button.append([InlineKeyboardButton(text="Savatcha",
                                                         callback_data="get_bucket")])

            await update.callback_query.message.reply_text(
                "Kategoriyalardan birini tanlang. (https://telegra.ph/Taomnoma-09-30)",

                reply_markup=InlineKeyboardMarkup(category_button))
        else:

            await context.bot.delete_message(chat_id=user.id, message_id=message_id)
            db.add_log(user_id=user_data["id"], log='201')
            product = db.get_details(int(data[1]))
            print(product)
            product_photo = product["photo"]
            product_name = product["name"]

            product_button = [
                [
                    InlineKeyboardButton(text="-", callback_data=f"detail_-_1_{product['id']}"),
                    InlineKeyboardButton(text=1, callback_data=f"detail{product['id']}"),
                    InlineKeyboardButton(text="+", callback_data=f"detail_+_1_{product['id']}")

                ],
                [
                    InlineKeyboardButton(text="Savatga qo'shish", callback_data=f"detail_add-bucket_1_{product['id']}")
                ],
                [
                    InlineKeyboardButton(text="Orqaga", callback_data=f"detail_back_{product['id']}")
                ]

            ]
            await update.callback_query.message.reply_photo(photo=open(f"{product_photo}", "rb"),
                                                            caption=f"{product_name}\nTavsifi: {product['description']}\nNarxi: {product['price']}",
                                                            reply_markup=InlineKeyboardMarkup(product_button))
    elif data[0] == "detail":
        if data[1] == "+":
            product = db.get_details(int(data[3]))
            print(product)
            product_photo = product["photo"]
            product_name = product["name"]

            product_button = [
                [
                    InlineKeyboardButton(text="-", callback_data=f"detail_-_{1 + int(data[2])}_{product['id']}"),
                    InlineKeyboardButton(text=1 + int(data[2]), callback_data='detail'),
                    InlineKeyboardButton(text="+", callback_data=f"detail_+_{1 + int(data[2])}_{product['id']}")

                ],
                [
                    InlineKeyboardButton(text="Savatga qo'shish",
                                         callback_data=f"detail_add-bucket_{1 + int(data[2])}_{product['id']}")
                ],
                [
                    InlineKeyboardButton(text="Orqaga", callback_data=f"detail_back_{product['id']}")

                ]

            ]
            await context.bot.edit_message_caption(chat_id=user.id, message_id=message_id,
                                                   caption=f"{product_name}\nTavsifi: {product['description']}\nNarxi: {int(product['price'])} * {int(data[2]) + 1}  = {int(product['price']) * (int(data[2]) + 1)}",
                                                   reply_markup=InlineKeyboardMarkup(product_button))
        elif data[1] == "-":
            if int(data[2]) > 1:
                product = db.get_details(int(data[3]))
                print(product)
                product_photo = product["photo"]
                product_name = product["name"]
                product_button = [
                    [
                        InlineKeyboardButton(text="-", callback_data=f"detail_-_{int(data[2]) - 1}_{product['id']}"),
                        InlineKeyboardButton(text=int(data[2]) - 1, callback_data="detail"),
                        InlineKeyboardButton(text="+", callback_data=f"detail_+_{int(data[2]) - 1}_{product['id']}")

                    ],
                    [
                        InlineKeyboardButton(text="Savatga qo'shish",
                                             callback_data=f"detail_add-bucket_{int(data[2]) - 1}_{product['id']}_{product['name']}_")
                    ],
                    [
                        InlineKeyboardButton(text="Orqaga", callback_data=f"detail_back_{product['id']}")
                    ]

                ]
                await context.bot.edit_message_caption(chat_id=user.id, message_id=message_id,
                                                       caption=f"{product_name}\nTavsifi: {product['description']}\nNarxi: {int(product['price'])} * {int(data[2]) - 1}  = {int(product['price']) * (int(data[2]) - 1)}",
                                                       reply_markup=InlineKeyboardMarkup(product_button))
        elif data[1] == "back":

            db.add_log(user_id=user_data["id"], log='101')
            category = db.get_category_id(int(data[2]))
            products = db.get_products(category['category_id'])
            product_button = []
            temp_button = []
            for product in products:
                temp_button.append(InlineKeyboardButton(text=f"{product['name']}",
                                                        callback_data=f"product_{product['id']}"))
                if len(temp_button) == 2:
                    product_button.append(temp_button)
                    temp_button = []
            if len(temp_button) == 1:
                product_button.append(temp_button)

            product_button.append([InlineKeyboardButton(text="Orqaga", callback_data="product_back")])

            if products:
                category_photo = products[0]["category_photo"]
                category_name = products[0]["category_name"]

                await context.bot.delete_message(chat_id=user.id, message_id=message_id)
                await update.callback_query.message.reply_photo(photo=open(f"{category_photo}", "rb"),
                                                                caption=category_name,
                                                                reply_markup=InlineKeyboardMarkup(product_button))
        elif data[1] == "add-bucket":
            product_id = data[3]
            count = data[2]
            user_data = db.get_user(user.id)
            bucket_id = db.get_bucket(user_data["id"])
            print(bucket_id['id'])
            db.add_item(bucket_id["id"], product_id, int(count))
            db.add_log(user_id=user.id, log=100)

            product = db.get_details(int(product_id))
            products = db.get_products(product['category_id'])
            product_button = []
            temp_button = []
            for product in products:
                temp_button.append(InlineKeyboardButton(text=f"{product['name']}",
                                                        callback_data=f"product_{product['id']}"))
                if len(temp_button) == 2:
                    product_button.append(temp_button)
                    temp_button = []
            if len(temp_button) == 1:
                product_button.append(temp_button)

            product_button.append([
                InlineKeyboardButton(text="Orqaga", callback_data="product_back"),
                InlineKeyboardButton(text="Savatcha", callback_data=f"basket_view_{bucket_id['id']}"),
            ])

            if products:
                category_photo = products[0]["category_photo"]
                category_name = products[0]["category_name"]

                await context.bot.delete_message(chat_id=user.id, message_id=message_id)
                await update.callback_query.message.reply_photo(photo=open(f"{category_photo}", "rb"),
                                                                caption=category_name,
                                                                reply_markup=InlineKeyboardMarkup(product_button))
    elif data[0] == "basket":
        if data[1] == "view":
            bucket_id = db.get_bucket(user_data["id"])
            items = db.get_item(int(data[2]))
            await context.bot.delete_message(chat_id=user.id, message_id=message_id)
            items_btn = []

            items_btn.append(
                [
                    InlineKeyboardButton(text="Orqaga", callback_data="products_back"),
                    InlineKeyboardButton(text="Buyurtma berish",
                                         callback_data=f"order_{user.id}_{bucket_id['id']}")
                ]
            )
            items_btn.append(
                [
                    InlineKeyboardButton(text=f"Savatni bo'shatish",
                                         callback_data=f"basket_clear_{bucket_id['id']}")
                ]
            )
            msg = f"Savatchada:\n\n"
            price_delivery = 10000
            price_total = 10000
            for item in items:
                temp_btn = [
                    InlineKeyboardButton(text="➖",
                                         callback_data=f'basket_item_desc_{item["id"]}_{item["count"]}_{bucket_id["id"]}'),
                    InlineKeyboardButton(text=f"{item['product_name']}",
                                         callback_data=f"basket_product_{item['product_id']}"),
                    InlineKeyboardButton(text="➕",
                                         callback_data=f'basket_item_asc_{item["id"]}_{item["count"]}_{bucket_id["id"]}')
                ]
                items_btn.append(temp_btn)
                msg += f"\t\t{item['count']}x {item['product_name']}\n"
                price_total += item['price'] * item["count"]
            msg += "\n"
            msg += f"Mahsulotlar: {price_total - price_delivery} so'm\nYetkazib berish: {price_delivery} so'm\nJami: {price_total}so'm"
            await update.callback_query.message.reply_text(text=msg,
                                                           reply_markup=InlineKeyboardMarkup(items_btn))
            print("await")
        elif data[1] == "clear":
            print("elif")

            await context.bot.delete_message(chat_id=user.id, message_id=message_id)
            db.clear_bucket(int(data[2]))
            db.add_log(user_id=user_data['id'], log=100)
            categories = db.get_category()
            category_buttons = []
            temp_button = []
            print("ishlamayapti")
            for category in categories:
                temp_button.append(
                    InlineKeyboardButton(text=category["name"], callback_data=f'category_{category["id"]}'))
                if len(temp_button) == 2:
                    category_buttons.append(temp_button)
                    temp_button = []
            if temp_button:
                category_buttons.append(temp_button)

            bucket_id = db.get_bucket(user_data['id'])
            items = db.get_item(bucket_id['id'])
            if not items:
                category_buttons.append(
                    [InlineKeyboardButton(text="Orqaga", callback_data="category_back")])
                await update.callback_query.message.reply_photo(photo=open("images/main_menu.jpg", 'rb'),
                                                                caption="Kategoriyalarni tanlang",
                                                                reply_markup=InlineKeyboardMarkup(category_buttons))
            else:
                category_buttons.append(
                    [InlineKeyboardButton(text=f"Savatcha",
                                          callback_data=f"basket_user_{bucket_id}")])
                category_buttons.append(
                    [InlineKeyboardButton(text=f"Orqaga", callback_data="category_back")])
                msg = f"Savatchada:\n\n"
                price_delivery = 10000
                price_total = 10000
                for item in items:
                    msg += f"\t\t{item['count']}x {item['product_name']}\n"
                    price_total += item['price'] * item["count"]
                msg += "\n"
                msg += f"Mahsulotlar: {price_total - price_delivery} so'm\nYetkazib berish {price_delivery} so'm\nJami: {price_total}so'm"
                await update.message.reply_text(text=msg,
                                                reply_markup=InlineKeyboardMarkup(category_buttons))
        elif data[1] == "item":
            item_id = int(data[3])
            count = int(data[4])
            if data[2] == "asc":
                db.update_item(item_id, count + 1)
            else:
                if count == 1:
                    db.clear_item(item_id)
                else:
                    db.update_item(item_id, count - 1)
            bucket_id = int(data[5])
            items = db.get_item(bucket_id)
            items_btn = []
            items_btn.append(
                [
                    InlineKeyboardButton(text="Orqaga", callback_data="products_back"),
                    InlineKeyboardButton(text="buyurtma berish", callback_data=f"order_{user.id}_{bucket_id}")
                ]
            )
            items_btn.append(
                [
                    InlineKeyboardButton(text="Savatni bo'shatish", callback_data=f"basket_clear_{bucket_id}")
                ]
            )
            print("ms")
            msg = "Savatchada: \n\n"
            price_delivery = 10000
            price_total = 10000
            for item in items:
                temp_btn = [
                    InlineKeyboardButton(text="➖",
                                         callback_data=f"basket_item_desc_{item['id']}_{item['count']}_{bucket_id}"),
                    InlineKeyboardButton(text=f"{item['product_name']}",
                                         callback_data=f"basket_product_{item['product_id']}"),
                    InlineKeyboardButton(text="➕",
                                         callback_data=f"basket_item_asc_{item['id']}_{item['count']}_{bucket_id}")
                ]
                items_btn.append(temp_btn)
                msg += f"\t\t{item['count']}x {item['product_name']}\n"
                price_total += item['price'] * item["count"]
            msg += "\n"
            msg += f"Mahsulotlar: {price_total - price_delivery} so'm\nYetkazib berish: {price_delivery} so'm\nJami: {price_total}so'm"
            print("ms1")
            await context.bot.edit_message_text(chat_id=user.id, message_id=message_id,

                                                text=msg,
                                                reply_markup=InlineKeyboardMarkup(items_btn))
            print("ms2")
    elif data[0] == "order":

        await context.bot.delete_message(chat_id=user.id, message_id=message_id)

        bucket_id = int(data[2])
        items = db.get_item(bucket_id)
        price = 0
        for item in items:
            price += item["price"] * item["count"]
        today = str(datetime.now())
        order_id = db.add_order(user.id, price, today)
        for item in items:
            db.add_order_item(order_id["user_id"], item["product_id"], item["count"])

        button = [
            [KeyboardButton('Joylashuv', request_location=True)]
        ]
        await update.callback_query.message.reply_text("Joylashuvni yuboring",
                                                       reply_markup=ReplyKeyboardMarkup(button, resize_keyboard=True))



    elif data[0] == "cancel":
        await context.bot.delete_message(chat_id=user.id, message_id=message_id)



    elif data[0] == "main":
        buttons = [
            [
                KeyboardButton("Menu")
            ],
            [
                KeyboardButton("Buyurtmalar tarixi"),
                KeyboardButton("Manzillarimiz")
            ],
            [
                KeyboardButton("Sozlamalar"),
                KeyboardButton("Biz haqimizda")
            ]

        ]
        db.add_log(user_id=user_data["id"], log=4)
        await context.bot.delete_message(chat_id=user.id, message_id=message_id)
        await update.callback_query.message.reply_text("Assalomu alaykum",
                                                       reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True,
                                                                                        one_time_keyboard=True))


async def message_handler(update, context):
    user = update.message.from_user
    msg = update.message.text
    user_data = db.get_user(user.id)
    lang = user_data["lang"]
    stage = db.get_log(user_data["id"])["log"]
    print(stage, msg)
    if int(stage) == 2:
        db.add_user(chat_id=user.id, fullname=msg)
        db.add_log(user_data["id"], log="3")
        button = [
            [KeyboardButton(TEXT["BTN_CONTACT"][lang], request_contact=True)]
        ]
        await update.message.reply_text(TEXT["TEXT_CONTACT"][lang],
                                        reply_markup=ReplyKeyboardMarkup(button, resize_keyboard=True))
    elif int(stage) == 3:
        isTrue = False
        for i in msg[4:]:
            if ord(i) not in range(48, 50):
                isTrue = True
                break
        if len(msg) != 13 or msg[:4] != "+998" or isTrue:
            await update.message.reply_text("Telefon raqam xato kiritilgan")
        else:
            db.add_user(chat_id=user.id, phone_number=msg)
            message = 'muvaffaqiyatli'
            await main_menu(update, context, user.id, message)

    elif int(stage) == 4:
        if msg == "Menu":
            db.add_log(user_id=user_data["id"], log="100")
            categories = db.get_category()
            category_button = []
            temp_button = []

            for category in categories:

                temp_button.append(InlineKeyboardButton(text=f"{category['name']}",
                                                        callback_data=f"category_{category['id']}"))
                if len(temp_button) == 2:
                    category_button.append(temp_button)

                    temp_button = []

            if len(temp_button) == 1:
                category_button.append(temp_button)

            category_button.append([InlineKeyboardButton(text="Asosiy menyu",
                                                         callback_data="main_menu")])
            await update.message.reply_text("Kategoriyalardan birini tanlang. (https://telegra.ph/Taomnoma-09-30)",
                                            reply_markup=InlineKeyboardMarkup(category_button))
        elif msg == 'Sozlamalar':
            await update.message.reply_text("Sozlamalar")
        elif msg == "Biz haqimizda":
            await update.message.reply_text("Biz haqimizda")
        elif msg == "Buyurtma berish":
            db.add_log(chat_id=user.id, log=100)
            categories = db.get_category()
            category_button = []
            temp_button = []
            for category in categories:
                temp_button.append(
                    InlineKeyboardButton(text=category["name"], callback_data=f"category_{category['id']}")
                )
                if len(temp_button) == 2:
                    category_button.append(temp_button)
                    temp_button = []
            if temp_button:
                category_button.append(temp_button)
            bucket_id = db.get_bucket(user_data['id'])
            items = db.get_item(bucket_id)
            if not items:
                category_button.append(
                    [InlineKeyboardButton(text="Orqaga", callback_data="category_back")]
                )
                await update.callback_query.message.reply_photo(photo=open("images/main_menu.jpg", 'rb'),
                                                                caption="Kategoriyalarni tanlang",
                                                                reply_markup=InlineKeyboardMarkup(category_button))
            # else:
            #     category_button.append(
            #         [InlineKeyboardButton(text=)]
            #     )

async def contact_handler(update, context):
    user = update.message.from_user

    user_data = db.get_user(user.id)
    lang = user_data["lang"]
    stage = db.get_log(user_data["id"])["log"]
    nmb = update.message.contact.phone_number
    db.add_user(chat_id=user.id, phone_number=nmb)
    db.add_log(user_data["id"], log="4")
    buttons = [
        [
            KeyboardButton("Menu")
        ],
        [
            KeyboardButton("Buyurtmalar tarixi"),
            KeyboardButton("Manzillarimiz")
        ],
        [
            KeyboardButton("Sozlamalar"),
            KeyboardButton("Biz haqimizda")
        ]

    ]

    await update.message.reply_text("Assalomu alaykum",
                                    reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True,
                                                                     one_time_keyboard=True))


async def location_handler(update, context):
    print(update)
    # loc = update.callback_query.data.sender.location
    # lat = loc.latitude
    # lng = loc.longitude
    user = update.message.from_user

    # print(lat, lng)
    user_data = db.get_user(user.id)
    stage = db.get_log(user_data["id"])["log"]
    nmd = update.message.location
    msg = "Buyurtmangiz qabul qilindi"
    # db.clear_bucket(user.id['bucket_id'])
    await main_menu(update, context, user.id, msg)


app = ApplicationBuilder().token("6740760413:AAE8wyGtR2CpRq_Lex6ZH_qI5GlVl2mF678").build()

app.add_handler(CommandHandler(command="start", callback=start))
app.add_handler(CallbackQueryHandler(callback_handler))
app.add_handler(MessageHandler(filters.TEXT, message_handler))
app.add_handler(MessageHandler(filters.CONTACT, contact_handler))
app.add_handler(MessageHandler(filters.LOCATION, location_handler))
app.run_polling()
