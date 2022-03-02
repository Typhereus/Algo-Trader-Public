import telegram_send

telegram_send.send(messages=["Wow that was easy!"])

"""
import telebot
from telethon.sync import TelegramClient
from telethon.tl.types import InputPeerUser, InputPeerChannel
from telethon import TelegramClient, sync, events

# get your api_id, api_hash, token
# from telegram as described above
api_id = 9946127
api_hash = '8c4cdb0cc1421978c3b2b7de4b733665'
token = '5079375567:AAEmR9kMmnJi0Dlc920TbHZCvbev2omwIfE'
message = "Working..."

# your phone number
phone = '18184709496'

# creating a telegram session and assigning
# it to a variable client
client = TelegramClient('session', api_id, api_hash)

# connecting and building the session
client.connect()

# in case of script ran first time it will
# ask either to input token or otp sent to
# number or sent or your telegram id
if not client.is_user_authorized():
    client.send_code_request(phone)

    # signing in the client
    client.sign_in(phone, input('Enter the code: '))


def send_message(message):

    try:
        # Get Hash

        # receiver user_id and access_hash, use
        # my user_id and access_hash for reference
        receiver = InputPeerUser('Typhereus', 'user_hash')

        # sending message using telegram client
        client.send_message(receiver, message, parse_mode='html')

    except Exception as e:
        # there may be many error coming in while like peer
        # error, wrong access_hash, flood_error, etc
        print(e)


send_message("WASSUP MFERS")

# disconnecting the telegram session
# client.disconnect()
"""