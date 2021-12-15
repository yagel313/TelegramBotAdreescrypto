import binascii
import hashlib
import cv2
import base58
import blockcypher
import telebot
from web3 import Web3


API_KEY = '5047920924:AAGypcK1FD9MdeybJWaAkjJiyl_sXh53MDM'
bot = telebot.TeleBot(API_KEY)
infura_url = 'https://mainnet.infura.io/v3/d0f9cbea2b8a4f96a3207b553385c41f'
w3 = Web3(Web3.HTTPProvider(infura_url))


@bot.message_handler(commands=['start'])
def start(message):
    bot.send_message(message.chat.id, "Enter a bitcoin or ethereum address:")

    # check if it's bitcoin address
def get_checksum_and_hash(bitcoin_address):
    base58Decoder = base58.b58decode(bitcoin_address).hex()  # generate Byte and convert it to Hex
    prefix_and_hash = base58Decoder[:len(base58Decoder) - 8]
    checksum = base58Decoder[len(base58Decoder) - 8:]
    # to handle true result, we should pass our input to hashlib.sha256() method() as Byte format
    # so we use binascii.unhexlify() method to convert our input from Hex to Byte
    # finally, hexdigest() method convert value to human-readable
    hash_value = prefix_and_hash
    for x in range(1, 3):
        hash_value = hashlib.sha256(binascii.unhexlify(hash_value)).hexdigest()

    return checksum, hash_value


@bot.message_handler()
def echo_message(message):
    message_text = message.text
    calc_wallet_address(message, message_text)

#convert qr photo to text
def convert_qr_photo_to_text(photo):
    fileID = photo[-1].file_id
    file = bot.get_file(fileID)
    downloaded_file = bot.download_file(file.file_path)
    with open("image.jpg", 'wb') as new_file:
        new_file.write(downloaded_file)
    img = cv2.imread("image.jpg")
    addres=cv2.QRCodeDetector()
    val, pts, st_code=addres.detectAndDecode(img)
    return val



@bot.message_handler(content_types=['photo'])
def echo_message(message):
    message_text = convert_qr_photo_to_text(message.photo)
    calc_wallet_address(message, message_text)


def calc_wallet_address(message, message_text):
    # check if it's ethereum address
    if w3.isAddress(message_text):
        bot.send_message(message.chat.id, "It's ethereum address")
        if w3.isChecksumAddress(message_text):
            bot.send_message(message.chat.id, "The wallet balance is:{0}".format(w3.eth.get_balance(message_text)))
        else:
            checksum_address = w3.toChecksumAddress(message_text)
            bot.send_message(message.chat.id, "The wallet balance is:{0}".format(w3.eth.get_balance(checksum_address)))
    else:  # check if is bitcoin address
        try:
            bitcoin_address = message_text
            checksum, hash_value = get_checksum_and_hash(message_text)

            if checksum == hash_value[:8]:
                bot.send_message(message.chat.id, "It's a bitcoin address")
                bot.send_message(message.chat.id,
                                 ("the balance wallet is: {0}".format(blockcypher.get_total_balance(bitcoin_address))))
            else:
                bot.send_message(message.chat.id, "Invalid crypto wallet address!")
        except Exception as e:
            bot.send_message(message.chat.id, "Invalid crypto wallet address!")


bot.polling(none_stop=True, timeout=123)
