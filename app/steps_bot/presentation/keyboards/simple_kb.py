from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, WebAppInfo

from app.steps_bot.services.settings_service import SettingsService
from app.steps_bot.settings import config

# Главное меню
async def main_menu_kb() -> InlineKeyboardMarkup:
    support_url = await SettingsService.get_setting('поддержка')

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text='🚶 Начать прогулку', callback_data='walk')],
            [InlineKeyboardButton(text='👪 Ваша семья', callback_data='family')],
            [InlineKeyboardButton(text='💳 Баланс', callback_data='balance')],
            [InlineKeyboardButton(text='🛍️ Каталог', callback_data='catalog')],
            [InlineKeyboardButton(text='📢 Канал', url='https://t.me/roxy_pets')],
            [InlineKeyboardButton(text='🎁 Реферальная система', callback_data='referral_system')],
            [InlineKeyboardButton(text='❓ FAQ', callback_data='faq')],
            [InlineKeyboardButton(
                text='🛠️ Техническая поддержка',
                url=support_url if support_url else 'https://t.me/bottecp'
            )]
        ]
    )
    return keyboard


# Назад
back_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='↩ Назад', callback_data='back')]
    ]
)

# Реплай меню с телефоном
phone_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text='📱 Поделиться номером телефона', request_contact=True)]
    ],
    resize_keyboard=True,
    one_time_keyboard=True,
    input_field_placeholder='Пожалуйста, поделитесь своим номером телефона'
)

# Меню с выбором вида прогулки
walk_choice = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(
        text='🐶 Гуляю с собакой', 
        callback_data='walk_dog'
    )],
    [InlineKeyboardButton(text='↩ Назад', callback_data='back')]
])


# Завершить прогулку
end_walk_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🏁 Завершить прогулку', callback_data='end_walk')]
])

# Когда пользователь ещё не состоит в семье
no_family_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='👪 Создать семью', callback_data='create_family')],
    [InlineKeyboardButton(text='↩ Назад', callback_data='back')]
])

# Согласие на обработку персональных данных
accept_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='✅ Соглашаюсь', callback_data='accept')],
])


balance_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='🛍️ Потратить баллы', callback_data='catalog')],
    [InlineKeyboardButton(text='🧾 История начислений и трат', callback_data='history')],
    [InlineKeyboardButton(text='↩ Назад', callback_data='back')]
])


walk_back_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text='↩ Назад', callback_data='walk_back')]
    ]
)

family_cancel_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="❌ Отмена", callback_data="family_cancel_create")]
    ]
)
