import asyncio
import json
import os
import logging
import time

from aiogram import F, Router, Bot
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import (CallbackQuery,
                           Message,
                           FSInputFile,
                           InputMediaPhoto,
                           LabeledPrice,
                           PreCheckoutQuery,
                           ShippingQuery,
                           ContentType)
from aiogram.utils.markdown import hbold, hcode, hlink

from database.repository import DataFacade

# from tg_bot.filters.user import AddAdminFilter
from tg_bot.config import Config
from tg_bot.misc.states import DownloadState
from tg_bot.services.youtubeManager import get_video_length, is_youtube_url, download_video_async
from tg_bot.services.messages_text import messages_text
from tg_bot.keyboards.user import (get_main_keyboard,
                                   get_back_keyboard,
                                   get_subscribe_keyboard,
                                   get_pay_keyboard,
                                   get_payment_methods_keyboard)
from tg_bot.services.utils import create_absolute_path, downloader_youtube_video
from tg_bot.filters.user import AddAdminFilter
from tg_bot.services.composer import Composer

logger = logging.getLogger(__name__)

user_router = Router()
user_router.message.filter(F.chat.type == "private")
user_router.callback_query.filter(F.message.chat.type == "private")


@user_router.message(AddAdminFilter())
async def add_admin(message: Message, config: Config,
                    dataFacade: DataFacade) -> None:
    if not message.from_user.id in config.tg_bot.admin_ids:
        config.tg_bot.admin_ids.append(message.from_user.id)
        await dataFacade.update_admin_ids(config.tg_bot.admin_ids)
        await message.answer("Вы получили права администратора")
    else:
        await message.answer("Вы уже являетесь администратором!")


@user_router.message(CommandStart())
@user_router.callback_query(F.data.startswith('main_menu'))
async def get_menu(obj: Message | CallbackQuery, state: FSMContext, dataFacade: DataFacade, bot: Bot) -> None:
    try:
        data = await state.get_data()
        user_id = int(data["user_id"])
        invoice_message = int(data["invoice_message"])
        await bot.delete_message(user_id, invoice_message)
    except:
        logging.info("Не invoice")

    await state.clear()
    if isinstance(obj, CallbackQuery):
        try:
            await obj.message.edit_text(text=messages_text["menu"], reply_markup=await get_main_keyboard())
        except:
            await obj.answer()
            await obj.message.answer(text=messages_text["menu"], reply_markup=await get_main_keyboard())
    else:
        await obj.answer(text=messages_text["menu"], reply_markup=await get_main_keyboard())

        try:
            username = None
            full_name = None
            if obj.from_user.username:
                username = obj.from_user.username
            if obj.from_user.full_name:
                full_name = obj.from_user.full_name
            await dataFacade.add_user(obj.chat.id, username, full_name)
        except Exception as e:
            logging.info(str(e))


@user_router.callback_query(F.data == 'download')
async def enter_url(call: CallbackQuery, state: FSMContext) -> None:
    await call.answer()
    await state.clear()
    await state.set_state(DownloadState.waiting_send_video_url)
    await call.message.edit_text(text=messages_text["downloadUrl"], reply_markup=await get_back_keyboard())


@user_router.message(DownloadState.waiting_send_video_url)
async def download_youtube_video(message: Message, state: FSMContext, dataFacade: DataFacade, bot: Bot, config: Config, composer: Composer) -> None:
    await downloader_youtube_video(message, state, dataFacade, bot, config, composer)


@user_router.message(Command(commands=['help']))
@user_router.callback_query(F.data == 'help')
async def get_help(obj: Message | CallbackQuery, state: FSMContext):
    await state.clear()

    if isinstance(obj, CallbackQuery):
        await obj.answer()
        await obj.message.edit_text(text=hcode(messages_text["help"]), reply_markup=await get_back_keyboard())
    else:
        await obj.answer(text=hcode(messages_text["help"]), reply_markup=await get_back_keyboard())


@user_router.message(Command(commands=['premium']))
@user_router.callback_query(F.data == 'subscribe')
async def send_donat(obj: Message | CallbackQuery, state: FSMContext, dataFacade: DataFacade) -> None:
    await state.clear()

    if isinstance(obj, CallbackQuery):
        await obj.answer()
        user = await dataFacade.get_user(user_id=obj.message.chat.id)
        if user.premium:
            await obj.message.edit_text(text=messages_text["subscribed"], reply_markup=await get_back_keyboard())
            return
        messsage_subscribe = await obj.message.edit_text(text=messages_text["subscribe"], reply_markup=await get_payment_methods_keyboard())
    else:
        user = await dataFacade.get_user(user_id=obj.chat.id)
        if user.premium:
            await obj.answer(text=messages_text["subscribed"], reply_markup=await get_back_keyboard())
            return
        messsage_subscribe = await obj.answer(text=messages_text["subscribe"], reply_markup=await get_payment_methods_keyboard())
    await state.set_data({"message_id": messsage_subscribe.message_id})


@user_router.callback_query(F.data == 'bankcards')
async def send_donat(call: CallbackQuery, state: FSMContext, config: Config, bot: Bot) -> None:
    await call.answer()
    data = await state.get_data()
    message_subscribe = int(data["message_id"])
    await state.clear()
    user_id = call.message.chat.id

    price = 79
    description = messages_text['paydescription']
    provider_data_dict = {
        "receipt": {
            "items": [
                {
                    "description": description,
                    "quantity": "1",
                    "vat_code": 1,
                    "amount": {
                        "value": str(price),
                        "currency": "RUB"
                    },
                }
            ]
        }
    }
    provider_data = json.dumps(provider_data_dict)

    invoice_message = await call.message.answer_invoice(
        title="Premium",
        description=description,
        provider_token=config.tg_bot.yookassa_token,
        currency="RUB",

        need_email=True,
        send_email_to_provider=True,
        provider_data=provider_data,
    #    photo_url='https://telegra.ph/file/some.jpg',
    #    photo_height=256,  # !=0/None or picture won't be shown
    #    photo_width=256,
    #    photo_size=512,
        is_flexible=False,
        prices=[
            LabeledPrice(
                label=description,
                amount=int(price * 100)
            )
        ],
        payload=str(user_id),
        reply_markup=await get_pay_keyboard(),
    )
    await bot.delete_message(user_id, message_subscribe)
    await state.set_data({"invoice_message": invoice_message.message_id, "user_id": user_id})


@user_router.shipping_query()
async def shipping(shipping_query: ShippingQuery) -> None:
    await shipping_query.answer(ok=True, error_message='Shipping error')


@user_router.pre_checkout_query()
async def pre_checkout(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True, error_message=f"Checkout error, ID = {pre_checkout_query.id}")


@user_router.message(F.content_type == ContentType.SUCCESSFUL_PAYMENT)
async def got_payment(message: Message, dataFacade: DataFacade, state: FSMContext) -> None:
    payment = message.successful_payment
    if not payment:
        await message.answer(text=messages_text["payError"], disable_web_page_preview=True)
        return

    user_id = int(payment.invoice_payload)
    user = await dataFacade.get_user(user_id=user_id)
    if not user:
        return

    amount = payment.total_amount / 100
    await dataFacade.add_payment(user_id=user_id, amount=round(amount, ndigits=2), method="bankcard")

    await dataFacade.update_user_premium(user_id=user_id, premium=True, email=payment.order_info.email)
    await message.answer(text=messages_text["paySuccess"], reply_markup=await get_back_keyboard(), disable_web_page_preview=True)


@user_router.message()
async def all_meesages(message: Message, state: FSMContext, dataFacade: DataFacade, bot: Bot, config: Config, composer: Composer):
    await state.clear()

    if message.chat.id == config.tg_bot.client_user_id:
        logging.info(message)
        video = message.video
        data = message.caption.split("*_*")
        user_id = int(data[0])
        message_del_id = int(data[1])

        await bot.delete_message(user_id, message_del_id)
        await bot.send_video(chat_id=user_id, video=video.file_id, caption=messages_text['followus'])
        return

    await downloader_youtube_video(message, state, dataFacade, bot, config, composer)
