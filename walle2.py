# -*- coding: utf-8 -*-

"""
Walle version 2.0
"""

from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
import logging
import logging.config
import sys
import sqlite3

logger = logging.getLogger(__name__)

BANG = "90057254"
CHUI = "119906841"
DB_NAME = "walle.db"

with open("token.key") as f:
    TOKEN = f.readline().strip()

# Define a few command handlers. These usually take the two arguments bot and
# update. Error handlers also receive the raised TelegramError object in error.
def start(bot, update):
    update.message.reply_text('Hi!')


def help(bot, update):
    update.message.reply_text('Help!')


def bookkeeper(bot, update):
    '''
    bookkeeper takes a command from account owner and
    does balance transfer betweent accounts

    'walle! pay 1000 for massage'
    chatid:-161289404 user:90057254 knightelvis
    chatid:-161289404 user:119906841 None
    '''

    parsed_cmd = _parse_payment_cmd(update.message.text)

    if not parsed_cmd:
        return
    try:
        money = int(parsed_cmd[0])
    except ValueError:
        logger.info("money is not a integer:%s" % parsed_cmd[0])
        update.message.reply_text("请输入数字：" + parsed_cmd[0])

    if len(parsed_cmd) > 1:
        reason = parsed_cmd[1]
    else:
        reason = "n/a"

    from_user = str(update.message.from_user.id)
    txn_date = update.message.date

    logger.debug('money:%s reason:%s from:%s date:%s' %
                 (money, reason, from_user, txn_date))

    if from_user == BANG:
        receiver = CHUI
    elif from_user == CHUI:
        receiver = BANG

    from_balance = _get_balance(from_user)

    if from_balance >= money:
        _write_balace(from_user, from_balance - money)
        _write_balace(receiver, _get_balance(receiver) + money)
        _log_txn(from_user, receiver, money, reason, txn_date)
        update.message.reply_text("大锤: %d 棒棒: %d" %
                                  (_get_balance(CHUI), _get_balance(BANG)))

    else:
        update.message.reply_text("Sorry, 余额不足哦！您现在余额:%s" % from_balance)


def _log_txn(from_user, to_user, money, reason, date):
    try:
        db = sqlite3.connect(DB_NAME)

        cursor = db.cursor()
        cursor.execute(
            "INSERT INTO Txn VALUES(?, ?, ?, ?, datetime('now'))",
            (from_user, to_user, money, reason))

        db.commit()
    except Exception as e:
        logger.exception("Error when saving txn to db.", e)
        raise e
    finally:
        db.close()


def _get_balance(user):
    '''
    Return an integer
    '''
    try:
        db = sqlite3.connect(DB_NAME)

        cursor = db.cursor()
        cursor.execute("SELECT balance from Balance where user = ?", (user,))
        return int(cursor.fetchone()[0])  # always single row returned
    except Exception as e:
        logger.exception("Error when getting balance from db.", e)
        raise e
    finally:
        db.close()


def _write_balace(user, new_balance):
    try:
        db = sqlite3.connect(DB_NAME)

        cursor = db.cursor()
        cursor.execute("UPDATE Balance SET balance = ? where user = ?",
                       (new_balance, user))
        db.commit()
    except Exception as e:
        logger.exception("Error when writing balance to db.", e)
        raise e
    finally:
        db.close()


def _parse_payment_cmd(msg):
    '''
    If the msg is valid command, the returned array has the money
    nominal value and the reason for payment. If not, return empty array.
    '''
    if msg and msg.startswith("walle!"):
        elements = msg.lower().strip().split()
        # filter == [x for x in elements if func(x)]
        return list(filter(None, elements))[2:]  # skip 'walle!' and 'pay'
    else:
        return []


def error(bot, update, error):
    logger.warn('Update "%s" caused error "%s"' % (update, error))


def main():

    kw = {
        'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'level': logging.INFO,
        'filename': 'walle2.log',
        # 'stream': sys.stdout,
    }

    logging.basicConfig(**kw)

    # Create the EventHandler and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # on different commands - answer in Telegram
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("help", help))
    dp.add_handler(MessageHandler(Filters.text, bookkeeper))

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()
