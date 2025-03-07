import fcntl
import re
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
# workTalkinPupose = 1579506507
send_to_chat = etvnews

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

MAX_CAPTION_LENGTH = 1024  # Telegram's typical caption limit

async def scrape_channel(channel_id):
    clean_download_folder()
    print("scrapping...", channel_id)
    try:
        async for message in client.iter_messages(int(channel_id), limit=35):
            if is_different_message(channel_id, message.id):
                update_last_sent_message_id(channel_id, message.id)

                if message.text:
                    edited_text = edit_message(message.text)
                    
                    # Check if the message includes a photo
                    if message.photo:
                        # If the message is part of a media group (album)
                        if message.grouped_id:
                            album_messages = []
                            # Gather all messages in the album
                            async for m in client.iter_messages(int(channel_id), limit=35):
                                if m.grouped_id == message.grouped_id:
                                    album_messages.append(m)
                            album_messages = sorted(album_messages, key=lambda m: m.id)
                            
                            files = []
                            for m in album_messages:
                                if m.photo:
                                    file = await m.download_media(file=PHOTO_DOWNLOAD_PATH)
                                    files.append(file)
                            
                            # Decide whether to use caption with media or separate reply based on length
                            if len(edited_text) > MAX_CAPTION_LENGTH:
                                sent_album = await client.send_file(send_to_chat, files, caption="")
                                await client.send_message(send_to_chat, edited_text, reply_to=sent_album[0].id)
                                print(f"Sent album with {len(files)} photos and separate caption reply.")
                            else:
                                await client.send_file(send_to_chat, files, caption=edited_text)
                                print(f"Sent album with {len(files)} photos and caption.")
                        else:
                            # Single photo case
                            file = await message.download_media(file=PHOTO_DOWNLOAD_PATH)
                            if len(edited_text) > MAX_CAPTION_LENGTH:
                                sent_photo = await client.send_file(send_to_chat, file, caption="")
                                await client.send_message(send_to_chat, edited_text, reply_to=sent_photo.id)
                                print(f"Sent single photo and separate caption reply.")
                            else:
                                await client.send_file(send_to_chat, file, caption=edited_text)
                                print(f"Sent single photo with caption.")
                    else:
                        # No photo, just send the text message normally
                        await client.send_message(send_to_chat, edited_text)
                        
    except Exception as e:
        print(f"An error occurred: {e}", message)
        traceback.print_exc()



def edit_message(text):
    """Removes specific unwanted elements and appends a new handle."""
    # Map of unwanted substrings to their replacements.
    # If the value is an empty string, it simply removes the substring.
    removals = {
        "@tikvahethiopia": "",
        "ትክክለኛዎቹን የአሐዱ ራዲዮ የማህበራዊ ሚዲያ ገጾች በመቀላቀል ቤተሰብ ይሁኑ!": "",
        "ፌስቡክ: https://www.facebook.com/ahaduradio": "",
        "ድረ ገጽ፡- https://ahaduradio.com/": "",
        "ዩትዩብ፦ http://shorturl.at/cknFP": "",
        "ቲክቶክ ፡- www.tiktok.com/@ahadutv.official": "",
        "ዋትስአፕ፦ whatsapp.com/channel/0029VajDfVZI1rcb05C5B22b": "",
        "አስተያየት እና ጥቆማ ለመስጠት በ7545 አጭር የፅሁፍ መልክት ይላኩ": "",
        "#አሐዱ_መድረክ": "",
        "#አሐዱ_የኢትዮጵያውያን_ድምጽ": "",
        "አሐዱ ሬዲዮ": "ኢቲቪ ዜና",
        "ኤፍ ኤም ሲ": "ኢቲቪ ዜና",
        "ቲክቫህ ኢትዮጵያ": "ኢቲቪ ዜና",
    }
    
    # Create a combined regex pattern by escaping each key and joining with '|'
    pattern = '|'.join(map(re.escape, removals.keys()))
    # Replace each unwanted substring with its corresponding replacement
    # This single call scans the text and substitutes any matching substring.
    text = re.sub(pattern, lambda m: removals[m.group(0)], text)
    
    # Remove custom words (like #TikvahEthiopiaFamily variants)
    text = remove_custom_words(text)
    
    # Clean up extra whitespace/newlines
    cleaned_text = text.strip()
    
    new_handle = (
        "**ፈጣን መረጃዎችን ለማግኘት ትክክለኛውን የቴሌግራም ቻናላችንን ይቀላቀሉ** \n"
        "**https://t.me/ETVNEWS24** \n\n @etvnews24"
    )
    
    return f"{cleaned_text}\n\n{new_handle}" if cleaned_text else new_handle


def remove_custom_words(text):
    # Combine all patterns into a single regular expression
    combined_pattern = r'#TikvahEthiopiaFamily\w*|anotherPattern|yetAnotherPattern'
    # Use re.sub to replace all patterns with an empty string
    cleaned_text = re.sub(combined_pattern, '', text)
    return cleaned_text

    
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
    # addisWalta = 1151106565
    ahadu = 1292605662
    
    channels = [1130580549, 1236564438, ahadu]  # Add your channel IDs here

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