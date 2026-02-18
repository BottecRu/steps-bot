"""
Словарь преобразования кодов источников рефералов в читаемые названия.
Добавляйте свои пары по мере необходимости.
"""

REFERRAL_SOURCE_LABELS = {
    "referral": "Реферал",
    "telegram_channel": "Телеграм канал",
    "instagram": "Инстаграм",
    "vk": "ВКонтакте",
    "website": "Сайт",
    "friend": "Друзья/знакомые",
    "sticker": "Наклейки",
    "sticker_pets": "Наклейки",
    "insights": "Инсайты",
    "insights_kids": "Инсайты",
    "email": "Email",
    "tg_post": "Пост в телеграм",
    "telegram_post": "Пост в телеграм",
}


def get_referral_source_display(source: str | None) -> str:
    """Возвращает красивое название источника или исходное значение, если не найдено."""
    if not source:
        return "—"
    return REFERRAL_SOURCE_LABELS.get(source.strip().lower(), source)
