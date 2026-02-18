from collections import Counter
from datetime import timezone as tz
from io import BytesIO
from zoneinfo import ZoneInfo

from django.contrib.admin.views.decorators import staff_member_required
from django.db.models import Count, Exists, F, OuterRef
from django.db.models.functions import Coalesce
from django.http import HttpResponse
from openpyxl import Workbook

from core.constants import get_referral_source_display
from core.models import LedgerEntry, OrderItem, Referral, User


def export_users_to_xlsx_response(queryset):
    """Формирует XLSX-выгрузку пользователей. Принимает queryset (все или выбранные)."""
    wb = Workbook()
    ws = wb.active
    ws.title = "Пользователи"

    headers_ru = [
        "ID",
        "Telegram ID",
        "Имя пользователя",
        "Телефон",
        "Адрес электронной почты",
        "Баланс",
        "Шаги",
        "Всего прогулок",
        "Прогулки с коляской",
        "Прогулки с собакой",
        "Прогулки с коляской и собакой",
        "По рефералу",
        "Источник перехода",
        "Рефералов",
        "Покупки",
        "Дни/время прогулок",
        "Роль",
        "Активен",
        "Семья",
    ]
    ws.append(headers_ru)

    qs = queryset.annotate(
        _referral_count=Count("my_referrals"),
        _is_referral=Exists(Referral.objects.filter(user_id=OuterRef("id"))),
        _walk_total=Coalesce(F("walk_count_stroller"), 0)
        + Coalesce(F("walk_count_dog"), 0)
        + Coalesce(F("walk_count_stroller_dog"), 0),
    ).select_related("family").prefetch_related("referred_by").order_by("id")

    day_names = ["Вс", "Пн", "Вт", "Ср", "Чт", "Пт", "Сб"]
    moscow = ZoneInfo("Europe/Moscow")

    for user in qs:
        purchases = list(
            OrderItem.objects.filter(order__user_id=user.id)
            .select_related("product")
            .values_list("product__title", "qty")
        )
        purchases_summary = ", ".join(f"{p}×{q}" for p, q in purchases if p) or ""

        dates = list(
            LedgerEntry.objects.filter(
                user_id=user.id,
                title="Начисление за прогулку",
                walk_form__isnull=False,
            ).values_list("created_at", flat=True)
        )
        if dates:
            slots = []
            for dt in dates:
                if dt:
                    if dt.tzinfo is None:
                        dt = dt.replace(tzinfo=tz.utc)
                    dt_local = dt.astimezone(moscow)
                    slots.append(f"{day_names[dt_local.weekday()]} {dt_local.hour}:00")
            top = Counter(slots).most_common(3)
            walks_summary = ", ".join(f"{s} ({c})" for s, c in top)
        else:
            walks_summary = ""

        family_name = str(user.family) if user.family_id and user.family else ""
        walk_total = getattr(user, "_walk_total", 0)

        refs = list(user.referred_by.all())
        if refs:
            raw_source = refs[0].referral_source or "referral"
        else:
            raw_source = getattr(user, "landing_source", None)
        source_display = get_referral_source_display(raw_source)

        row = [
            user.id,
            user.telegram_id,
            user.username or "",
            user.phone or "",
            user.email or "",
            user.balance,
            user.step_count,
            walk_total,
            getattr(user, "walk_count_stroller", 0),
            getattr(user, "walk_count_dog", 0),
            getattr(user, "walk_count_stroller_dog", 0),
            "Да" if getattr(user, "_is_referral", False) else "Нет",
            source_display,
            getattr(user, "_referral_count", 0),
            purchases_summary,
            walks_summary,
            user.role,
            user.is_active,
            family_name,
        ]
        ws.append(row)

    buf = BytesIO()
    wb.save(buf)
    buf.seek(0)

    response = HttpResponse(
        buf.getvalue(),
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
    response["Content-Disposition"] = 'attachment; filename="users_export.xlsx"'
    return response


@staff_member_required
def export_users_xlsx(request):
    """Выгрузка всех пользователей в XLSX."""
    return export_users_to_xlsx_response(User.objects.all())
