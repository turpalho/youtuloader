from typing import List

from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types.inline_keyboard_button import InlineKeyboardButton
from aiogram.types import InlineKeyboardMarkup


async def get_main_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(*[
        InlineKeyboardButton(text="🎥  Скачать видео", callback_data="download"),
        InlineKeyboardButton(text="❓  Инструкция", callback_data="help"),
        InlineKeyboardButton(text="🔰  Premium", callback_data="subscribe"),
    ])
    kb.adjust(1)
    return kb.as_markup()


async def get_back_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(*[
        InlineKeyboardButton(text="🔙  Главное меню", callback_data="main_menu")
    ])
    kb.adjust(1)
    return kb.as_markup()


async def get_subscribe_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(*[
        InlineKeyboardButton(text="🔰  Купить Premium", callback_data="subscribe"),
        InlineKeyboardButton(text="🔙  Главное меню", callback_data="main_menu")
    ])
    kb.adjust(1)
    return kb.as_markup()


async def get_payment_methods_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(*[
        InlineKeyboardButton(text="💳  Банковские карты", callback_data="bankcards"),
        InlineKeyboardButton(text="🔙  Главное меню", callback_data=f"main_menu")
    ])
    kb.adjust(1)
    return kb.as_markup()


async def get_pay_keyboard() -> InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.add(*[
        InlineKeyboardButton(text="💲  Оплатить", pay=True),
        InlineKeyboardButton(text="🔙  Главное меню", callback_data=f"main_menu")
    ])
    kb.adjust(1)
    return kb.as_markup()