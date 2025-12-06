from typing import Optional
from sqlalchemy import select

from app.steps_bot.db.repo import get_session
from app.steps_bot.db.models.user import User


async def register_user(
    telegram_id: int,
    username: Optional[str],
    phone: Optional[str] = None,
    email: Optional[str] = None,
) -> User:
    async with get_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))

        if not user:
            user = User(telegram_id=telegram_id, username=username)
            session.add(user)

        # Обновляем username при регистрации
        if username and user.username != username:
            user.username = username

        # Обновляем контакты, если переданы (перезаписываем старыми или новыми значениями)
        if phone is not None:
            user.phone = phone
        if email is not None:
            user.email = email

        await session.flush()
        return user


async def get_user(telegram_id: int) -> Optional[User]:
    async with get_session() as session:
        return await session.scalar(select(User).where(User.telegram_id == telegram_id))
    

async def sync_username(telegram_id: int, new_username: Optional[str]) -> None:
    """
    Обновить username, если пользователь уже есть в БД и ник изменился.
    """
    if not new_username:
        return

    async with get_session() as session:
        user = await session.scalar(
            select(User).where(User.telegram_id == telegram_id)
        )
        if user and user.username != new_username:
            user.username = new_username
            await session.flush()