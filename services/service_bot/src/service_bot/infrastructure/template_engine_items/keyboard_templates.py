from collections.abc import Iterable
from typing import Literal

from aiogram.enums import ButtonStyle
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from service_bot.domain.entities import Cabinet, Group, User


class TemplateKeyboardRenderer:
    """ "Класс шаблонизатора клавиатуры"""

    @staticmethod
    def main_menu(
        user: "User",
        items: Iterable["Group | Cabinet"] | None = None,
    ) -> InlineKeyboardMarkup:
        """Шаблон клавиатуры главного меню"""
        builder = InlineKeyboardBuilder()

        item_type = "group" if user.user_type == "student" else "cabinet"

        if items is not None:
            subscribed = (
                user.group_subscribes
                if user.user_type == "student"
                else user.cabinet_subscribes
            )

            for item in items:
                if item.index in subscribed:
                    builder.button(
                        text=str(item),
                        callback_data=f"open_{item_type}_{item.index}",
                    )

        builder.adjust(3)

        builder.row(
            InlineKeyboardButton(
                text=f"➕ Добавить {
                    'группу' if user.user_type == 'student' else 'кабинет'
                }",
                callback_data="add_schedule_item",
            ),
            InlineKeyboardButton(
                text="⚙ Настройки",
                callback_data="open_settings",
                style=ButtonStyle.PRIMARY,
            ),
        )

        if user.is_admin:
            builder.row(
                InlineKeyboardButton(
                    text="💎 Админ-панель",
                    callback_data="open_admin_panel",
                    style=ButtonStyle.DANGER,
                ),
            )

        return builder.as_markup()

    @staticmethod
    def to_main_menu() -> InlineKeyboardMarkup:
        """Шаблон кнопки перехода в главное меню"""
        builder = InlineKeyboardBuilder()

        builder.row(
            InlineKeyboardButton(
                text="🏠 В главное меню",
                callback_data="open_main_menu",
            ),
        )

        return builder.as_markup()

    @staticmethod
    def delete_message() -> InlineKeyboardMarkup:
        """Шаблон кнопки удаления сообщения"""
        builder = InlineKeyboardBuilder()

        builder.row(
            InlineKeyboardButton(
                text="❌ Удалить сообщение",
                callback_data="delete_message",
            ),
        )

        return builder.as_markup()

    @staticmethod
    def user_settings(user: "User") -> InlineKeyboardMarkup:
        """Шаблон клавиатуры настроек пользователя"""
        builder = InlineKeyboardBuilder()

        builder.row(
            InlineKeyboardButton(
                text="🔔 Уведомления",
                callback_data="user_settings_notifications",
                style=(
                    ButtonStyle.SUCCESS
                    if user.notifications_enabled
                    else ButtonStyle.DANGER
                ),
            ),
            (
                InlineKeyboardButton(
                    text="👨‍🎓 Тип профиля",
                    callback_data="user_settings_profile_type",
                )
                if user.user_type == "student"
                else InlineKeyboardButton(
                    text="👨‍🏫 Тип профиля",
                    callback_data="user_settings_profile_type",
                )
            ),
        )

        builder.row(
            InlineKeyboardButton(
                text="📚 Группировка пар",
                callback_data="user_settings_grouping_lessons",
                style=(
                    ButtonStyle.SUCCESS if user.grouping_lessons else ButtonStyle.DANGER
                ),
            ),
        )

        builder.row(
            InlineKeyboardButton(
                text="🏠 В главное меню",
                callback_data="open_main_menu",
            ),
        )

        return builder.as_markup()

    @staticmethod
    def day_schedule(
        item_index: str,
        schedule_for: Literal["group", "cabinet"],
        schedule_to: Literal["today", "tomorrow"],
    ) -> InlineKeyboardMarkup:
        """Шаблон клавиатуры расписания пар"""
        builder = InlineKeyboardBuilder()

        builder.row(
            InlineKeyboardButton(
                text="◀ Сегодня",
                callback_data=f"schedule_{schedule_for}_{item_index}_today"
                f"{'_update' if schedule_to == 'today' else ''}",
                style=ButtonStyle.SUCCESS
                if schedule_to == "today"
                else ButtonStyle.DANGER,
            ),
            InlineKeyboardButton(
                text="Завтра ▶",
                callback_data=f"schedule_{schedule_for}_{item_index}_tomorrow"
                f"{'_update' if schedule_to == 'tomorrow' else ''}",
                style=ButtonStyle.SUCCESS
                if schedule_to == "tomorrow"
                else ButtonStyle.DANGER,
            ),
            InlineKeyboardButton(
                text="❌ Удалить",
                callback_data=f"schedule_{schedule_for}_{item_index}_delete",
            ),
            InlineKeyboardButton(
                text="🏠 В главное меню",
                callback_data="open_main_menu",
            ),
            width=2,
        )

        return builder.as_markup()
