from aiogram import Router
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

from app.steps_bot.presentation.keyboards.simple_kb import main_menu_kb
from app.steps_bot.services.user_service import register_user, get_user, sync_username, set_landing_source
from app.steps_bot.services.captions_service import render
from app.steps_bot.services.referral_service import parse_start_param, create_referral
from app.steps_bot.db.repo import get_session

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext, command: CommandObject):
    """Показываем главное меню и регистрируем пользователя без запроса телефона/email."""

    await sync_username(message.from_user.id, message.from_user.username)
    user = await get_user(message.from_user.id)
    
    # Парсим start: ref_123456_source (реферал) или sticker/insights/email (источник)
    inviter_telegram_id, referral_source, landing_source = (
        parse_start_param(command.args) if command.args else (None, None, None)
    )

    is_new_user = user is None

    if is_new_user:
        await register_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            phone=None,
            email=None,
        )
        if inviter_telegram_id:
            async with get_session() as session:
                await create_referral(
                    session=session,
                    user_telegram_id=message.from_user.id,
                    inviter_telegram_id=inviter_telegram_id,
                    referral_source=referral_source,
                )
        elif landing_source:
            await set_landing_source(message.from_user.id, landing_source)
        user = await get_user(message.from_user.id)

    kb = await main_menu_kb()

    await render(
        message,
        "start_welcome" if is_new_user else "main_menu",
        reply_markup=kb,
        name=message.from_user.first_name,
        phone=user.phone if user else "",
        email=user.email if user else "",
    )
    await state.clear()
