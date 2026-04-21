"""
UpSoft Demo Bot — Key Consulting Mystery Shopper
Telegram-бот приёма откликов от кандидатов

Ishga tushirish:
    1. pip install aiogram==3.4.1
    2. BotFather orqali bot yarating va token oling
    3. Ushbu fayldagi BOT_TOKEN ga tokenni qo'ying
    4. python demo_bot.py

Xususiyatlari:
    - Ikki tilli interfeys (ru/uz)
    - Anketa to'plash (FIO, tel, region, yosh, tajriba)
    - Validatsiya (yosh, telefon)
    - Vakansiya haqida ma'lumot
    - "Tayyor ishlash" tasdig'i
    - Demo rejimida Bitrix24 ga chiqarish o'rniga konsolga yoziladi
"""

import asyncio
import logging
from aiogram import Bot, Dispatcher, F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import (
    Message,
    CallbackQuery,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardRemove,
    Contact,
)

# ============================================================
# CONFIGURATION — token bu yerga qo'yiladi
# ============================================================
BOT_TOKEN = "8119420447:AAG9Fx3twCVOPOQoVs78ef4VKX4Ii1Bu_gY"

# ============================================================
# TEXTS — ikki tilda
# Real loyihada bu admin-panel orqali tahrirlanadi
# ============================================================
TEXTS = {
    "ru": {
        "welcome": (
            "Здравствуйте! 👋\n\n"
            "Спасибо за интерес к вакансии <b>тайного покупателя</b> в Key Consulting.\n\n"
            "Я помогу вам подать заявку. Это займёт 3–5 минут.\n\n"
            "Для начала — на каком языке вам удобнее общаться?"
        ),
        "ask_name": "Как вас зовут?\n<i>Укажите ФИО полностью</i>",
        "ask_phone": (
            "Отлично, {name}!\n\n"
            "Теперь поделитесь вашим номером телефона — нажмите кнопку ниже 👇"
        ),
        "phone_button": "📱 Поделиться номером",
        "ask_region": "В каком регионе вы проживаете?",
        "ask_city": "Укажите ваш город:",
        "ask_age": "Сколько вам полных лет?\n<i>Введите число</i>",
        "age_error": "⚠️ Пожалуйста, введите возраст числом (от 18 до 65)",
        "ask_experience": "Есть ли у вас опыт работы тайным покупателем?",
        "ask_smartphone": (
            "У вас есть смартфон с:\n"
            "• Telegram\n"
            "• Интернетом\n"
            "• Камерой\n\n"
            "Всё это есть?"
        ),
        "ask_ready_visit": "Готовы ли вы посещать объекты по заданию?",
        "info_1": (
            "<b>Кто такой тайный покупатель?</b>\n\n"
            "Это обычный с виду человек, который приходит в магазин, кафе или сервисный центр "
            "под видом клиента — и затем оценивает качество обслуживания.\n\n"
            "Вы просто пользуетесь услугой как обычный посетитель, "
            "а после заполняете короткий отчёт в нашем боте."
        ),
        "info_2": (
            "<b>Что входит в работу?</b>\n\n"
            "• Посещение объекта по заданию\n"
            "• Общение с персоналом по сценарию\n"
            "• Наблюдение за чистотой, сервисом, скоростью\n"
            "• Заполнение чек-листа в Telegram-боте\n\n"
            "⏱ Одно посещение занимает 20–60 минут."
        ),
        "info_3": (
            "<b>Условия сотрудничества</b>\n\n"
            "• Оформление по договору ГПХ\n"
            "• Оплата после каждого одобренного визита\n"
            "• Свободный график — сами выбираете удобные задания\n"
            "• Возмещение расходов на покупки (по условиям задания)"
        ),
        "ask_final": "Готовы ли вы начать работать тайным покупателем?",
        "ask_question": "Напишите, пожалуйста, ваш вопрос. Мы свяжемся с вами в ближайшее время.",
        "ask_reject_reason": "Подскажите, пожалуйста, причину отказа — это поможет нам сделать условия лучше:",
        "final_ready": (
            "✅ <b>Ваша анкета принята!</b>\n\n"
            "Спасибо за интерес к работе, {name}.\n\n"
            "В течение 1–3 рабочих дней с вами свяжется наш координатор "
            "для следующего шага — оформления.\n\n"
            "Хорошего дня! ☀️"
        ),
        "final_consult": (
            "📩 <b>Ваш вопрос передан координатору.</b>\n\n"
            "Мы свяжемся с вами в рабочее время и ответим на все вопросы.\n\n"
            "Спасибо, {name}!"
        ),
        "final_reject": (
            "Спасибо за вашу честность, {name}.\n\n"
            "Если в будущем ситуация изменится — мы всегда рады новым кандидатам. "
            "Хорошего дня! 🌿"
        ),
        # Buttons
        "btn_yes": "✅ Да",
        "btn_no": "❌ Нет",
        "btn_ready": "✅ Готова / Готов работать",
        "btn_consult": "💬 Хочу уточнить детали",
        "btn_reject": "❌ Не готов / Не готова",
        "btn_next": "Далее →",
        "btn_ru": "🇷🇺 Русский",
        "btn_uz": "🇺🇿 O'zbekcha",
        # Regions
        "regions": [
            "Ташкент", "Самарканд", "Бухара", "Андижан",
            "Фергана", "Наманган", "Карши", "Ургенч",
            "Нукус", "Джизак", "Навои", "Гулистан", "Термез",
        ],
    },
    "uz": {
        "welcome": (
            "Assalomu alaykum! 👋\n\n"
            "Key Consulting kompaniyasining <b>tayyor xaridor</b> vakansiyasiga qiziqish bildirganingiz uchun rahmat.\n\n"
            "Men sizga ariza topshirishda yordam beraman. Bu 3–5 daqiqa vaqtingizni oladi.\n\n"
            "Avval — qaysi tilda muloqot qilish siz uchun qulay?"
        ),
        "ask_name": "Ismingiz nima?\n<i>To'liq FISh yozing</i>",
        "ask_phone": (
            "Ajoyib, {name}!\n\n"
            "Endi telefon raqamingizni ulashing — pastdagi tugmani bosing 👇"
        ),
        "phone_button": "📱 Raqamimni ulashish",
        "ask_region": "Qaysi viloyatda yashaysiz?",
        "ask_city": "Shahringizni yozing:",
        "ask_age": "Yoshingiz nechida?\n<i>Raqam bilan kiriting</i>",
        "age_error": "⚠️ Iltimos, yoshingizni raqam bilan kiriting (18 dan 65 gacha)",
        "ask_experience": "Sizda tayyor xaridor bo'lib ishlash tajribasi bormi?",
        "ask_smartphone": (
            "Sizda quyidagilar bilan smartfon bormi:\n"
            "• Telegram\n"
            "• Internet\n"
            "• Kamera\n\n"
            "Hammasi bormi?"
        ),
        "ask_ready_visit": "Vazifa bo'yicha obyektlarga borishga tayyormisiz?",
        "info_1": (
            "<b>Tayyor xaridor kim?</b>\n\n"
            "Bu oddiy ko'rinishga ega odam bo'lib, do'kon, kafe yoki xizmat markaziga "
            "oddiy mijoz kabi kelib, keyin xizmat sifatini baholaydi.\n\n"
            "Siz oddiy tashrif buyuruvchi sifatida xizmatdan foydalanasiz, "
            "keyin botimizda qisqa hisobot to'ldirasiz."
        ),
        "info_2": (
            "<b>Ishga nimalar kiradi?</b>\n\n"
            "• Vazifa bo'yicha obyektga tashrif buyurish\n"
            "• Xodimlar bilan stsenariy asosida muloqot\n"
            "• Tozalik, xizmat, tezlikni kuzatish\n"
            "• Telegram-botda checklistni to'ldirish\n\n"
            "⏱ Bir tashrif 20–60 daqiqa vaqt oladi."
        ),
        "info_3": (
            "<b>Hamkorlik shartlari</b>\n\n"
            "• GPX shartnomasi bo'yicha rasmiylashtirish\n"
            "• Har bir tasdiqlangan tashrifdan keyin to'lov\n"
            "• Erkin jadval — qulay vazifalarni o'zingiz tanlaysiz\n"
            "• Xaridlar uchun xarajatlarni qoplash (vazifa shartlariga ko'ra)"
        ),
        "ask_final": "Tayyor xaridor sifatida ishlashga tayyormisiz?",
        "ask_question": "Iltimos, savolingizni yozing. Tez orada siz bilan bog'lanamiz.",
        "ask_reject_reason": "Iltimos, rad etish sababini ayting — bu shartlarimizni yaxshilashga yordam beradi:",
        "final_ready": (
            "✅ <b>Arizangiz qabul qilindi!</b>\n\n"
            "Ishga qiziqish bildirganingiz uchun rahmat, {name}.\n\n"
            "1–3 ish kuni ichida koordinatorimiz siz bilan bog'lanadi — "
            "keyingi qadam uchun rasmiylashtirish bo'yicha.\n\n"
            "Kuningiz xayrli o'tsin! ☀️"
        ),
        "final_consult": (
            "📩 <b>Savolingiz koordinatorga yuborildi.</b>\n\n"
            "Ish vaqtida siz bilan bog'lanib, barcha savollarga javob beramiz.\n\n"
            "Rahmat, {name}!"
        ),
        "final_reject": (
            "Halolligingiz uchun rahmat, {name}.\n\n"
            "Kelajakda vaziyat o'zgarsa — yangi kandidatlarni doim qutib olamiz. "
            "Kuningiz xayrli o'tsin! 🌿"
        ),
        "btn_yes": "✅ Ha",
        "btn_no": "❌ Yo'q",
        "btn_ready": "✅ Tayyorman",
        "btn_consult": "💬 Tafsilotlarni aniqlashtirmoqchiman",
        "btn_reject": "❌ Tayyor emasman",
        "btn_next": "Keyingi →",
        "btn_ru": "🇷🇺 Русский",
        "btn_uz": "🇺🇿 O'zbekcha",
        "regions": [
            "Toshkent", "Samarqand", "Buxoro", "Andijon",
            "Farg'ona", "Namangan", "Qarshi", "Urganch",
            "Nukus", "Jizzax", "Navoiy", "Guliston", "Termiz",
        ],
    },
}


# ============================================================
# FSM STATES — anketa bosqichlari
# ============================================================
class Survey(StatesGroup):
    language = State()
    name = State()
    phone = State()
    region = State()
    city = State()
    age = State()
    experience = State()
    smartphone = State()
    ready_visit = State()
    info_block = State()
    final_decision = State()
    question = State()
    reject_reason = State()


# ============================================================
# HELPERS
# ============================================================
def t(lang: str, key: str) -> str:
    """Matnlarni tilga qarab olish"""
    return TEXTS.get(lang, TEXTS["ru"])[key]


def lang_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=TEXTS["ru"]["btn_ru"], callback_data="lang:ru"),
            InlineKeyboardButton(text=TEXTS["uz"]["btn_uz"], callback_data="lang:uz"),
        ]
    ])


def yes_no_keyboard(lang: str, prefix: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text=t(lang, "btn_yes"), callback_data=f"{prefix}:yes"),
            InlineKeyboardButton(text=t(lang, "btn_no"), callback_data=f"{prefix}:no"),
        ]
    ])


def regions_keyboard(lang: str) -> InlineKeyboardMarkup:
    regions = t(lang, "regions")
    buttons = []
    for i in range(0, len(regions), 2):
        row = [
            InlineKeyboardButton(text=regions[i], callback_data=f"region:{regions[i]}")
        ]
        if i + 1 < len(regions):
            row.append(
                InlineKeyboardButton(text=regions[i + 1], callback_data=f"region:{regions[i + 1]}")
            )
        buttons.append(row)
    return InlineKeyboardMarkup(inline_keyboard=buttons)


def phone_keyboard(lang: str) -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=t(lang, "phone_button"), request_contact=True)]],
        resize_keyboard=True,
        one_time_keyboard=True,
    )


def next_keyboard(lang: str, step: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "btn_next"), callback_data=f"next:{step}")]
    ])


def final_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=t(lang, "btn_ready"), callback_data="final:ready")],
        [InlineKeyboardButton(text=t(lang, "btn_consult"), callback_data="final:consult")],
        [InlineKeyboardButton(text=t(lang, "btn_reject"), callback_data="final:reject")],
    ])


# ============================================================
# HANDLERS
# ============================================================
router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(Survey.language)
    await message.answer(
        TEXTS["ru"]["welcome"],
        reply_markup=lang_keyboard(),
        parse_mode="HTML",
    )


@router.callback_query(F.data.startswith("lang:"))
async def choose_language(callback: CallbackQuery, state: FSMContext):
    lang = callback.data.split(":")[1]
    await state.update_data(lang=lang)
    await state.set_state(Survey.name)
    await callback.message.edit_text(t(lang, "ask_name"), parse_mode="HTML")
    await callback.answer()


@router.message(Survey.name)
async def enter_name(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    name = message.text.strip()
    if len(name) < 3:
        await message.answer(t(lang, "ask_name"), parse_mode="HTML")
        return
    await state.update_data(name=name)
    await state.set_state(Survey.phone)
    await message.answer(
        t(lang, "ask_phone").format(name=name.split()[0]),
        reply_markup=phone_keyboard(lang),
        parse_mode="HTML",
    )


@router.message(Survey.phone, F.contact)
async def enter_phone(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    await state.update_data(phone=message.contact.phone_number)
    await state.set_state(Survey.region)
    await message.answer(
        t(lang, "ask_region"),
        reply_markup=ReplyKeyboardRemove(),
    )
    await message.answer(
        t(lang, "ask_region"),
        reply_markup=regions_keyboard(lang),
    )


@router.callback_query(F.data.startswith("region:"), Survey.region)
async def choose_region(callback: CallbackQuery, state: FSMContext):
    region = callback.data.split(":", 1)[1]
    data = await state.get_data()
    lang = data["lang"]
    await state.update_data(region=region)
    await state.set_state(Survey.city)
    await callback.message.edit_text(t(lang, "ask_city"))
    await callback.answer()


@router.message(Survey.city)
async def enter_city(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    await state.update_data(city=message.text.strip())
    await state.set_state(Survey.age)
    await message.answer(t(lang, "ask_age"), parse_mode="HTML")


@router.message(Survey.age)
async def enter_age(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    try:
        age = int(message.text.strip())
        if age < 18 or age > 65:
            raise ValueError
    except ValueError:
        await message.answer(t(lang, "age_error"))
        return
    await state.update_data(age=age)
    await state.set_state(Survey.experience)
    await message.answer(
        t(lang, "ask_experience"),
        reply_markup=yes_no_keyboard(lang, "exp"),
    )


@router.callback_query(F.data.startswith("exp:"), Survey.experience)
async def enter_experience(callback: CallbackQuery, state: FSMContext):
    has_exp = callback.data.split(":")[1] == "yes"
    data = await state.get_data()
    lang = data["lang"]
    await state.update_data(experience=has_exp)
    await state.set_state(Survey.smartphone)
    await callback.message.edit_text(
        t(lang, "ask_smartphone"),
        reply_markup=yes_no_keyboard(lang, "phone"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("phone:"), Survey.smartphone)
async def enter_smartphone(callback: CallbackQuery, state: FSMContext):
    has_phone = callback.data.split(":")[1] == "yes"
    data = await state.get_data()
    lang = data["lang"]
    await state.update_data(smartphone=has_phone)
    await state.set_state(Survey.ready_visit)
    await callback.message.edit_text(
        t(lang, "ask_ready_visit"),
        reply_markup=yes_no_keyboard(lang, "visit"),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("visit:"), Survey.ready_visit)
async def enter_ready_visit(callback: CallbackQuery, state: FSMContext):
    ready = callback.data.split(":")[1] == "yes"
    data = await state.get_data()
    lang = data["lang"]
    await state.update_data(ready_visit=ready)
    await state.set_state(Survey.info_block)
    await callback.message.edit_text(
        t(lang, "info_1"),
        reply_markup=next_keyboard(lang, "info2"),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "next:info2", Survey.info_block)
async def info_block_2(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    await callback.message.edit_text(
        t(lang, "info_2"),
        reply_markup=next_keyboard(lang, "info3"),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "next:info3", Survey.info_block)
async def info_block_3(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    await callback.message.edit_text(
        t(lang, "info_3"),
        reply_markup=next_keyboard(lang, "final"),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "next:final", Survey.info_block)
async def ask_final(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    await state.set_state(Survey.final_decision)
    await callback.message.edit_text(
        t(lang, "ask_final"),
        reply_markup=final_keyboard(lang),
    )
    await callback.answer()


@router.callback_query(F.data == "final:ready", Survey.final_decision)
async def final_ready(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    await save_candidate(callback.from_user.id, callback.from_user.username, data, "ready")
    await callback.message.edit_text(
        t(lang, "final_ready").format(name=data["name"].split()[0]),
        parse_mode="HTML",
    )
    await state.clear()
    await callback.answer()


@router.callback_query(F.data == "final:consult", Survey.final_decision)
async def final_consult(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    await state.set_state(Survey.question)
    await callback.message.edit_text(t(lang, "ask_question"))
    await callback.answer()


@router.message(Survey.question)
async def enter_question(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    data["question"] = message.text
    await save_candidate(message.from_user.id, message.from_user.username, data, "consult")
    await message.answer(
        t(lang, "final_consult").format(name=data["name"].split()[0]),
        parse_mode="HTML",
    )
    await state.clear()


@router.callback_query(F.data == "final:reject", Survey.final_decision)
async def final_reject(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    await state.set_state(Survey.reject_reason)
    await callback.message.edit_text(t(lang, "ask_reject_reason"))
    await callback.answer()


@router.message(Survey.reject_reason)
async def enter_reject_reason(message: Message, state: FSMContext):
    data = await state.get_data()
    lang = data["lang"]
    data["reject_reason"] = message.text
    await save_candidate(message.from_user.id, message.from_user.username, data, "reject")
    await message.answer(
        t(lang, "final_reject").format(name=data["name"].split()[0]),
        parse_mode="HTML",
    )
    await state.clear()


# ============================================================
# BITRIX24 SAVE — demo rejimda konsolga chiqariladi
# Real loyihada bu yerda Bitrix24 REST API chaqiruvi bo'ladi
# ============================================================
async def save_candidate(tg_id: int, username: str, data: dict, status: str):
    """
    Real loyihada:
        - requests.post(BITRIX_WEBHOOK_URL + "/crm.item.add", json=...)
        - smart-process "Kandidaty" ga yozish
        - UTM manbani qayd qilish
    Demo rejimda — konsolga chiqaramiz
    """
    print("\n" + "=" * 60)
    print(f"✉️  YANGI KANDIDAT — status: {status.upper()}")
    print("=" * 60)
    print(f"Telegram ID:  {tg_id}")
    print(f"Username:     @{username}")
    print(f"Til:          {data.get('lang')}")
    print(f"FISh:         {data.get('name')}")
    print(f"Telefon:      {data.get('phone')}")
    print(f"Viloyat:      {data.get('region')}")
    print(f"Shahar:       {data.get('city')}")
    print(f"Yosh:         {data.get('age')}")
    print(f"Tajriba:      {'Ha' if data.get('experience') else 'Yoq'}")
    print(f"Smartfon:     {'Ha' if data.get('smartphone') else 'Yoq'}")
    print(f"Tashriflar:   {'Ha' if data.get('ready_visit') else 'Yoq'}")
    if data.get("question"):
        print(f"Savol:        {data['question']}")
    if data.get("reject_reason"):
        print(f"Rad sababi:  {data['reject_reason']}")
    print("=" * 60 + "\n")


# ============================================================
# MAIN
# ============================================================
async def main():
    logging.basicConfig(level=logging.INFO)

    # if BOT_TOKEN == "8119420447:AAG9Fx3twCVOPOQoVs78ef4VKX4Ii1Bu_gY":
        # print("⚠️  Iltimos, BOT_TOKEN ni sozlang (BotFather'dan oling)")
        # return

    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    dp.include_router(router)

    print("🚀 UpSoft Demo Bot ishga tushdi!")
    print("   Bot bilan Telegram'da gaplashing")
    print("   Yangi kandidatlar shu konsolda ko'rinadi\n")

    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
