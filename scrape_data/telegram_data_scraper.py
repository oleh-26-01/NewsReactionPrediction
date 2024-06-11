import json
import time

import helper as h
import pickle
import os

from pyrogram import filters


class Global:
    response_prefix = "~"


app = h.log_in("./auth_data.json", update_session_string=False)


@app.on_message(filters.chat("me") & filters.command("info"))
async def info(client, command_message):
    if not command_message.reply_to_message:
        await command_message.reply("Please reply to a message.", quote=True)
        return

    target_message_id = command_message.reply_to_message.id

    # get the forwarded message and save it
    message = await client.get_messages("me", target_message_id)
    h.save_message("last_message.json", message)

    # approve command execution
    reply_message = await message.reply(Global.response_prefix + "info extracted", quote=True)

    # delete the command message and the reply message
    h.delete_message_with_delay(reply_message)
    await command_message.delete()


@app.on_message(filters.chat("me") & filters.command("check"))
async def check(client, command_message):
    # open the last message
    data = open("last_message.json", "r").read()
    data = json.loads(data)
    chat_id = data["forward_from_chat"]["id"]
    last_message_id = data["forward_from_message_id"]

    special_message = ""
    messages_count = 3
    for i in range(messages_count):
        message = await client.get_messages(chat_id, last_message_id - i)
        special_message += message.__str__() + "\n\n"

    reply_message = Global.response_prefix + \
                    f"chat_id: {chat_id}\nmessage_id: {last_message_id}\n\n" + \
                    special_message

    # check if the message is too long
    if len(reply_message) > 4096:
        reply_message = reply_message[:4096] + "\n\n[message too long]"

    # reply to the command message with chat id and message id
    reply_message = await command_message.reply(reply_message, quote=True)

    # delete the command message and the reply message
    h.delete_message_with_delay(reply_message)
    await command_message.delete()


@app.on_message(filters.chat("me") & filters.command("extract"))
async def extract(client, command_message):
    # open the last message
    data = open("last_message.json", "r").read()
    data = json.loads(data)

    # Get the channel name from the command
    # channel_name = data["forward_from_chat"]["username"]
    # check if key exists
    if "username" in data["forward_from_chat"]:
        channel_name = data["forward_from_chat"]["username"]
    else:
        channel_name = data["forward_from_chat"]["id"]

    # Check if the file already exists
    data_path = "../data/channel_messages"
    file_path = f"{data_path}/{channel_name}.pickle"
    if os.path.exists(file_path):
        # Load messages from the existing file
        with open(file_path, "rb") as file:
            all_messages = pickle.load(file)
    else:
        # If the file does not exist, create an empty list for messages
        all_messages = {}
    message_id_offset = data["forward_from_message_id"]

    # create progress message
    progress_message = await command_message.reply(Global.response_prefix + "extracting...", quote=True)

    # extract new messages
    chat_id = data["forward_from_chat"]["id"]
    to_extract = await client.get_chat_history_count(chat_id)
    to_extract -= len(all_messages)

    start_time = time.time()
    while True:
        last_message_id = 0
        messages_before = len(all_messages)
        async for message in client.get_chat_history(chat_id, limit=100, offset_id=message_id_offset):
            all_messages[message.id] = message
            last_message_id = message.id
        message_id_offset = last_message_id
        extracted_messages = len(all_messages) - messages_before

        to_extract -= extracted_messages

        if to_extract <= 0 or extracted_messages == 0:
            break

        # update progress message
        extracted = len(all_messages)
        time_left = (time.time() - start_time) / extracted * to_extract
        await progress_message.edit(
            Global.response_prefix + f"extracting... {extracted}/{to_extract + extracted} ({time_left:.0f}s left)")

    # delete progress message
    h.delete_message_with_delay(progress_message)

    # Save the messages to the file in pickle format
    with open(file_path, "wb") as file:
        pickle.dump(all_messages, file)

    # reply to the command message with chat id and message id
    reply_message = await command_message.reply(Global.response_prefix + "messages extracted", quote=True)

    # delete the command message and the reply message
    h.delete_message_with_delay(reply_message)
    await command_message.delete()

print("Starting...")
app.run()
