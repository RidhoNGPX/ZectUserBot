import io
import os
import random
import time

from PIL import Image
from pyrogram import emoji, filters
from pyrogram.raw.functions.messages import GetStickerSet
from pyrogram.raw.types import InputStickerSetShortName
from pyrogram.errors import YouBlockedUser, StickersetInvalid
from Zect.helpers.pyrohelper import get_args
from Zect import app, CMD_HELP
from config import PREFIX

CMD_HELP.update(
    {
        "sticker": """
『 **Sticker** 』
  `colong` -> kangs stickers or creates new ones".
  `stkrinfo` -> Get sticker pack info.
"""
    }
)



@app.on_message(filters.command("colong", PREFIX) & filters.me)
async def kang(client, message):
    user = await app.get_me()
    replied = message.reply_to_message
    photo = None
    emoji_ = None
    is_anim = False
    resize = False
    if replied and replied.media:
        if replied.photo:
            resize = True
        elif replied.document and "image" in replied.document.mime_type:
            resize = True
        elif replied.document and "tgsticker" in replied.document.mime_type:
            is_anim = True
        elif replied.sticker:
            if not replied.sticker.file_name:
                await message.edit("`Sticker ora duwe jeneng!`")
                return
            emoji_ = replied.sticker.emoji
            is_anim = replied.sticker.is_animated
            if not replied.sticker.file_name.endswith(".tgs"):
                resize = True
        else:
            await message.edit("`File sing ora didhukung!`")
            return
        await message.edit(f"`{random.choice(KANGING_STR)}`")
        photo = await app.download_media(message=replied)
    else:
        await message.edit("`Aku ora bisa kang...`")
        return
    if photo:
        args = get_args(message)
        pack = 1
        if len(args) == 2:
            emoji_, pack = args
        elif len(args) == 1:
            if args[0].isnumeric():
                pack = int(args[0])
            else:
                emoji_ = args[0]

        if emoji_ and emoji_ not in (
            getattr(emoji, a) for a in dir(emoji) if not a.startswith("_")
        ):
            emoji_ = None
        if not emoji_:
            emoji_ = "🤔"

        u_name = user.username
        if u_name:
            u_name = "@" + u_name
        else:
            u_name = user.first_name or user.id
        packname = f"a{user.id}_by_odier_{pack}"
        custom_packnick = f"{u_name}' Sticker Nyolong "
        packnick = f"{custom_packnick} Vol.{pack}"
        cmd = "/newpack"
        if resize:
            photo = resize_photo(photo)
        if is_anim:
            packname += "_anim"
            packnick += " (Animated)"
            cmd = "/newanimated"
        exist = False
        try:
            exist = await app.send(
                GetStickerSet(stickerset=InputStickerSetShortName(short_name=packname))
            )
        except StickersetInvalid:
            pass
        if exist is not False:
            try:
                await app.send_message("Stickers", "/addsticker")
            except YouBlockedUser:
                await message.edit("Mbukak kunci dhisik @Stickers")
                return
            await app.send_message("Stickers", packname)
            limit = "50" if is_anim else "120"
            while limit in await get_response(message):
                pack += 1
                packname = f"a{user.id}_by_pitik_{pack}"
                packnick = f"{custom_packnick} Vol.{pack}"
                if is_anim:
                    packname += "_anim"
                    packnick += " (Animated)"
                await message.edit(
                    "`Switching to Pack " + str(pack) + " due to insufficient space`"
                )
                await app.send_message("Stickers", packname)
                if await get_response(message) == "Invalid pack selected":
                    await app.send_message("Stickers", cmd)
                    await get_response(message)
                    await app.send_message("Stickers", packnick)
                    await get_response(message)
                    await app.send_document("Stickers", photo)
                    await get_response(message)
                    await app.send_message("Stickers", emoji_)
                    await get_response(message)
                    await app.send_message("Stickers", packname)
                    if is_anim:
                        await get_response(message)
                        await app.send_message(
                            "Stickers", f"<{packnick}>", parse_mode=None
                        )
                    await get_response(message)
                    await app.send_message("Stickers", "/publish")
                    await get_response(message)
                    await app.send_message("Stickers", "/skip")
                    out = f"[Dicolong](t.me/addstickers/{packname})"
                    await message.edit(
                        f"**Stikere Wis** {out} __in a Different Pack__**🙏😎**"
                    )
                    return
            await app.send_document("Stickers", photo)
            time.sleep(0.2)
            rsp = await get_response(message)
            if "Sorry, the file type is invalid." in rsp:
                await message.edit(
                    "`Gagal nambah stiker, gunakake` @Stickers "
                    "`bot kanggo nambah stiker kanthi manual.`"
                )
                return
            await app.send_message("Stickers", emoji_)
            await get_response(message)
            await app.send_message("Stickers", "/done")
        else:
            await message.edit("`nggawe paket stiker anyar...`")
            try:
                await app.send_message("Stickers", cmd)
            except YouBlockedUser:
                await message.edit("Mbukak kunci dhisik @Stickers")
                return
            await app.send_message("Stickers", packnick)
            await get_response(message)
            await app.send_document("Stickers", photo)
            await get_response(message)
            rsp = await get_response(message)
            if "Sorry, the file type is invalid." in rsp:
                await message.edit(
                    "`Gagal nambah stiker, gunakake` @Stickers "
                    "`bot kanggo nambah stiker kanthi manual.`"
                )
                return
            await app.send_message("Stickers", emoji_)
            await get_response(message)
            await app.send_message("Stickers", "/publish")
            if is_anim:
                await get_response(message)
                await app.send_message("Stickers", f"<{packnick}>", parse_mode=None)
            await get_response(message)
            await app.send_message("Stickers", "/skip")
            await get_response(message)
            await app.send_message("Stickers", packname)
        out = f"[Dicolong](t.me/addstickers/{packname})"
        await message.edit(f"**Stikere wis** {out}**🙏😎**")
        await app.read_history("Stickers")
        if os.path.exists(str(photo)):
            os.remove(photo)


@app.on_message(filters.command("stkrinfo", PREFIX) & filters.me)
async def sticker_pack_info_(client, message):
    replied = message.reply_to_message
    if not replied:
        await message.edit("`Aku ora bisa njupuk info saka apa-apa, bisa ?!`")
        return
    if not replied.sticker:
        await message.edit("`Mbales stiker kanggo entuk rincian pack`")
        return
    await message.edit("`Njupuk Rincian Paket Stiker, mangga tunggu..`")
    get_stickerset = await app.send(
        GetStickerSet(
            stickerset=InputStickerSetShortName(short_name=replied.sticker.set_name)
        )
    )
    pack_emojis = []
    for document_sticker in get_stickerset.packs:
        if document_sticker.emoticon not in pack_emojis:
            pack_emojis.append(document_sticker.emoticon)
    out_str = (
        f"**Sticker Title:** `{get_stickerset.set.title}\n`"
        f"**Sticker Short Name:** `{get_stickerset.set.short_name}`\n"
        f"**Archived:** `{get_stickerset.set.archived}`\n"
        f"**Official:** `{get_stickerset.set.official}`\n"
        f"**Masks:** `{get_stickerset.set.masks}`\n"
        f"**Animated:** `{get_stickerset.set.animated}`\n"
        f"**Stickers In Pack:** `{get_stickerset.set.count}`\n"
        f"**Emojis In Pack:**\n{' '.join(pack_emojis)}"
    )
    await message.edit(out_str)


def resize_photo(photo: str) -> io.BytesIO:
    """Resize the given photo to 512x512"""
    image = Image.open(photo)
    maxsize = 512
    scale = maxsize / max(image.width, image.height)
    new_size = (int(image.width * scale), int(image.height * scale))
    image = image.resize(new_size, Image.LANCZOS)
    resized_photo = io.BytesIO()
    resized_photo.name = "sticker.png"
    image.save(resized_photo, "PNG")
    os.remove(photo)
    return resized_photo


async def get_response(message):
    return [x async for x in app.iter_history("Stickers", limit=1)][0].text


KANGING_STR = (
    "Nggunakake Sihir kanggo nyolong stiker iki...",
    "Tak colong yo stikere hehe...",
    "Ngundang stiker iki menyang paket...",
    "Lagi Nyolong stiker iki...",
    "Hey iki stikere apik yo!\nApa olih tak colong?!..",
    "Hehe Aku nyolong stikere koe\nhehe.",
    "Delengen ana stiker apik (☉.☉)!→\nTek colong lah...",
    "Penjara stiker iki...",
)
