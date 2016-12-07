#!/usr/bin/env python3
# -*- coding: utf-8 -*-
#

import logging
import telegram
from time import sleep
import sys
import datetime

try:
    from urllib.error import URLError
except ImportError:
    from urllib2 import URLError  # python 2

with open("token.key") as f:
    TOKEN = f.readline().strip()

logger = logging.getLogger('wallebot')
logger.setLevel(logging.DEBUG)

ch = logging.StreamHandler(sys.stdout)
ch.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)
logger.addHandler(ch)

is_greeting = False

def main():
    # Telegram Bot Authorization Token
    bot = telegram.Bot(TOKEN)

    # get the first pending update_id, this is so we can skip over it in case
    # we get an "Unauthorized" exception.
    try:
        update_id = bot.getUpdates()[0].update_id
    except IndexError:
        update_id = None

    while True:
        try:
            update_id = echo(bot, update_id)
            logger.debug('update_id:%s', update_id)
        except telegram.TelegramError as e:
            # These are network problems with Telegram.
            if e.message in ("Bad Gateway", "Timed out"):
                sleep(1)
            elif e.message == "Unauthorized":
                # The user has removed or blocked the bot.
                update_id += 1
            else:
                raise e
        except URLError as e:
            # These are network problems on our end.
            sleep(1)


def echo(bot, update_id):
    global is_greeting

    # Request updates after the last update_id
    for update in bot.getUpdates(offset=update_id, timeout=10):
        # chat_id is required to reply to any message
        chat_id = update.message.chat_id
        from_user = update.message.from_user
        print("chatid:" + str(chat_id) +
              " user:" + str(from_user.id) +
              " " + from_user.username)

        update_id = update.update_id + 1
        message = update.message.text
        print(message)
        record(message, from_user.username)

        # response = message
        response = ""

        if(message and message.startswith("你是谁") and not is_greeting):
            response = get_one_year()
            is_greeting = True

        if response:
            # Reply to the message
            bot.sendMessage(chat_id=chat_id,
                            text=response)

    return update_id


def get_one_year():
    with open("1year.txt", "r") as f:
        mydear = f.read()

    return mydear


def record(content, sender):
    with open("content.txt", "a") as f:
        f.write(content + "#" +
                str(datetime.datetime.now()) + "#" +
                sender + "\n")


if __name__ == '__main__':
    main()
