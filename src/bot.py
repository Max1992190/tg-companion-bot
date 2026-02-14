import asyncio
import logging
import random
import time

from aiogram import Bot, Dispatcher, F, Router
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton,
    ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove,
    LabeledPrice, PreCheckoutQuery, FSInputFile,
)
from aiogram.filters import Command, CommandStart
from aiogram.enums import ParseMode

from src.config import (
    BOT_TOKEN, ADMIN_ID, ADMIN_IDS, FREE_COMPANIONS_LIMIT, FREE_AI_REPLIES_PER_COMPANION,
    PAYMENT_STARS_PRICE, PAID_ACCESS_DURATION, BONUS_DURATION, BONUS_WINDOW,
    PHOTO_COOLDOWN_MIN, PHOTO_COOLDOWN_MAX, PHOTO_TRIGGER_WORDS,
)
from src.storage import get_user, save_user, get_companion_data
from src.companions import get_companion_by_id, get_companions_list
from src.dialog_log import log_dialog, get_last_dialogs
from src.ai_engine import (
    is_short_message, get_short_reply, update_mood, pick_emoji,
    generate_ai_response,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
router = Router()
dp.include_router(router)


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


def has_active_access(user: dict, companion_id: str, user_id: int = 0) -> bool:
    if is_admin(user_id):
        return True
    cd = get_companion_data(user, companion_id)
    return time.time() < cd.get("paid_until", 0)


def check_bonus(user: dict, companion_id: str) -> bool:
    last_paid_ended = user.get("last_paid_ended_at", 0)
    if (
        last_paid_ended > 0
        and not user.get("bonus_given", False)
        and time.time() - last_paid_ended <= BONUS_WINDOW
    ):
        user["bonus_given"] = True
        cd = get_companion_data(user, companion_id)
        cd["paid_until"] = time.time() + BONUS_DURATION
        return True
    return False


def check_paid_expiry(user: dict, companion_id: str):
    cd = get_companion_data(user, companion_id)
    paid_until = cd.get("paid_until", 0)
    if paid_until > 0 and time.time() >= paid_until:
        user["last_paid_ended_at"] = paid_until
        cd["paid_until"] = 0


def get_menu_keyboard() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="☰ Menu")],
        ],
        resize_keyboard=True,
    )


def get_full_menu_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="💬 Back to chat", callback_data="back_to_chat")],
            [InlineKeyboardButton(text="🔁 Change companion", callback_data="change_companion")],
            [InlineKeyboardButton(text="🧲 Recruiting models", callback_data="new_models")],
            [InlineKeyboardButton(text="🆘 Support", callback_data="support")],
            [InlineKeyboardButton(text="ℹ️ About", callback_data="about")],
            [InlineKeyboardButton(text="📄 Terms of Service", callback_data="terms")],
        ]
    )


async def send_companion_cards(chat_id: int):
    companions = get_companions_list()
    for c in companions:
        caption = f"*{c['name']}*, {c['age']}\n\n{c['description']}"
        select_kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text=f"💬 Chat with {c['name']}", callback_data=f"select_{c['id']}")]
        ])
        profile_photo = c.get("profile_photo")
        if profile_photo:
            photo = FSInputFile(profile_photo)
            await bot.send_photo(
                chat_id=chat_id,
                photo=photo,
                caption=caption,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=select_kb,
                protect_content=True,
            )
        else:
            await bot.send_message(
                chat_id=chat_id,
                text=caption,
                parse_mode=ParseMode.MARKDOWN,
                reply_markup=select_kb,
            )


def get_payment_keyboard(companion_id: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(
                text=f"⭐ Open access — {PAYMENT_STARS_PRICE} Stars",
                callback_data=f"pay_{companion_id}"
            )],
        ]
    )


@router.message(CommandStart())
async def cmd_start(message: Message):
    user_id = message.from_user.id
    user = get_user(user_id)

    if user.get("blocked"):
        return

    if is_admin(user_id):
        user["age_confirmed"] = True
        user["state"] = "active" if user.get("name") else "awaiting_name"
        save_user(user_id, user)
        if user.get("name"):
            await message.answer("Welcome back, admin.", reply_markup=get_menu_keyboard())
            return

    if not user.get("age_confirmed"):
        user["state"] = "awaiting_age"
        save_user(user_id, user)

        age_text = (
            "International studio of beautiful models\n"
            "who enjoy private conversations with you.\n\n"
            "🔞 Adults only (18+)\n\n"
            "By continuing, you confirm that:\n"
            "• You are 18 years old or older\n"
            "• This is a virtual conversation\n"
            "• You agree to the Terms\n\n"
            "Do you confirm?"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ I am 18+", callback_data="age_confirm")],
            [InlineKeyboardButton(text="❌ Leave", callback_data="age_deny")],
        ])
        await message.answer(age_text, reply_markup=kb)
        return

    if not user.get("name"):
        user["state"] = "awaiting_name"
        save_user(user_id, user)
        await message.answer("What's your name?", reply_markup=ReplyKeyboardRemove())
        return

    user["state"] = "active"
    save_user(user_id, user)
    await message.answer(
        f"Welcome back, {user['name']}! Choose a companion to chat with:",
        reply_markup=get_menu_keyboard()
    )
    await send_companion_cards(user_id)


@router.callback_query(F.data == "age_confirm")
async def age_confirmed_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = get_user(user_id)

    if user.get("blocked"):
        await callback.answer()
        return

    user["age_confirmed"] = True
    user["state"] = "awaiting_name"
    save_user(user_id, user)

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("What's your name?", reply_markup=ReplyKeyboardRemove())
    await callback.answer()


@router.callback_query(F.data == "age_deny")
async def age_denied_handler(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = get_user(user_id)

    user["blocked"] = True
    user["state"] = "blocked"
    save_user(user_id, user)

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Access denied.")
    await callback.answer()


@router.callback_query(F.data.startswith("select_"))
async def companion_selected(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = get_user(user_id)

    if not user.get("age_confirmed") or user.get("blocked"):
        await callback.answer()
        return

    if not user.get("name"):
        await callback.answer("Please tell me your name first.")
        return

    companion_id = callback.data.replace("select_", "")
    companion = get_companion_by_id(companion_id)
    if not companion:
        await callback.answer("Companion not found.")
        return

    used = user.get("companions_used", [])
    cd = get_companion_data(user, companion_id)

    if companion_id not in used and not is_admin(user_id):
        current_cid = user.get("current_companion")
        if current_cid and current_cid != companion_id and has_active_access(user, current_cid, user_id):
            active_companion = get_companion_by_id(current_cid)
            active_name = active_companion["name"] if active_companion else "your companion"
            kb = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text=f"💬 Return to {active_name}", callback_data=f"select_{current_cid}")],
                [InlineKeyboardButton(
                    text=f"⭐ Open access — {PAYMENT_STARS_PRICE} Stars",
                    callback_data=f"pay_{companion_id}"
                )],
            ])
            await callback.message.answer(
                f"You already have active access with {active_name} ✨\n\n"
                f"You can return to this conversation,\n"
                f"or open access for a new companion.",
                reply_markup=kb
            )
            await callback.answer()
            return

        if len(used) >= FREE_COMPANIONS_LIMIT and not has_active_access(user, companion_id, user_id):
            if cd.get("free_ai_count", 0) == 0 and cd.get("paid_until", 0) == 0:
                await callback.message.answer(
                    f"You've already chatted with two companions for free.\n"
                    f"Open access to chat with {companion['name']}:",
                    reply_markup=get_payment_keyboard(companion_id)
                )
                await callback.answer()
                return
        if companion_id not in used:
            used.append(companion_id)
            user["companions_used"] = used

    user["current_companion"] = companion_id
    user["state"] = "chatting"
    save_user(user_id, user)

    if check_bonus(user, companion_id):
        save_user(user_id, user)
        await callback.message.answer(
            f"Welcome back! Here's a bonus — 5 extra minutes with {companion['name']} 💕",
            reply_markup=get_menu_keyboard()
        )

    await callback.message.edit_reply_markup(reply_markup=None)
    await bot.send_chat_action(chat_id=user_id, action="typing")
    await asyncio.sleep(2.0)
    await callback.message.answer(
        f"*{companion['name']}*\n\n{companion['greeting']}",
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=get_menu_keyboard()
    )

    welcome_photo = companion.get("welcome_photo")
    if welcome_photo:
        photo = FSInputFile(welcome_photo)
        await bot.send_photo(
            chat_id=user_id,
            photo=photo,
            protect_content=True,
        )

    await callback.answer()


@router.callback_query(F.data.startswith("pay_"))
async def initiate_payment(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = get_user(user_id)

    if not user.get("age_confirmed") or user.get("blocked"):
        await callback.answer()
        return

    companion_id = callback.data.replace("pay_", "")
    companion = get_companion_by_id(companion_id)
    if not companion:
        await callback.answer("Companion not found.")
        return

    await bot.send_invoice(
        chat_id=user_id,
        title=f"10 minutes with {companion['name']}",
        description=f"Open access to chat with {companion['name']} for 10 minutes.",
        payload=f"access_{companion_id}",
        currency="XTR",
        prices=[LabeledPrice(label="Access", amount=PAYMENT_STARS_PRICE)],
    )
    await callback.answer()


@router.pre_checkout_query()
async def pre_checkout_handler(pre_checkout: PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout.id, ok=True)


@router.message(F.successful_payment)
async def successful_payment_handler(message: Message):
    user_id = message.from_user.id
    user = get_user(user_id)
    payload = message.successful_payment.invoice_payload

    if payload.startswith("access_"):
        companion_id = payload.replace("access_", "")
        companion = get_companion_by_id(companion_id)
        cd = get_companion_data(user, companion_id)

        cd["paid_until"] = time.time() + PAID_ACCESS_DURATION
        user["last_paid_ended_at"] = 0
        user["current_companion"] = companion_id
        user["state"] = "chatting"
        save_user(user_id, user)

        name = companion["name"] if companion else "your companion"
        await message.answer(
            f"Access opened! You have 10 minutes with {name}. Enjoy your time together 💕",
            reply_markup=get_menu_keyboard()
        )


@router.callback_query(F.data == "back_to_chat")
async def back_to_chat(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = get_user(user_id)

    if not user.get("age_confirmed") or user.get("blocked"):
        await callback.answer()
        return

    companion_id = user.get("current_companion")
    if not companion_id:
        await callback.message.answer("Choose a companion first:")
        await send_companion_cards(user_id)
    else:
        companion = get_companion_by_id(companion_id)
        name = companion["name"] if companion else "your companion"
        await callback.message.answer(f"You're chatting with {name}. Go ahead...", reply_markup=get_menu_keyboard())

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.answer()


@router.callback_query(F.data == "change_companion")
async def change_companion(callback: CallbackQuery):
    user_id = callback.from_user.id
    user = get_user(user_id)

    if not user.get("age_confirmed") or user.get("blocked"):
        await callback.answer()
        return

    await callback.message.edit_reply_markup(reply_markup=None)
    await callback.message.answer("Choose a companion:")
    await send_companion_cards(user_id)
    await callback.answer()


@router.callback_query(F.data == "new_models")
async def new_models(callback: CallbackQuery):
    await callback.message.answer(
        "We are looking for people to join our team\n"
        "with a pleasant, well-groomed appearance\n"
        "and a lively, warm personality.\n\n"
        "It is important to be able to maintain a conversation,\n"
        "be an attentive listener,\n"
        "and show genuine interest in people.\n\n"
        "Having a background in psychology\n"
        "or experience in emotional support\n"
        "will be a strong advantage —\n"
        "because we do more than just talk.\n\n"
        "We help people cope with difficult situations,\n"
        "emotional struggles,\n"
        "and moments of low mood.\n\n"
        "If you are empathetic, able to listen,\n"
        "support others,\n"
        "and want to make someone's days a little easier and warmer —\n"
        "we would be happy to hear from you 🤍\n\n"
        "Contact:\nanketa.loveis2030@gmail.com\n\n"
        "Please send a short introduction about yourself."
    )
    await callback.answer()


@router.callback_query(F.data == "support")
async def support_handler(callback: CallbackQuery):
    await callback.message.answer(
        "If any service is not working,\n"
        "or your payment was successful but access did not appear,\n"
        "or you have any other questions —\n\n"
        "please contact our support team:\n\n"
        "@loveis2030_support"
    )
    await callback.answer()


@router.callback_query(F.data == "about")
async def about_handler(callback: CallbackQuery):
    await callback.message.answer(
        "We are an international studio of models,\n"
        "conversation partners, psychologists,\n"
        "and creative, talented people.\n\n"
        "Our space ranges from light flirting\n"
        "and easy conversations\n"
        "to sincere emotional support in difficult moments.\n\n"
        "We offer emotional connection,\n"
        "care, and positive feelings.\n\n"
        "You are always welcome here —\n"
        "and we do our best for you 🤍\n\n"
        "Payment unlocks extended features\n"
        "of the conversation service\n"
        "for a limited period of time.\n\n"
        "Payment is not a subscription.\n"
        "This is a text-based conversation service.\n\n"
        "You communicate with your chosen companion\n"
        "in a private chat format.\n"
        "The service is designed for calm,\n"
        "comfortable, and relaxed dialogue.\n\n"
        "Some features are available for free.\n"
        "Full access opens for a limited time after payment.\n\n"
        "Payments are made via Telegram Stars.\n"
        "The purchase is not a subscription —\n"
        "access is provided once\n"
        "for the selected period.\n\n"
        "This service is not a psychological assistance service\n"
        "and does not replace real-life communication.\n\n"
        "If you have questions or requests,\n"
        "you can contact support\n"
        "through the corresponding menu section."
    )
    await callback.answer()


@router.callback_query(F.data == "terms")
async def terms_handler(callback: CallbackQuery):
    await callback.message.answer(
        "================= TERMS OF SERVICE =================\n\n"
        "1. General Provisions\n"
        "1.1. This document constitutes an official public offer\n"
        "for providing virtual text-based communication services.\n"
        "1.2. By using the service and/or purchasing access,\n"
        "the user agrees to the terms of this offer.\n\n"
        "2. Service Description\n"
        "2.1. The provider grants the user temporary access\n"
        "to a virtual text conversation with a selected character.\n"
        "2.2. Communication is carried out automatically\n"
        "using software algorithms.\n"
        "2.3. All characters are virtual\n"
        "and do not represent real individuals.\n\n"
        "3. Price and Payment Procedure\n"
        "3.1. The cost of the service is 75 (seventy-five) Telegram Stars.\n"
        "3.2. Payment is made through the built-in Telegram Stars system.\n"
        "3.3. The payment is not a subscription.\n"
        "Access is provided on a one-time basis.\n"
        "3.4. Access duration is 10 minutes\n"
        "from the moment payment is confirmed.\n\n"
        "4. Service Delivery\n"
        "4.1. Access is activated automatically\n"
        "after Telegram confirms successful payment.\n"
        "4.2. Access is provided only\n"
        "for the selected companion.\n"
        "4.3. Selecting a different companion\n"
        "may require a new payment.\n\n"
        "5. Bonuses\n"
        "5.1. In certain cases,\n"
        "additional access time may be granted as a bonus.\n"
        "5.2. A bonus may be granted only once\n"
        "and is not a mandatory part of the service.\n\n"
        "6. Refund Policy\n"
        "6.1. Once the service has started\n"
        "(access has been granted),\n"
        "refunds are not provided.\n"
        "6.2. Refunds are possible only\n"
        "in cases covered by Telegram Stars rules.\n\n"
        "7. Limitation of Liability\n"
        "7.1. The service is provided \"as is\".\n"
        "7.2. The provider is not responsible\n"
        "for user expectations,\n"
        "subjective evaluation of the conversation,\n"
        "or technical issues on Telegram's platform.\n\n"
        "8. Contact Information\n"
        "8.1. For support inquiries,\n"
        "please use the corresponding section\n"
        "in the bot menu.\n\n"
        "===================================================="
    )
    await callback.answer()


@router.message(Command("grant"))
async def grant_access(message: Message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return

    parts = message.text.split()
    if len(parts) != 3:
        await message.answer("Usage: /grant <user_id> <seconds>")
        return

    try:
        target_id = int(parts[1])
        seconds = int(parts[2])
    except ValueError:
        await message.answer("Invalid user_id or seconds.")
        return

    target_user = get_user(target_id)
    companion_id = target_user.get("current_companion")
    if not companion_id:
        await message.answer("User has no active companion.")
        return

    cd = get_companion_data(target_user, companion_id)
    current_until = cd.get("paid_until", 0)
    if current_until < time.time():
        cd["paid_until"] = time.time() + seconds
    else:
        cd["paid_until"] = current_until + seconds
    save_user(target_id, target_user)

    await message.answer(f"Granted {seconds}s access to user {target_id}.")

    try:
        await bot.send_message(
            chat_id=target_id,
            text="✨ Access has been granted manually.\n\n"
                 "You can continue the conversation now.\n"
                 "Enjoy your time here."
        )
    except Exception:
        pass


@router.message(Command("logs"))
async def view_logs(message: Message):
    user_id = message.from_user.id
    if not is_admin(user_id):
        return

    dialogs = get_last_dialogs(10)
    if not dialogs:
        await message.answer("No dialogs logged yet.")
    else:
        await message.answer(dialogs)


@router.message(F.text == "☰ Menu")
async def menu_handler(message: Message):
    user_id = message.from_user.id
    user = get_user(user_id)

    if not user.get("age_confirmed") or user.get("blocked"):
        return

    await message.answer("Menu:", reply_markup=get_full_menu_keyboard())


@router.message()
async def chat_handler(message: Message):
    user_id = message.from_user.id
    user = get_user(user_id)

    if user.get("blocked"):
        return

    if not user.get("age_confirmed"):
        age_text = (
            "International studio of beautiful models\n"
            "who enjoy private conversations with you.\n\n"
            "🔞 Adults only (18+)\n\n"
            "By continuing, you confirm that:\n"
            "• You are 18 years old or older\n"
            "• This is a virtual conversation\n"
            "• You agree to the Terms\n\n"
            "Do you confirm?"
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ I am 18+", callback_data="age_confirm")],
            [InlineKeyboardButton(text="❌ Leave", callback_data="age_deny")],
        ])
        await message.answer(age_text, reply_markup=kb)
        return

    if not message.text:
        return

    if user.get("state") == "awaiting_name":
        name = message.text.strip()[:50]
        user["name"] = name
        user["state"] = "active"
        save_user(user_id, user)
        await message.answer(
            f"Nice to meet you, {name}! Now choose a companion:",
            reply_markup=get_menu_keyboard()
        )
        await send_companion_cards(user_id)
        return

    if not user.get("name"):
        user["state"] = "awaiting_name"
        save_user(user_id, user)
        await message.answer("What's your name?")
        return

    companion_id = user.get("current_companion")
    if not companion_id:
        await message.answer("Choose a companion first:")
        await send_companion_cards(user_id)
        return

    companion = get_companion_by_id(companion_id)
    if not companion:
        await message.answer("Something went wrong. Choose a companion:")
        await send_companion_cards(user_id)
        return

    cd = get_companion_data(user, companion_id)
    user_text = message.text.strip()

    check_paid_expiry(user, companion_id)

    if check_bonus(user, companion_id):
        save_user(user_id, user)
        await message.answer(
            f"Welcome back! Here's a bonus — 5 extra minutes with {companion['name']} 💕",
            reply_markup=get_menu_keyboard()
        )

    is_photo_request = any(trigger in user_text.lower() for trigger in PHOTO_TRIGGER_WORDS)
    if is_photo_request:
        await handle_photo_request(message, user, user_id, companion, cd)
        return

    admin = is_admin(user_id)

    if not admin:
        if cd.get("free_ai_count", 0) >= FREE_AI_REPLIES_PER_COMPANION and not has_active_access(user, companion_id, user_id):
            if not cd.get("paywall_shown"):
                cd["paywall_shown"] = True
                save_user(user_id, user)
                paywall_text = (
                    "Access is limited ✨\n\n"
                    "You can chat for free with two companions.\n"
                    "To continue this conversation,\n"
                    "open access for 10 minutes."
                )
                await message.answer(paywall_text, reply_markup=get_payment_keyboard(companion_id))
            else:
                await message.answer(
                    f"Open access to continue chatting with {companion['name']}:",
                    reply_markup=get_payment_keyboard(companion_id)
                )
            return

    if has_active_access(user, companion_id, user_id) and not admin:
        remaining = int(cd.get("paid_until", 0) - time.time())
        if remaining <= 60 and remaining > 0:
            await message.answer(f"⏰ Less than a minute remaining...")

    mood = update_mood(user)

    if is_short_message(user_text):
        reply = get_short_reply()
        emoji = pick_emoji(user, mood)
        cd.setdefault("chat_history", []).append({"role": "user", "content": user_text})
        cd["chat_history"].append({"role": "assistant", "content": reply})
        if len(cd["chat_history"]) > 20:
            cd["chat_history"] = cd["chat_history"][-20:]
        save_user(user_id, user)
        await bot.send_chat_action(chat_id=user_id, action="typing")
        await asyncio.sleep(random.uniform(5.0, 7.0))
        await message.answer(f"{reply} {emoji}")
        log_dialog(user_text, reply)
        return

    await bot.send_chat_action(chat_id=user_id, action="typing")

    chat_history = cd.get("chat_history", [])
    free_ai_count = cd.get("free_ai_count", 0)

    ai_task = asyncio.create_task(asyncio.to_thread(
        generate_ai_response,
        companion_name=companion["name"],
        companion_description=companion["description"],
        user_name=user["name"],
        user_message=user_text,
        free_ai_count=free_ai_count,
        chat_history=chat_history,
        mood=mood,
    ))
    await asyncio.sleep(random.uniform(5.0, 7.0))
    ai_reply = await ai_task

    emoji = pick_emoji(user, mood)
    final_reply = f"{ai_reply} {emoji}"

    cd.setdefault("chat_history", []).append({"role": "user", "content": user_text})
    cd["chat_history"].append({"role": "assistant", "content": ai_reply})
    if len(cd["chat_history"]) > 20:
        cd["chat_history"] = cd["chat_history"][-20:]

    if not admin and not has_active_access(user, companion_id, user_id):
        cd["free_ai_count"] = free_ai_count + 1

    save_user(user_id, user)
    await message.answer(final_reply)
    log_dialog(user_text, ai_reply)


async def handle_photo_request(message: Message, user: dict, user_id: int, companion: dict, cd: dict):
    companion_id = companion["id"]

    if not has_active_access(user, companion_id, user_id) and not is_admin(user_id):
        await message.answer(
            "Photos are available with active access. Open access to see more:",
            reply_markup=get_payment_keyboard(companion_id)
        )
        return

    photos = companion.get("photos", [])
    if not photos:
        await message.answer(f"{companion['name']}: I don't have any photos ready yet... but I will soon 💕")
        return

    sent = cd.get("photos_sent", [])
    available = [p for p in photos if p not in sent]

    if not available:
        await message.answer(f"You've already seen all of {companion['name']}'s photos 💕")
        return

    now = time.time()
    last_photo_time = cd.get("last_photo_time", 0)

    if sent and (now - last_photo_time < random.randint(PHOTO_COOLDOWN_MIN, PHOTO_COOLDOWN_MAX)):
        remaining = int(PHOTO_COOLDOWN_MIN - (now - last_photo_time))
        if remaining > 0:
            await message.answer(f"Give me a moment... I'll send another one soon 😉")
            return

    photo_id = available[0]
    cd["photos_sent"] = sent + [photo_id]
    cd["last_photo_time"] = now
    save_user(user_id, user)

    try:
        await bot.send_photo(
            chat_id=user_id,
            photo=photo_id,
            caption=f"Just for you... 💕",
            protect_content=True,
        )
    except Exception as e:
        logger.error(f"Failed to send photo: {e}")
        await message.answer(f"Hmm, I couldn't send the photo right now. Try again in a bit...")


async def main():
    logger.info("Bot starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
