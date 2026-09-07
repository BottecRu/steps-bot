from __future__ import annotations

from math import ceil
from typing import List

from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from app.steps_bot.db.models.user import User
from app.steps_bot.db.models.faq import FAQ
from app.steps_bot.db.models.catalog import CatalogCategory, Product
from app.steps_bot.db.models.promo import PromoGroup


PER_PAGE = 6


# Меню овнера семьи
def build_owner_kb(members: List[User], me_tg_id: int) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text="➕ Добавить участников",
                              callback_data="family_invite")]
    ]

    for m in members:
        label = f"👁 @{m.username}"
        row = [InlineKeyboardButton(text=label,
                                    callback_data=f"family_info:{m.id}")]
        if m.telegram_id != me_tg_id:
            row.append(InlineKeyboardButton(text="🗑️ Удалить",
                                            callback_data=f"family_kick:{m.id}"))
        rows.append(row)

    rows += [
        [InlineKeyboardButton(text="✏️ Переименовать",
                              callback_data="family_rename")],
        [InlineKeyboardButton(text="🧨 Расформировать",
                              callback_data="disband")],
        [InlineKeyboardButton(text="↩ Назад", callback_data="back")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


# Меню принятия приглашения в семью
def invite_response_kb(inv_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[[

            InlineKeyboardButton(text="✅ Принять",  callback_data=f"family_accept:{inv_id}"),
            InlineKeyboardButton(text="❌ Отклонить", callback_data=f"family_decline:{inv_id}"),

        ]]
    )


# Меню обычного участника
def build_member_kb(members: List[User],
                    me_tg_id: int,
                    owner_id: int) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text="➕ Добавить участников",
                              callback_data="family_invite")]
    ]

    for m in members:
        tag = "👑 " if m.id == owner_id else "👁 "
        label = f"{tag}@{m.username}" + (
            " (вы)" if m.telegram_id == me_tg_id else ""
        )
        row = [InlineKeyboardButton(text=label,
                                    callback_data=f"family_info:{m.id}")]
        if m.id != owner_id:
            row.append(InlineKeyboardButton(text="🗑️ Удалить",
                                            callback_data=f"family_kick:{m.id}"))
        rows.append(row)

    rows += [
        [InlineKeyboardButton(text="✏️ Переименовать",
                              callback_data="family_rename")],
        [InlineKeyboardButton(text="🚪 Выйти из семьи",
                              callback_data="family_leave")],
        [InlineKeyboardButton(text="↩ Назад", callback_data="back")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=rows)


# FAQ меню
def faq_list_kb(faqs: List[FAQ], page: int = 1) -> InlineKeyboardMarkup:
    pages = max(1, ceil(len(faqs) / PER_PAGE))
    page = max(1, min(page, pages))
    start = (page - 1) * PER_PAGE
    chunk = faqs[start:start + PER_PAGE]

    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text=f"❓ {f.question}", callback_data=f"faq_show:{f.slug}")]
        for f in chunk
    ]

    nav: list[InlineKeyboardButton] = []
    if page > 1:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"faq_page:{page-1}"))
    if page < pages:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"faq_page:{page+1}"))
    if nav:
        rows.append(nav)

    rows.append([InlineKeyboardButton(text="↩ Назад", callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# Возврат в FAQ
faq_back_kb = InlineKeyboardMarkup(
    inline_keyboard=[[InlineKeyboardButton(text="↩", callback_data="faq")]]
)


# Категории + промокоды
def catalog_root_kb(categories: List[CatalogCategory]) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text=f"🗂️ {c.name}", callback_data=f"cat:{c.id}:1")] for c in categories
    ]
    rows.append([InlineKeyboardButton(text="🏷️ Промокоды", callback_data="promo_stub")])
    rows.append([InlineKeyboardButton(text="↩ Назад", callback_data="back")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


# Клавиатура товаров
def catalog_page_kb(
    products: List[Product],
    cat_id: int,
    page: int,
    pages: int,
    *,
    back_callback: str = "catalog_root",
) -> InlineKeyboardMarkup:
    rows: list[list[InlineKeyboardButton]] = [
        [InlineKeyboardButton(text=f"🛒 {p.title}", callback_data=f"product:{p.id}:{cat_id}:{page}")]
        for p in products
    ]

    nav: list[InlineKeyboardButton] = []
    if page > 1:
        nav.append(InlineKeyboardButton(text="◀️", callback_data=f"cat:{cat_id}:{page-1}"))
    if page < pages:
        nav.append(InlineKeyboardButton(text="▶️", callback_data=f"cat:{cat_id}:{page+1}"))
    if nav:
        rows.append(nav)

    rows.append([InlineKeyboardButton(text="🏷️ Промокоды", callback_data="promo_stub")])
    rows.append([InlineKeyboardButton(text="↩ Назад", callback_data=back_callback)])
    return InlineKeyboardMarkup(inline_keyboard=rows)



# Карточки товаров
def product_card_kb(product_id: int, cat_id: int, page: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="🛍️ Купить", callback_data=f"buy:{product_id}")],
            [InlineKeyboardButton(text="↩ Назад", callback_data=f"cat:{cat_id}:{page}")],
        ]
    )


def promo_groups_kb(groups: List[PromoGroup]) -> InlineKeyboardMarkup:
    """
    Клавиатура групп промокодов с ценой.
    """
    rows: list[list[InlineKeyboardButton]] = [
        [
            InlineKeyboardButton(
                text=f"🏷️ {g.name} • {g.discount_percent}% • {g.price_points} баллов",
                callback_data=f"promo_group:{g.id}",
            )
        ]
        for g in groups
    ]
    rows.append([InlineKeyboardButton(text="↩ Назад", callback_data="catalog_root")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

