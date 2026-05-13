import logging

from aiogram import Bot
from aiogram.types import BufferedInputFile
from aiohttp import web

from bot import database as db
from bot.keyboards.builders import after_payment_kb
from bot.services import storage
from bot.services.robokassa import verify_result

logger = logging.getLogger(__name__)


async def robokassa_result(request: web.Request) -> web.Response:
    bot: Bot = request.app["bot"]

    try:
        if request.method == "POST":
            data = await request.post()
        else:
            data = request.query
        out_sum = data.get("OutSum", "")
        inv_id = data.get("InvId", "")
        signature = data.get("SignatureValue", "")
        shp_uid = data.get("Shp_uid", "")
    except Exception:
        logger.exception("Failed to parse Robokassa result request")
        return web.Response(status=400)

    logger.info(
        "Robokassa result: InvId=%s OutSum=%s Shp_uid=%s",
        inv_id, out_sum, shp_uid,
    )

    if not verify_result(out_sum, inv_id, signature, shp_uid):
        logger.warning("Robokassa: invalid signature for InvId=%s", inv_id)
        return web.Response(status=400, text="bad signature")

    try:
        payment_id = int(inv_id)
        uid = int(shp_uid)
        credits = await db.complete_payment(payment_id, f"robokassa:{inv_id}")
        logger.info("User %s credited %s generations payment_id=%s", uid, credits, payment_id)
    except Exception:
        logger.exception("Payment crediting failed InvId=%s", inv_id)
        return web.Response(status=500)

    if credits == 0:
        logger.info("Robokassa duplicate callback ignored InvId=%s", inv_id)
        return web.Response(text=f"OK{inv_id}")

    try:
        await bot.send_message(
            uid,
            f"✅ Оплата прошла! Начислено <b>{credits} генераций</b>.\n\nМожешь продолжать.",
            parse_mode="HTML",
            reply_markup=after_payment_kb(),
        )
    except Exception:
        logger.exception("Failed to notify user %s about payment", uid)

    try:
        storage_path = await db.get_pending_unlock(uid)
        if storage_path:
            try:
                clean_bytes = await storage.download_clean_photo(storage_path)
                await bot.send_photo(
                    uid,
                    BufferedInputFile(clean_bytes, filename="result.jpg"),
                    caption="Вот твоё фото без водяного знака! 🎉",
                )
                logger.info("User %s pending clean photo delivered", uid)
            except Exception:
                logger.exception("Failed to download clean photo user=%s path=%s", uid, storage_path)
            finally:
                await storage.delete_clean_photo(storage_path)
                await db.delete_pending_unlock(uid)
    except Exception:
        logger.exception("Failed to deliver pending clean photo user=%s", uid)

    return web.Response(text=f"OK{inv_id}")


def create_app(bot: Bot) -> web.Application:
    app = web.Application()
    app["bot"] = bot
    app.router.add_get("/robokassa/result", robokassa_result)
    app.router.add_post("/robokassa/result", robokassa_result)
    return app
