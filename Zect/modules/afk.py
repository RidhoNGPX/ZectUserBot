import time

from pyrogram import Client, filters
from pyrogram.types import Message


from config import LOG_CHAT, PREFIX
from Zect import app, CMD_HELP
from Zect.helpers.msg_types import Types, get_message_type
from Zect.helpers.parser import escape_markdown, mention_markdown
from Zect.database.sql.afk_db import get_afk, set_afk



MENTIONED = []
AFK_RESTIRECT = {}
DELAY_TIME = 3  # seconds


@app.on_message(filters.me & filters.command("afk", PREFIX))
async def afk(client: Client, message: Message):
    if len(message.text.split()) >= 2:
        set_afk(True, message.text.split(None, 1)[1])
        await message.edit(
            "{} <b>AFK! Right Now!</b>\n<b>Reason :</b> <code>{}</code>".format(
                mention_markdown(message.from_user.id, message.from_user.first_name),
                message.text.split(None, 1)[1],
            )
        )
    else:
        set_afk(True, "")
        await message.edit(
            "{} <b>AFK! Right Now!</b>".format(
                mention_markdown(message.from_user.id, message.from_user.first_name)
            )
        )
    await message.stop_propagation()


@app.on_message(
    (filters.mentioned | filters.private) & filters.incoming & ~filters.bot, group=11
)
async def afk_mentioned(client: Client, message: Message):
    global MENTIONED
    get = get_afk()
    if get and get["afk"]:
        if "-" in str(message.chat.id):
            cid = str(message.chat.id)[4:]
        else:
            cid = str(message.chat.id)

        if cid in list(AFK_RESTIRECT):
            if int(AFK_RESTIRECT[cid]) >= int(time.time()):
                return
        AFK_RESTIRECT[cid] = int(time.time()) + DELAY_TIME
        if get["reason"]:
            await message.reply(
                "{} <b>AFK! Right Now!</b>\n<b>Reason:</b> <code>{}</code>".format(
                    client.me.mention, get["reason"]
                )
            )
        else:
            await message.reply(
                f"<b>Sorry!</b> {client.me.first_name} <b>AFK! Right Now!</b>"
            )

        _, message_type = get_message_type(message)
        if message_type == Types.TEXT:
            if message.text:
                text = message.text
            else:
                text = message.caption
        else:
            text = message_type.name

        MENTIONED.append(
            {
                "user": message.from_user.first_name,
                "user_id": message.from_user.id,
                "chat": message.chat.title,
                "chat_id": cid,
                "text": text,
                "message_id": message.id,
            }
        )
        try:
            await client.send_message(
                LOG_CHAT,
                "<b>#MENTION\n • From :</b> {}\n • <b>Chat :</b> <code>{}</code>\n • <b>Message :</b> <code>{}</code>".format(
                    message.from_user.mention,
                    message.chat.title,
                    text[:3500],
                ),
            )
        except BaseException:
            pass


@app.on_message(filters.me & filters.group, group=12)
async def no_longer_afk(client: Client, message: Message):
    global MENTIONED
    get = get_afk()
    if get and get["afk"]:
        set_afk(False, "")
        try:
            await client.send_message(LOG_CHAT, "You are no longer AFK!")
        except BaseException:
            pass
        text = "<b>Total {} Mention while AFK<b>\n".format(len(MENTIONED))
        for x in MENTIONED:
            msg_text = x["text"]
            if len(msg_text) >= 11:
                msg_text = "{}...".format(x["text"])
            text += "- [{}](https://t.me/c/{}/{}) ({}): {}\n".format(
                escape_markdown(x["user"]),
                x["chat_id"],
                x["message_id"],
                x["chat"],
                msg_text,
            )
        try:
            await client.send_message(LOG_CHAT, text)
        except BaseException:
            pass
        MENTIONED = []

CMD_HELP.update(
    {
        "AFK": """
『 **AFK** 』
  `afk [reason]` -> Provides a message saying that you are unavailable.
"""
    }
)


