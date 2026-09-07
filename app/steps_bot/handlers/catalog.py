from __future__ import annotations

from math import ceil

from aiogram import Router, F
from aiogram.types import CallbackQuery

from app.steps_bot.presentation.keyboards.generic_kb import (
    PER_PAGE,
    catalog_page_kb,
    product_card_kb,
)
from app.steps_bot.services.catalog_service import (
    get_category_by_name,
    get_category_page,
    get_product,
    render_product,
)

router = Router()
VISIBLE_CATEGORY_NAME = "ROXY-PETS"


async def get_visible_category_id() -> int | None:
    category = await get_category_by_name(VISIBLE_CATEGORY_NAME)
    return category.id if category else None


async def show_category_page(
    callback: CallbackQuery,
    cat_id: int,
    page: int,
) -> None:
    products, total = await get_category_page(cat_id, page, PER_PAGE)
    if total == 0:
        await callback.answer("Здесь пока пусто", show_alert=True)
        return

    pages = max(1, ceil(total / PER_PAGE))
    page = max(1, min(page, pages))
    kb = catalog_page_kb(
        products,
        cat_id,
        page,
        pages,
        back_callback="back",
    )

    await callback.message.delete()
    await callback.message.answer("Список доступных товаров:", reply_markup=kb)
    await callback.answer()


@router.callback_query(F.data == "catalog")
async def catalog_root(callback: CallbackQuery):
    cat_id = await get_visible_category_id()
    if cat_id is None:
        await callback.answer("Каталог временно недоступен", show_alert=True)
        return
    await show_category_page(callback, cat_id, 1)


@router.callback_query(F.data == "catalog_root")
async def back_to_root(callback: CallbackQuery):
    await catalog_root(callback)


@router.callback_query(F.data.startswith("cat:"))
async def category_page(callback: CallbackQuery):
    _, cat_id, page = callback.data.split(":")
    cat_id, page = int(cat_id), int(page)

    visible_cat_id = await get_visible_category_id()
    if visible_cat_id is None or cat_id != visible_cat_id:
        await callback.answer("Каталог недоступен", show_alert=True)
        return

    await show_category_page(callback, cat_id, page)


@router.callback_query(F.data.startswith("product:"))
async def product_card(callback: CallbackQuery):
    _, prod_id, cat_id, page = callback.data.split(":")
    prod_id, cat_id, page = int(prod_id), int(cat_id), int(page)

    product = await get_product(prod_id)
    visible_cat_id = await get_visible_category_id()
    if (
        not product
        or not product.is_active
        or visible_cat_id is None
        or product.category_id != visible_cat_id
        or cat_id != visible_cat_id
    ):
        await callback.answer("Товар недоступен", show_alert=True)
        return

    await callback.message.delete()
    await render_product(
        callback.message,
        prod_id,
        reply_markup=product_card_kb(prod_id, cat_id, page),
    )
    await callback.answer()
