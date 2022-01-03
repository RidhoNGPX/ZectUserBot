import time
from pyrogram import filters
import asyncio

from pitik import app
from config import LOG_CHAT
from Zect.helpers.pyrohelper import get_arg
import Zect.database.afkdb as pitik
from Zect.helpers.pyrohelper import user_afk
from Zect.modules.alive import get_readable_time
from Zect.helpers.utils import get_message_type, Types


LOG_CHAT = LOG_CHAT

MENTIONED = []
AFK_RESTIRECT = {}
DELAY_TIME = 60


@app.on_message(filters.command("afk"))
async def afk(client, message):
    afk_time = int(time.time())
    arg = get_arg(message)
    if not arg:
        reason = None
    else:
        reason = arg
    await pitik.set_afk(True, afk_time, reason)
    await message.reply("**Aku bakal lunga afk**")


@app.on_message(filters.mentioned & ~filters.bot & filters.create(user_afk), group=11)
async def afk_mentioned(_, message):
    global MENTIONED
    afk_time, reason = await pitik.afk_stuff()
    afk_since = get_readable_time(time.time() - afk_time)
    if "-" in str(message.chat.id):
        cid = str(message.chat.id)[4:]
    else:
        cid = str(message.chat.id)

    if cid in list(AFK_RESTIRECT) and int(AFK_RESTIRECT[cid]) >= int(time.time()):
        return
    AFK_RESTIRECT[cid] = int(time.time()) + DELAY_TIME
    if reason:
        await message.reply(
            f"**Aku Afk Saiki**\n**awit**: `{afk_since}`\n**Alesane:** __{reason}__"
        )
    else:
        await message.reply(f"**Aku Afk Saiki (awit {afk_since})**")

        _, message_type = get_message_type(message)
        if message_type == Types.TEXT:
            text = message.text or message.caption
        else:
            text = message_type.name

        MENTIONED.append(
            {
                "user": message.from_user.first_name,
                "user_id": message.from_user.id,
                "chat": message.chat.title,
                "chat_id": cid,
                "text": text,
                "message_id": message.message_id,
            }
        )


@app.on_message(filters.create(user_afk) & filters.outgoing)
async def auto_unafk(_, message):
    await pitik.set_unafk()
    unafk_message = await app.send_message(message.chat.id, "**I'm no longer AFK**")
    global MENTIONED
    text = "**Total {} sebutno sampeyan**\n".format(len(MENTIONED))
    for x in MENTIONED:
        msg_text = x["text"]
        if len(msg_text) >= 11:
            msg_text = "{}...".format(x["text"])
        text += "- [{}](https://t.me/c/{}/{}) ({}): {}\n".format(
            x["user"],
            x["chat_id"],
            x["message_id"],
            x["chat"],
            msg_text,
        )
        await app.send_message(chat_id=LOG_CHAT, text=text)
        MENTIONED = []
    await asyncio.sleep(2)
    await unafk_message.delete()
