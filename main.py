import logging
from datetime import datetime, timedelta
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    InputMediaPhoto
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes
)
from telegram.constants import ParseMode, ChatAction

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = "BOT_TOKENINGIZNI_YERGA_QOYING"
ADMIN_USERNAME = "U_M_1_K_O"
ADMIN_ID = None
CINEMA_CHANNEL_ID = None
CARD_NUMBER = "5614 **** **** 6987"
CARD_HOLDER = "M/A"
PAYMENT_AMOUNT = "10 270"
BOT_USERNAME = None

user_data = {}
pending_payments = {}
active_subscriptions = {}
link_usage = {}

OPEN_MENU_PHOTO = "https://via.placeholder.com/500x300/1a1a2e/FFD700?text=CINEMA+BOT"
BALANCE_PHOTO = "https://via.placeholder.com/500x300/FF8C00/FFFFFF?text=BALANS"
STORE_PHOTO = "https://via.placeholder.com/500x300/1a1a2e/FF6B6B?text=DOKON"
HISTORY_PHOTO = "https://via.placeholder.com/500x300/2d2d44/4ECDC4?text=TARIX"


def get_user_data(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            'balance': 0,
            'username': None,
            'first_name': None,
            'subscription_end': None,
            'purchase_history': [],
            'is_subscribed': False
        }
    return user_data[user_id]


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    data = get_user_data(user_id)
    data['username'] = user.username
    data['first_name'] = user.first_name

    try:
        member = await context.bot.get_chat_member(
            chat_id=CINEMA_CHANNEL_ID,
            user_id=user_id
        )
        if member.status in ['member', 'administrator', 'creator']:
            data['is_subscribed'] = True
        else:
            data['is_subscribed'] = False
    except Exception:
        data['is_subscribed'] = False

    if not data['is_subscribed']:
        keyboard = [
            [InlineKeyboardButton(
                "Kanalga obuna bo'lish",
                url=f"https://t.me/{context.bot.username.replace('@', '')}?start=channel"
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Botdan foydalanish uchun rasmiy kanalimizga obuna bo'ling va "
            "/start ni qayta bosing",
            reply_markup=reply_markup
        )
        return

    await show_open_menu(update, context)


async def show_open_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    data = get_user_data(user_id)

    balance_text = f"{data['balance']:,} so'm".replace(',', ' ')
    username_text = f"@{data['username']}" if data['username'] else data['first_name']

    caption = (
        f"<b>NurliCraft DONATE</b>\n\n"
        f"<b>Sizning balansingiz</b>\n"
        f"<b>{balance_text}</b>\n"
        f"<code>{username_text}</code>"
    )

    keyboard = [
        [InlineKeyboardButton("Do'kon", callback_data="store")],
        [InlineKeyboardButton("Balans", callback_data="balance")],
        [InlineKeyboardButton("Tarix", callback_data="history")]
    ]

    if data.get('subscription_end') and data['subscription_end'] > datetime.now():
        keyboard.insert(0, [InlineKeyboardButton(
            "Kanalga kirish 🔗",
            callback_data="send_link"
        )])

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await update.callback_query.edit_message_media(
            media=InputMediaPhoto(
                media=OPEN_MENU_PHOTO,
                caption=caption,
                parse_mode=ParseMode.HTML
            ),
            reply_markup=reply_markup
        )
    else:
        await update.message.reply_photo(
            photo=OPEN_MENU_PHOTO,
            caption=caption,
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )


async def open_menu_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = get_user_data(user_id)

    balance_text = f"{data['balance']:,} so'm".replace(',', ' ')
    username_text = f"@{data['username']}" if data['username'] else data['first_name']

    caption = (
        f"<b>NurliCraft DONATE</b>\n\n"
        f"<b>Sizning balansingiz</b>\n"
        f"<b>{balance_text}</b>\n"
        f"<code>{username_text}</code>"
    )

    keyboard = [
        [InlineKeyboardButton("Do'kon", callback_data="store")],
        [InlineKeyboardButton("Balans", callback_data="balance")],
        [InlineKeyboardButton("Tarix", callback_data="history")]
    ]

    if data.get('subscription_end') and data['subscription_end'] > datetime.now():
        keyboard.insert(0, [InlineKeyboardButton(
            "Kanalga kirish 🔗",
            callback_data="send_link"
        )])

    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_media(
        media=InputMediaPhoto(
            media=OPEN_MENU_PHOTO,
            caption=caption,
            parse_mode=ParseMode.HTML
        ),
        reply_markup=reply_markup
    )


async def store_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = get_user_data(user_id)

    balance_text = f"{data['balance']:,} so'm".replace(',', ' ')

    caption = (
        f"<b>Joriy balans</b>\n\n"
        f"<b>{balance_text}</b>\n\n"
        f"<b>Hisob raqami:</b> <code>8527010929</code> <code>Nusxa</code>\n\n"
        f"<b>To'lov usuli</b>"
    )

    keyboard = [
        [InlineKeyboardButton(
            "CLICK",
            callback_data="pay_click"
        )],
        [InlineKeyboardButton(
            "MirPay",
            callback_data="pay_mirpay"
        )],
        [InlineKeyboardButton(
            "Paynet orqali",
            callback_data="pay_paynet"
        )],
        [InlineKeyboardButton("Orqaga", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_media(
        media=InputMediaPhoto(
            media=BALANCE_PHOTO,
            caption=caption,
            parse_mode=ParseMode.HTML
        ),
        reply_markup=reply_markup
    )


async def payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE, method: str):
    query = update.callback_query
    await query.answer()

    method_names = {
        'click': 'CLICK',
        'mirpay': 'MirPay',
        'paynet': 'Paynet'
    }

    method_name = method_names.get(method, method.upper())

    caption = (
        f"<b>To'ldirish muvaffaqiyatli</b>\n\n"
        f"<b>Miqdor {PAYMENT_AMOUNT} so'm</b>\n\n"
        f"<b>MUHIM!</b> Quyida ko'rsatilgan summani <b>AYNAN</b> to'lashingiz shart! "
        f"Hatto <b>1 so'm</b> kam yoki ko'p bo'lsa ham to'lov <b>avtomatik qabul qilinmaydi</b>.\n\n"
        f"<b>AYNI SHU SUMMA 29:53</b>\n"
        f"<b>{PAYMENT_AMOUNT}</b> <code>Nusxalash</code>\n\n"
        f"<b>Karta raqami:</b> <code>{CARD_NUMBER}</code> <code>Nusxalash</code>\n"
        f"<b>Karta egasi:</b> <b>{CARD_HOLDER}</b>\n\n"
        f"<b>To'lov usuli:</b> {method_name}"
    )

    keyboard = [
        [InlineKeyboardButton("OK", callback_data="confirm_payment")],
        [InlineKeyboardButton("Orqaga", callback_data="balance")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_media(
        media=InputMediaPhoto(
            media=BALANCE_PHOTO,
            caption=caption,
            parse_mode=ParseMode.HTML
        ),
        reply_markup=reply_markup
    )


async def confirm_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = get_user_data(user_id)

    pending_payments[user_id] = {
        'username': data['username'],
        'first_name': data['first_name'],
        'amount': PAYMENT_AMOUNT,
        'timestamp': datetime.now(),
        'status': 'pending'
    }

    admin_keyboard = [
        [
            InlineKeyboardButton(
                "Tasdiqlash ✅",
                callback_data=f"approve_{user_id}"
            ),
            InlineKeyboardButton(
                "Rad etish ❌",
                callback_data=f"reject_{user_id}"
            )
        ]
    ]
    admin_markup = InlineKeyboardMarkup(admin_keyboard)

    admin_msg = (
        f"<b>💳 To'lov so'rovi</b>\n\n"
        f"<b>Foydalanuvchi:</b> @{data['username'] or data['first_name']}\n"
        f"<b>User ID:</b> <code>{user_id}</code>\n"
        f"<b>Summa:</b> {PAYMENT_AMOUNT} so'm\n"
        f"<b>Vaqt:</b> {datetime.now().strftime('%d.%m.%Y %H:%M')}"
    )

    try:
        await context.bot.send_message(
            chat_id=ADMIN_ID,
            text=admin_msg,
            parse_mode=ParseMode.HTML,
            reply_markup=admin_markup
        )
    except Exception as e:
        logger.error(f"Admin xabar yuborishda xatolik: {e}")

    keyboard = [
        [InlineKeyboardButton("Orqaga", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_media(
        media=InputMediaPhoto(
            media=BALANCE_PHOTO,
            caption=(
                f"<b>To'lovingiz tekshirilmoqda...</b>\n\n"
                f"Admin tasdiqlagandan so'ng balansingizga qo'shiladi.\n"
                f"Iltimos kuting."
            ),
            parse_mode=ParseMode.HTML
        ),
        reply_markup=reply_markup
    )


async def approve_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        await query.answer("Faqat admin tasdiqlashi mumkin!", show_alert=True)
        return

    user_id = int(query.data.split('_')[1])

    if user_id not in pending_payments:
        await query.answer("To'lov topilmadi!", show_alert=True)
        return

    data = get_user_data(user_id)
    data['balance'] += 10000
    data['subscription_end'] = datetime.now() + timedelta(days=30)
    data['purchase_history'].append({
        'date': datetime.now().strftime('%d.%m.%Y %H:%M'),
        'amount': 10000,
        'status': 'Tasdiqlandi'
    })

    del pending_payments[user_id]

    try:
        keyboard = [
            [InlineKeyboardButton(
                "Kanalga kirish 🔗",
                callback_data="send_link"
            )]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"<b>✅ To'lovingiz tasdiqlandi!</b>\n\n"
                f"Balansingizga 10,000 so'm qo'shildi.\n"
                f"Obuna muddati: 30 kun\n\n"
                f"Kanalga kirish uchun quyidagi tugmani bosing:"
            ),
            parse_mode=ParseMode.HTML,
            reply_markup=reply_markup
        )
    except Exception as e:
        logger.error(f"Foydalanuvchiga xabar yuborishda xatolik: {e}")

    await query.edit_message_text(
        text=f"✅ To'lov tasdiqlandi! Foydalanuvchi: @{data['username']}",
        parse_mode=ParseMode.HTML
    )


async def reject_payment_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.from_user.id != ADMIN_ID:
        await query.answer("Faqat admin rad eta oladi!", show_alert=True)
        return

    user_id = int(query.data.split('_')[1])

    if user_id not in pending_payments:
        await query.answer("To'lov topilmadi!", show_alert=True)
        return

    data = get_user_data(user_id)
    data['purchase_history'].append({
        'date': datetime.now().strftime('%d.%m.%Y %H:%M'),
        'amount': 10000,
        'status': 'Rad etildi'
    })

    del pending_payments[user_id]

    try:
        await context.bot.send_message(
            chat_id=user_id,
            text=(
                f"<b>❌ To'lovingiz rad etildi.</b>\n\n"
                f"Iltimos, qaytadan urinib ko'ring."
            ),
            parse_mode=ParseMode.HTML
        )
    except Exception as e:
        logger.error(f"Foydalanuvchiga xabar yuborishda xatolik: {e}")

    await query.edit_message_text(
        text=f"❌ To'lov rad etildi! Foydalanuvchi: @{data['username']}",
        parse_mode=ParseMode.HTML
    )


async def balance_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = get_user_data(user_id)

    balance_text = f"{data['balance']:,} so'm".replace(',', ' ')

    caption = (
        f"<b>Joriy balans</b>\n\n"
        f"<b>{balance_text}</b>\n\n"
        f"<b>Hisob raqami:</b> <code>8527010929</code> <code>Nusxa</code>\n\n"
        f"<b>To'lov usuli</b>"
    )

    keyboard = [
        [InlineKeyboardButton(
            "CLICK",
            callback_data="pay_click"
        )],
        [InlineKeyboardButton(
            "MirPay",
            callback_data="pay_mirpay"
        )],
        [InlineKeyboardButton(
            "Paynet orqali",
            callback_data="pay_paynet"
        )],
        [InlineKeyboardButton("Orqaga", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_media(
        media=InputMediaPhoto(
            media=BALANCE_PHOTO,
            caption=caption,
            parse_mode=ParseMode.HTML
        ),
        reply_markup=reply_markup
    )


async def history_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = get_user_data(user_id)

    if data['purchase_history']:
        history_text = "\n".join([
            f"• {h['date']} - {h['amount']} so'm"
            for h in data['purchase_history'][-5:]
        ])
        caption = (
            f"<b>Sotib olishlar tarixi</b>\n\n"
            f"{history_text}"
        )
    else:
        caption = (
            f"<b>Sotib olishlar tarixi</b>\n\n"
            f"<i>Hali sotib olishlar yo'q</i>"
        )

    keyboard = [
        [InlineKeyboardButton("Orqaga", callback_data="back_to_menu")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    await query.edit_message_media(
        media=InputMediaPhoto(
            media=HISTORY_PHOTO,
            caption=caption,
            parse_mode=ParseMode.HTML
        ),
        reply_markup=reply_markup
    )


async def send_link_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    data = get_user_data(user_id)

    if data['subscription_end'] and data['subscription_end'] > datetime.now():
        remaining = data['subscription_end'] - datetime.now()
        days = remaining.days

        if user_id not in link_usage:
            link_usage[user_id] = {'used': False, 'link': None}

        if not link_usage[user_id]['used']:
            invite_link = await context.bot.create_chat_invite_link(
                chat_id=CINEMA_CHANNEL_ID,
                member_limit=1,
                name=f"User {user_id} - {datetime.now().strftime('%d%m%Y')}"
            )
            link_usage[user_id]['link'] = invite_link.invite_link
            link_usage[user_id]['used'] = True

            keyboard = [
                [InlineKeyboardButton(
                    "Kirish",
                    url=invite_link.invite_link
                )]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)

            await query.edit_message_media(
                media=InputMediaPhoto(
                    media=OPEN_MENU_PHOTO,
                    caption=(
                        f"<b>Sizning kirish linkingiz</b>\n\n"
                        f"<b>Obuna muddati:</b> {days} kun qoldi\n"
                        f"<b>Diqqat:</b> Link faqat 1 marta ishlatiladi!"
                    ),
                    parse_mode=ParseMode.HTML
                ),
                reply_markup=reply_markup
            )
        else:
            await query.answer("Link allaqachon ishlatildi!", show_alert=True)
    else:
        await query.answer(
            "Sizda obuna yo'q yoki muddati tugagan!",
            show_alert=True
        )


async def check_subscription(context: ContextTypes.DEFAULT_TYPE):
    now = datetime.now()
    for user_id, data in list(user_data.items()):
        if data.get('subscription_end') and data['subscription_end'] < now:
            try:
                await context.bot.ban_chat_member(
                    chat_id=CINEMA_CHANNEL_ID,
                    user_id=user_id
                )
                await context.bot.unban_chat_member(
                    chat_id=CINEMA_CHANNEL_ID,
                    user_id=user_id
                )
                data['subscription_end'] = None
                data['is_subscribed'] = False

                await context.bot.send_message(
                    chat_id=user_id,
                    text=(
                        "<b>Obuna muddati tugadi!</b>\n\n"
                        "Kanalga kirish huquqingiz o'chirildi.\n"
                        "Qayta obuna bo'lish uchun /start ni bosing."
                    ),
                    parse_mode=ParseMode.HTML
                )
            except Exception as e:
                logger.error(f"Obuna tekshirishda xatolik: {e}")


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    data = query.data

    if data == "store":
        await store_callback(update, context)
    elif data == "balance":
        await balance_callback(update, context)
    elif data == "history":
        await history_callback(update, context)
    elif data.startswith("pay_"):
        method = data.replace("pay_", "")
        await payment_callback(update, context, method)
    elif data == "confirm_payment":
        await confirm_payment_callback(update, context)
    elif data.startswith("approve_"):
        await approve_payment_callback(update, context)
    elif data.startswith("reject_"):
        await reject_payment_callback(update, context)
    elif data == "back_to_menu":
        await open_menu_callback(update, context)
    elif data == "send_link":
        await send_link_callback(update, context)


async def post_init(application: Application):
    global ADMIN_ID, BOT_USERNAME
    bot = application.bot
    BOT_USERNAME = bot.username
    me = await bot.get_me()
    BOT_USERNAME = me.username
    
    try:
        admins = await bot.get_chat_administrators(chat_id=CINEMA_CHANNEL_ID)
        for admin in admins:
            if admin.user.username and admin.user.username.lower() == ADMIN_USERNAME.lower():
                ADMIN_ID = admin.user.id
                break
    except Exception as e:
        logger.error(f"Admin ID ni olishda xatolik: {e}")


def main():
    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))

    job_queue = application.job_queue
    job_queue.run_repeating(
        check_subscription,
        interval=3600,
        first=10
    )

    print("Bot ishga tushdi!")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == '__main__':
    main()
