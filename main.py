import fcntl
import traceback
from telethon import TelegramClient
from getpass import getpass
import os
import json
import shutil


api_id = '1317311'
api_hash = '378767fb848892b60ed62a4e962787ca'
phone_number = '+251920722057'
etvnews = 1460532634

# File to store the last message IDs per channel
LAST_MESSAGE_FILE = 'last_sent_message_ids.json'
PHOTO_DOWNLOAD_PATH = "downloaded_photos"  # Folder for photos

# Ensure the folder exists
os.makedirs(PHOTO_DOWNLOAD_PATH, exist_ok=True)


client = TelegramClient('new_session', api_id, api_hash, connection_retries=5, retry_delay=1)

# async def list_channels():
#     # Connect to Telegram
#     await client.start(phone_number)

#     print("Subscribed Channels:")
#     async for dialog in client.iter_dialogs():
#         if dialog.is_channel:
#             print(f"- {dialog.name} (ID: {dialog.entity.id})")

# # Run the code
# with client:
#     client.loop.run_until_complete(list_channels())

async def scrape_channel(channel_id):
    clean_download_folder()
    print("scrapping...", channel_id)
    try:
        async for message in client.iter_messages(int(channel_id), limit=35):
            # print(message)
            if is_different_message(channel_id, message.id):
                update_last_sent_message_id(channel_id, message.id)

                if message.text:
                    edited_text = edit_message(message.text)

                    if message.photo:
                        file = await message.download_media(file=PHOTO_DOWNLOAD_PATH)
                        await client.send_file(etvnews, file, caption=edited_text)
                        print(f"Sent message with photo: {file}")
                        if os.path.exists(file):
                            os.remove(file)
                            print(f"Deleted file: {file}")
                    else:
                        await client.send_message(etvnews, edited_text)
                        print("Sent message without photo")
    except Exception as e:
        print(f"An error occurred: {e}", message)
        traceback.print_exc()

async def handle_media_message(message):
    """Handle single or grouped media messages."""
    media_group = []

    # If part of a media group (album), fetch all messages in the group
    if message.grouped_id:
        async for msg in client.iter_messages(message.chat_id, message.grouped_id):
            media_group.append(msg)
    else:
        media_group = [message]  # Single photo message

    # Download each media item into the specified folder
    downloaded_files = []
    for msg in media_group:
        file = await msg.download_media(file=PHOTO_DOWNLOAD_PATH)
        downloaded_files.append(file)

    # Send each media item and delete after sending
    for file in downloaded_files:
        edited_text = edit_message(message.text or "")
        print(f"\n\nSent message with photo: {file}")
        await client.send_file(etvnews, file, caption=edited_text)

        # Delete the photo after sending
        if os.path.exists(file):
            os.remove(file)
            print(f"Deleted file: {file}")

async def handle_media_group(channel_id, groupedId):
    media_files = []
    # print("\n media files ", media_files)
    try:
        async for msg in client.iter_messages(channel_id, groupedId):
            await print("\n\n ", client.iter_messages(channel_id, groupedId))
            # print("\n msg ", msg, "\n \n grouped id ", groupedId)
            try:
                file = await msg.download_media(file=PHOTO_DOWNLOAD_PATH)
                print("\n\n\n file   ", file)
                if file:
                    media_files.append(file)
            except Exception as download_error:
                print(f"Error downloading media: {download_error}")
                continue

        if media_files:
            print("\n\n\n\n media files        ", media_files)
            edited_text = edit_message(msg.text or "")
            print(f"Sending media group with files: {media_files}")
            await client.send_file(etvnews, media_files, caption=edited_text)

    except Exception as e:
        print(f"Error in handle_media_group: {e}")
    finally:
        # Cleanup
        for file in media_files:
            if os.path.exists(file):
                try:
                    os.remove(file)
                    print(f"Deleted file: {file}")
                except OSError as e:
                    print(f"Error deleting file {file}: {e}")

async def handle_single_media(message):
    """Handle messages with a single media."""
    file = None
    try:
        file = await message.download_media(file=PHOTO_DOWNLOAD_PATH)
        if file:
            edited_text = edit_message(message.text or "")
            print(f"Sending single media file: {file}")
            await client.send_file(etvnews, file, caption=edited_text)

    except Exception as e:
        print(f"Error in handle_single_media: {e}")
    finally:
        if file and os.path.exists(file):
            try:
                os.remove(file)
                print(f"Deleted file: {file}")
            except OSError as e:
                print(f"Error deleting file {file}: {e}")

async def send_text_message(message):
    try:
        edited_text = edit_message(message.text)
        print(f"Sending text message: {edited_text}")
        await client.send_message(etvnews, edited_text)
    except Exception as e:
        print(f"Error in send_text_message: {e}")

def edit_message(text):
    """Checks and removes specific unwanted elements from the text."""
    toBeRemoved = [
        "@tikvahethiopia", 
        "ትክክለኛዎቹን የአሐዱ ራዲዮ የማህበራዊ ሚዲያ ገጾች በመቀላቀል ቤተሰብ ይሁኑ!", 
        "ፌስቡክ: https://www.facebook.com/ahaduradio", 
        "ድረ ገጽ፡- https://ahaduradio.com/", 
        "ዩትዩብ፦ http://shorturl.at/cknFP", 
        "ቲክቶክ ፡- www.tiktok.com/@ahadutv.official", 
        "አስተያየት እና ጥቆማ ለመስጠት በ7545 አጭር የፅሁፍ መልክት ይላኩ"
    ]

    new_handle = (
        "ፈጣን መረጃዎችን ለማግኘት ትክክለኛውን የቴሌግራም ቻናላችንን ይቀላቀሉ \n"
        "https://t.me/ETVNEWS24 \n\n @etvnews24"
    )

    # Remove unwanted elements from the text
    for remove in toBeRemoved:
        text = text.replace(remove, "")

    # Clean up any extra whitespace or newlines
    cleaned_text = text.strip()

    # Append the new handle at the end
    return f"{cleaned_text}\n\n{new_handle}" if cleaned_text else new_handle


def is_different_message(channel_id, new_message_id):
    """Check if the message is different from the last one sent."""
    if os.path.exists(LAST_MESSAGE_FILE):
        with open(LAST_MESSAGE_FILE, 'r') as f:
            last_message_data = json.load(f)
            last_message_list = last_message_data.get(str(channel_id))

            # print(f"\n channel_id {channel_id} (last_message_id list: {last_message_list})")
            if last_message_list:
                return new_message_id not in last_message_list
        
    return True  # If no record exists, treat it as a different message

def update_last_sent_message_id(channel_id, message_id):
    """Update the last sent message ID for a given channel."""
    if os.path.exists(LAST_MESSAGE_FILE):
        with open(LAST_MESSAGE_FILE, 'r') as f:
            last_message_data = json.load(f)
    else:
        last_message_data = {}
    print ("channel id - ", channel_id, "\n mssage id - ", message_id)

    # Ensure the channel ID exists as a key in the dictionary
    if str(channel_id) not in last_message_data:
        last_message_data[str(channel_id)] = []

    last_message_data[str(channel_id)].append(message_id)
    if len(last_message_data[str(channel_id)]) > 75 :
        last_message_data[str(channel_id)].pop(0)

    # print("\n\n\n\n the arrays length:: ", channel_id ," - ", len(last_message_data[str(channel_id)]), "\n")

    with open(LAST_MESSAGE_FILE, 'w') as f:
        json.dump(last_message_data, f)

def acquire_lock():
    lock_file = open("bot.lock", "w")
    try:
        fcntl.lockf(lock_file, fcntl.LOCK_EX | fcntl.LOCK_NB)
        return lock_file
    except IOError:
        return None
        

async def main():
    addisWalta = 1151106565
    ahadu = 1292605662
    channels = [1130580549, 1236564438, 1151106565, 1292605662]  # Add your channel IDs here

    # lock = acquire_lock()
    # if not lock:
    #     print("Another instance is running")
    #     return
    try:
        for channel_id in channels:
            channel_id = int(channel_id)
            await scrape_channel(channel_id)
        
    finally:
        # lock.close()
        # os.remove("bot.lock")
        print("")

def clean_download_folder():
    if os.path.exists(PHOTO_DOWNLOAD_PATH):
        shutil.rmtree(PHOTO_DOWNLOAD_PATH)
    os.makedirs(PHOTO_DOWNLOAD_PATH)

clean_download_folder()

with client:
            client.loop.run_until_complete(main())