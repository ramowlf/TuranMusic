from pyrogram import filters
from pyrogram.types import Message

from config import BANNED_USERS, MONGO_DB_URI, OWNER_ID, MUSIC_BOT_NAME
from strings import get_command
from AlexaMusic import app
from AlexaMusic.misc import SUDOERS
from AlexaMusic.utils.database import add_sudo, remove_sudo
from AlexaMusic.utils.decorators.language import language

# Command
ADDSUDO_COMMAND = get_command("ADDSUDO_COMMAND")
DELSUDO_COMMAND = get_command("DELSUDO_COMMAND")
SUDOUSERS_COMMAND = get_command("SUDOUSERS_COMMAND")


@app.on_message(filters.command(ADDSUDO_COMMAND) & filters.user(OWNER_ID))
@language
async def useradd(client, message: Message, _):
    if MONGO_DB_URI is None:
        return await message.reply_text(
            "**ᴅᴜᴇ ᴛᴏ {MUSIC_BOT_NAME}'s ᴩʀɪᴠᴀᴄʏ ɪssᴜᴇs, ʏᴏᴜ ᴄᴀɴ'ᴛ ᴍᴀɴᴀɢᴇ sᴜᴅᴏ ᴜsᴇʀs ᴏɴ {MUSIC_BOT_NAME} ᴅᴀᴛᴀʙᴀsᴇ.\n\n ᴩʟᴇᴀsᴇ ᴀᴅᴅ ʏᴏᴜʀ ᴍᴏɴɢᴏ ᴅᴀᴛᴀʙᴀsᴇ ɪɴ ᴠᴀʀs ᴛᴏ ᴜsᴇ ᴛʜɪs ғᴇᴀᴛᴜʀᴇ.**"
        )
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(_["auth_1"])
        user = message.text.split(None, 1)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await app.get_users(user)
        if user.id in SUDOERS:
            return await message.reply_text(_["sudo_1"].format(user.mention))
        added = await add_sudo(user.id)
        if added:
            SUDOERS.add(user.id)
            await message.reply_text(_["sudo_2"].format(user.mention))
        else:
            await message.reply_text("ғᴀɪʟᴇᴅ.")
        return
    if message.reply_to_message.from_user.id in SUDOERS:
        return await message.reply_text(
            _["sudo_1"].format(message.reply_to_message.from_user.mention)
        )
    added = await add_sudo(message.reply_to_message.from_user.id)
    if added:
        SUDOERS.add(message.reply_to_message.from_user.id)
        await message.reply_text(
            _["sudo_2"].format(message.reply_to_message.from_user.mention)
        )
    else:
        await message.reply_text("ғᴀɪʟᴇᴅ.")
    return


@app.on_message(filters.command(DELSUDO_COMMAND) & filters.user(OWNER_ID))
@language
async def userdel(client, message: Message, _):
    if MONGO_DB_URI is None:
        return await message.reply_text(
            "**ᴅᴜᴇ ᴛᴏ {MUSIC_BOT_NAME}'s ᴩʀɪᴠᴀᴄʏ ɪssᴜᴇs, ʏᴏᴜ ᴄᴀɴ'ᴛ ᴍᴀɴᴀɢᴇ sᴜᴅᴏ ᴜsᴇʀs ᴏɴ {MUSIC_BOT_NAME} ᴅᴀᴛᴀʙᴀsᴇ.\n\n ᴩʟᴇᴀsᴇ ᴀᴅᴅ ʏᴏᴜʀ ᴍᴏɴɢᴏ ᴅᴀᴛᴀʙᴀsᴇ ɪɴ ᴠᴀʀs ᴛᴏ ᴜsᴇ ᴛʜɪs ғᴇᴀᴛᴜʀᴇ.**"
        )
    if not message.reply_to_message:
        if len(message.command) != 2:
            return await message.reply_text(_["auth_1"])
        user = message.text.split(None, 1)[1]
        if "@" in user:
            user = user.replace("@", "")
        user = await app.get_users(user)
        if user.id not in SUDOERS:
            return await message.reply_text(_["sudo_3"])
        removed = await remove_sudo(user.id)
        if removed:
            SUDOERS.remove(user.id)
            await message.reply_text(_["sudo_4"])
            return
        await message.reply_text("Something went wrong.")
        return
    user_id = message.reply_to_message.from_user.id
    if user_id not in SUDOERS:
        return await message.reply_text(_["sudo_3"])
    removed = await remove_sudo(user_id)
    if removed:
        SUDOERS.remove(user_id)
        await message.reply_text(_["sudo_4"])
        return
    await message.reply_text("Something went wrong.")


@app.on_message(filters.command(SUDOUSERS_COMMAND) & ~BANNED_USERS)
@language
async def sudoers_list(client, message: Message, _):
    # Sudo kullanıcılarını listeleme işlemi
    if message.from_user.id not in SUDOERS and message.from_user.id != OWNER_ID:
        return await message.reply_text("Bu komutu kullanma izniniz yok.")

    text = _["sudo_5"]
    user = await app.get_users(OWNER_ID)
    user = user.first_name if not user.mention else user.mention
    text += f"1➤ {user}\n"
    count = 0
    smex = 0
    for user_id in SUDOERS:
        if user_id != OWNER_ID:  # OWNER_ID'yi kontrol et
            try:
                user = await app.get_users(user_id)
                user = user.first_name if not user.mention else user.mention
                if smex == 0:
                    smex += 1
                    text += _["sudo_6"]
                count += 1
                text += f"{count}➤ {user}\n"
            except Exception:
                continue
    if count == 0:
        await message.reply_text(_["sudo_7"])
    else:
        await message.reply_text(text)