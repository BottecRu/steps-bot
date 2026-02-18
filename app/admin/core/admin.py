from django.contrib import admin
from django.contrib.auth.models import Group, User as AuthUser

from django.contrib import messages

from core.models import (
    Family,
    FamilyInvitation,
    WalkFormCoefficient,
    TemperatureCoefficient,
    Content,
    User,
    FAQ,
    CatalogCategory,
    Product,
    OrderStatusChoices,
    Order,
    OrderItem,
    UserAddress,
    BotSetting,
    PromoGroup,
    PromoCode,
    Broadcast,
    Referral,
    LedgerEntry,
    PVZ,
)
from core.constants import get_referral_source_display
from core.views import export_users_to_xlsx_response

admin.site.unregister(Group)
admin.site.unregister(AuthUser)


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "balance", "step_count")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(FamilyInvitation)
class FamilyInvitationAdmin(admin.ModelAdmin):
    list_display = ("id", "family", "inviter_id", "invitee_id", "status")
    list_filter = ("status", "family")
    search_fields = ("family__name", "invitee_id")


@admin.register(WalkFormCoefficient)
class WalkFormCoefficientAdmin(admin.ModelAdmin):
    list_display = ("walk_form", "coefficient")
    list_editable = ("coefficient",)
    ordering = ("walk_form",)


@admin.register(TemperatureCoefficient)
class TemperatureCoefficientAdmin(admin.ModelAdmin):
    list_display = ("walk_form", "min_temp_c", "max_temp_c", "coefficient")
    list_filter = ("walk_form",)
    list_editable = ("coefficient",)
    ordering = ("walk_form", "min_temp_c")


@admin.register(Content)
class ContentAdmin(admin.ModelAdmin):
    """
    Контент с медиа.
    """
    list_display = ("slug", "media_type", "file", "telegram_file_id", "media_url")
    list_editable = ("media_type", "telegram_file_id", "media_url")
    list_filter = ("media_type",)
    search_fields = ("slug",)


class WalkCountFilter(admin.SimpleListFilter):
    title = "Количество прогулок"
    parameter_name = "walk_count"

    def lookups(self, request, model_admin):
        return (
            ("0", "0"),
            ("1_5", "1–5"),
            ("6_20", "6–20"),
            ("21_plus", "21+"),
        )

    def queryset(self, request, queryset):
        from django.db.models import F
        from django.db.models.functions import Coalesce
        if self.value() == "0":
            return queryset.filter(walk_count_stroller=0, walk_count_dog=0, walk_count_stroller_dog=0)
        if self.value() == "1_5":
            return queryset.annotate(
                _total=Coalesce(F("walk_count_stroller"), 0) + Coalesce(F("walk_count_dog"), 0) + Coalesce(F("walk_count_stroller_dog"), 0)
            ).filter(_total__gte=1, _total__lte=5)
        if self.value() == "6_20":
            return queryset.annotate(
                _total=Coalesce(F("walk_count_stroller"), 0) + Coalesce(F("walk_count_dog"), 0) + Coalesce(F("walk_count_stroller_dog"), 0)
            ).filter(_total__gte=6, _total__lte=20)
        if self.value() == "21_plus":
            return queryset.annotate(
                _total=Coalesce(F("walk_count_stroller"), 0) + Coalesce(F("walk_count_dog"), 0) + Coalesce(F("walk_count_stroller_dog"), 0)
            ).filter(_total__gte=21)
        return queryset


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = (
        "id", "telegram_id", "username", "phone", "email", "balance", "step_count",
        "walk_total_display",
        "walk_count_stroller", "walk_count_dog", "walk_count_stroller_dog",
        "is_referral_display", "landing_source_display",
        "referral_count_display",
        "purchases_summary_display", "walks_schedule_summary_display",
        "role", "is_active", "family",
    )
    list_filter = ("role", "is_active", WalkCountFilter)
    search_fields = ("telegram_id", "phone", "username")
    actions = ["export_selected_xlsx"]

    def export_selected_xlsx(self, request, queryset):
        """Выгрузить выбранных пользователей в Excel."""
        if not queryset.exists():
            self.message_user(request, "Выберите хотя бы одного пользователя.", messages.WARNING)
            return
        return export_users_to_xlsx_response(queryset)
    export_selected_xlsx.short_description = "Выгрузить в Excel"

    def get_queryset(self, request):
        from django.db.models import Count, Exists, F, OuterRef
        from django.db.models.functions import Coalesce
        qs = super().get_queryset(request)
        qs = qs.annotate(
            _referral_count=Count("my_referrals"),
            _is_referral=Exists(Referral.objects.filter(user_id=OuterRef("id"))),
            _walk_total=Coalesce(F("walk_count_stroller"), 0) + Coalesce(F("walk_count_dog"), 0) + Coalesce(F("walk_count_stroller_dog"), 0),
        )
        return qs

    def walk_total_display(self, obj):
        return getattr(obj, "_walk_total", 0)
    walk_total_display.short_description = "Всего прогулок"
    walk_total_display.admin_order_field = "_walk_total"

    def is_referral_display(self, obj):
        return "Да" if getattr(obj, "_is_referral", False) else "Нет"
    is_referral_display.short_description = "По рефералу"

    def landing_source_display(self, obj):
        ref = Referral.objects.filter(user_id=obj.id).first()
        if ref:
            return get_referral_source_display(ref.referral_source or "referral")
        return get_referral_source_display(getattr(obj, "landing_source", None))
    landing_source_display.short_description = "Источник перехода"

    def referral_count_display(self, obj):
        return getattr(obj, "_referral_count", 0)
    referral_count_display.short_description = "Рефералов"

    def purchases_summary_display(self, obj):
        items = OrderItem.objects.filter(order__user_id=obj.id).select_related("product")
        return ", ".join(f"{i.product.title}×{i.qty}" for i in items[:10]) or "—"
    purchases_summary_display.short_description = "Покупки"

    def walks_schedule_summary_display(self, obj):
        from collections import Counter
        from zoneinfo import ZoneInfo
        moscow = ZoneInfo("Europe/Moscow")
        dates = list(LedgerEntry.objects.filter(
            user_id=obj.id, title="Начисление за прогулку", walk_form__isnull=False
        ).values_list("created_at", flat=True))
        if not dates:
            return "—"
        day_names = ["Вс", "Пн", "Вт", "Ср", "Чт", "Пт", "Сб"]
        slots = []
        for dt in dates:
            if dt:
                if dt.tzinfo is None:
                    from datetime import timezone as tz
                    dt = dt.replace(tzinfo=tz.utc)
                dt_local = dt.astimezone(moscow)
                slots.append(f"{day_names[dt_local.weekday()]} {dt_local.hour}:00")
        if not slots:
            return "—"
        top = Counter(slots).most_common(3)
        return ", ".join(f"{s} ({c})" for s, c in top)
    walks_schedule_summary_display.short_description = "Дни/время прогулок"

    add_fieldsets = (
        (None, {
            "fields": (
                "telegram_id", "phone", "email", "username",
                "balance", "step_count", "family",
            ),
        }),
    )

    fieldsets = (
        (None, {
            "fields": (
                "telegram_id", "username", "phone", "email",
                "balance", "step_count", "family",
                "role", "is_active",
            ),
        }),
    )


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display  = ("slug", "question", "media_type", "telegram_file_id", "media_url")
    list_editable = ("media_type", "telegram_file_id", "media_url")
    search_fields = ("slug", "question")


@admin.register(CatalogCategory)
class CatalogCategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name")
    search_fields = ("name",)


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "category", "price", "is_active", "media_type")
    list_filter = ("category", "is_active", "media_type")
    search_fields = ("title",)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("product", "qty")
    can_delete = False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ("id", "user_display", "status", "total_price", "pvz_id", "created_at")
    list_filter = ("status",)
    search_fields = ("id", "pvz_id", "user__telegram_id")
    inlines = (OrderItemInline,)

    def user_display(self, obj):
        if obj.user.username:
            return f"@{obj.user.username}"
        return f"ID: {obj.user.telegram_id}"
    user_display.short_description = "Пользователь"


@admin.register(BotSetting)
class BotSettingAdmin(admin.ModelAdmin):
    list_display = ("key", "value", "description_hint")
    search_fields = ("key",)
    fields = ("key", "value")
    
    def description_hint(self, obj):
        """Подсказка для каждой настройки"""
        hints = {
            "поддержка": "Ссылка на тех. поддержку",
            "referral_reward_percent": "Процент вознаграждения за реферала (например, 10 для 10%)",
        }
        return hints.get(obj.key, "")
    description_hint.short_description = "Описание"
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.key == "referral_reward_percent":
            if 'value' in form.base_fields:
                form.base_fields['value'].help_text = "Укажите процент вознаграждения (например, 10 для 10%)"
        return form
from django.contrib import admin
from core.models import PromoGroup, PromoCode


class PromoCodeInline(admin.TabularInline):
    """
    Инлайн промокодов внутри группы.
    """
    model = PromoCode
    extra = 0
    fields = ("code", "max_uses", "used_count", "is_active")
    show_change_link = True
    can_delete = True


@admin.register(PromoGroup)
class PromoGroupAdmin(admin.ModelAdmin):
    """
    Управление группами промокодов.
    """
    list_display = ("id", "name", "discount_percent", "price_points", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
    inlines = (PromoCodeInline,)


@admin.register(PromoCode)
class PromoCodeAdmin(admin.ModelAdmin):
    """
    Управление отдельными промокодами.
    """
    list_display = ("id", "code", "group", "max_uses", "used_count", "is_active", "created_at")
    list_filter = ("is_active", "group")
    search_fields = ("code",)
    autocomplete_fields = ("group",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
    fields = ("code", "group", "max_uses", "used_count", "is_active", "created_at")


@admin.register(Broadcast)
class BroadcastAdmin(admin.ModelAdmin):
    list_display = ("id", "status", "scheduled_at", "sent_at")
    list_filter = ("status",)
    search_fields = ("id", "text")
    fields = ("text", "media_type", "media_file", "telegram_file_id", "media_url", "scheduled_at", "sent_at")
    readonly_fields = ("sent_at", "status")


@admin.register(Referral)
class ReferralAdmin(admin.ModelAdmin):
    list_display = ("id", "user_display", "inviter_display", "referral_source_display", "reward_points", "created_at")
    list_filter = ("created_at", "referral_source")
    search_fields = ("user__telegram_id", "user__username", "inviter__telegram_id", "inviter__username")
    readonly_fields = ("user", "inviter", "referral_source_display", "reward_points", "created_at")
    ordering = ("-created_at",)

    def referral_source_display(self, obj):
        return get_referral_source_display(obj.referral_source or "referral")
    referral_source_display.short_description = "Источник ссылки"

    def user_display(self, obj):
        """Отображает username или telegram_id пользователя"""
        if obj.user.username:
            return f"@{obj.user.username}"
        return f"ID: {obj.user.telegram_id}"
    user_display.short_description = "Пользователь"

    def inviter_display(self, obj):
        """Отображает username или telegram_id пригласившего"""
        if obj.inviter.username:
            return f"@{obj.inviter.username}"
        return f"ID: {obj.inviter.telegram_id}"
    inviter_display.short_description = "Пригласивший"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return True


@admin.register(PVZ)
class PVZAdmin(admin.ModelAdmin):
    """
    Управление пунктами выдачи (ПВЗ).
    """
    list_display = ("id", "full_address", "created_at")
    search_fields = ("id", "full_address")
    list_filter = ("created_at",)
    ordering = ("-created_at",)
    readonly_fields = ("created_at",)
    fields = ("id", "full_address", "created_at")


