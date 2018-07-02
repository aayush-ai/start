

#### SQLITE BRANCH ####
import sys
import sqlite3

def loadDB():
    # Creates SQLite database to store info.
    conn = sqlite3.connect('game5.sqlite', timeout=10)
    cur = conn.cursor()
    conn.text_factory = str
    cur.executescript('''CREATE TABLE IF NOT EXISTS userdata
    (
    id INTEGER PRIMARY KEY UNIQUE,
    firstname TEXT,
    email TEXT UNIQUE,
    total_balance INTEGER DEFAULT 100,
    twr1_pick TEXT,
    twr1_stake INTEGER DEFAULT 0,
    twr2_pick TEXT,
    twr2_stake INTEGER DEFAULT 0,
    twr3_pick TEXT,
    twr3_stake INTEGER DEFAULT 0,
    twr3_feed TEXT,
    twr3_feed_token INTEGER DEFAULT 0,
    gk1_pick TEXT,
    gk1_token INTEGER DEFAULT 0,
    twr4_pick TEXT,
    twr4_stake INTEGER DEFAULT 0,
    twr4_feed TEXT,
    twr4_feed_token INTEGER DEFAULT 0,
    verify1_text TEXT,
    verify1_token INTEGER DEFAULT 0,
    twr5_pick TEXT,
    twr5_stake INTEGER DEFAULT 0,
    twr5_feed TEXT,
    twr5_feed_token INTEGER DEFAULT 0,
    gk2_pick TEXT,
    gk2_token INTEGER DEFAULT 0,
    twr6_pick TEXT,
    twr6_stake INTEGER DEFAULT 0,
    gk3_pick TEXT,
    gk3_token INTEGER DEFAULT 0,
    twr7_pick TEXT,
    twr7_stake INTEGER DEFAULT 0,
    feed_pick TEXT,
    priv_pick TEXT,
    frnd_email TEXT,
    feed_text TEXT);'''
    )
    #cur.execute("ALTER TABLE userdata ADD COLUMN qs_index int(32)")


    conn.commit()
    conn.close()

def checkUser(update, user_data):
    # Checks if user has visited the bot before
    # If yes, load data of user
    # If no, then create a new entry in database
    conn = sqlite3.connect('game5.sqlite')
    cur = conn.cursor()
    conn.text_factory = str
    if len(cur.execute('''SELECT id FROM userdata WHERE id = ?
            ''', (update.message.from_user.id,)).fetchall())>0:
        c=cur.execute('''SELECT firstname FROM userdata WHERE id = ?''', (update.message.from_user.id,)).fetchone()
        user_data['firstname']=c[0]
        c=cur.execute('''SELECT email FROM userdata WHERE id = ?''', (update.message.from_user.id,)).fetchone()
        user_data['email']=c[0]
        c=cur.execute('''SELECT twr1_pick FROM userdata WHERE id = ?''', (update.message.from_user.id,)).fetchone()
        user_data['twr1_pick']=c[0]
        c=cur.execute('''SELECT twr1_stake FROM userdata WHERE id = ?''', (update.message.from_user.id,)).fetchone()
        user_data['twr1_stake']=c[0]
        c=cur.execute('''SELECT twr2_pick FROM userdata WHERE id = ?''', (update.message.from_user.id,)).fetchone()
        user_data['twr2_pick']=c[0]
        c=cur.execute('''SELECT twr2_stake FROM userdata WHERE id = ?''', (update.message.from_user.id,)).fetchone()
        user_data['twr2_stake']=c[0]
        c=cur.execute('''SELECT twr3_pick FROM userdata WHERE id = ?''', (update.message.from_user.id,)).fetchone()
        user_data['twr3_pick']=c[0]
        c=cur.execute('''SELECT twr3_stake FROM userdata WHERE id = ?''', (update.message.from_user.id,)).fetchone()
        user_data['twr3_stake']=c[0]
        c=cur.execute('''SELECT total_balance FROM userdata WHERE id = ?''', (update.message.from_user.id,)).fetchone()
        user_data['total_balance']=c[0]
        print('Past user')

    else:
        cur.execute('''INSERT OR IGNORE INTO userdata (id, firstname) VALUES (?, ?)''', \
        (update.message.from_user.id, update.message.from_user.first_name,))

        print('New user')
    conn.commit()
    conn.close()

def updateUser(category, text, update):
    # Updates user info as inputted.
    conn = sqlite3.connect('game5.sqlite')
    cur = conn.cursor()
    conn.text_factory = str
    # Update SQLite database as needed.
    cur.execute('''UPDATE OR IGNORE userdata SET {} = ? WHERE id = ?'''.format(category), \
        (text, update.effective_message.from_user.id,))
    conn.commit()
    conn.close()


#### Python Telegram Bot Branch ####

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton,Message, Chat, Update, Bot, User
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, RegexHandler, MessageHandler, Filters, ConversationHandler
import logging

twr_game_questions= ['TWR 1: Which project is more innovative?',
    'TWR 2: Which project is more likely to execute its vision? ',
    'TWR 3: Which project appears more credible?',
    'TWR 4: Which project is more innovative?',
    'TWR 5: Which project is more likely to execute its vision?',
    'TWR 6: Which project appears more credible?',
    'TWR 7: Which project is more likely to execute its vision?']

twr_game_photos = ['https://docs.google.com/drawings/d/e/2PACX-1vQX1mRsidYvG_yX6xxKziZpl9I6aOv69dJ_zoKKfaBWqOuLQabTwWnogidWCxox-CVIKeg2R6Pv8OlL/pub?w=960&h=720',
    'https://docs.google.com/drawings/d/e/2PACX-1vS-9DriXrKG7eX1P7UPeMQq-K7hqP8FmrhrO13QodCcD4-xu8IgJ_eBJieEobta3FYbCuBXRAWiQkjm/pub?w=960&h=720',
    'https://docs.google.com/drawings/d/e/2PACX-1vT5r7zia0xewHls11ET4u9OSmErWKwDn1PNJwX_YwowawI0xRn391LxdQSCI1UG6rB2JCUSQKBqJz5Y/pub?w=960&h=720',
    'https://docs.google.com/drawings/d/e/2PACX-1vQ8wUF0CNqgQv6TSXHKYRupOAP1Hm5TkLgtAsQEjrH-Dymwir7biqEuMEBJmEpDxYg6DpVri-hTrtAW/pub?w=960&h=720',
    'https://docs.google.com/drawings/d/e/2PACX-1vTm7BAwz2uJdyToHDqzBGz7ahjlz-0A-f5piFTtuxIy5YCgSgBfSYYgVOuVwnaNQ58qEIJHVsuv1J0l/pub?w=960&h=720',
    'https://docs.google.com/drawings/d/e/2PACX-1vSkfxq6n5bFI6iNgFgjMBwPira45A-sZA-krBPBkn4utUxwnUnOlPME2R3cvzRJBh9wA2KzRzva45o5/pub?w=960&h=720',
    'https://docs.google.com/drawings/d/e/2PACX-1vTOlb_Z7P2heP5_BGvPzykQgUPmxLxW9b54oFmXWBFfZ94QF5J87Z2tEbezyPFneEWhMOQkq1CJM43r/pub?w=960&h=720']

#gk_qs = []


# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)




markup = ReplyKeyboardMarkup([['Enter Email Address'],['Check Token Balance'],
                  ['End Game and Submit']], one_time_keyboard=True)
markup1 = ReplyKeyboardMarkup([['How to Play'],['Start the Game']], one_time_keyboard=True)


def start(bot, update, user_data):

    checkUser(update, user_data)
    #if checkUser(update, user_data) == "New User":
    update.message.reply_text("Hola Cypherpunk!\nEnter your email ID to receive your playing balance:")




    #else:
        #update.message.reply_text("Welcome back, {}!\nAre you ready for another round?".format(update.effective_user.first_name),reply_markup=markup1)
        #return CHOOSING_INLINE


def email(bot, update, user_data):

    text = update.message.text
    category = 'email'
    user_data[category] = text
    updateUser(category, text, update)
    update.message.reply_text("Okay, you now have 100 startereum tokens to play with.\n\nIf you have already been allocated startereums in the past, these will be credited to your account after a delay.\n\nYou will receive an update on your email: "
                              "{}".format(text), reply_markup=markup1)




def how_play(bot,update, user_data):

    text = update.message.text
    if text == 'How to Play':
        update.message.reply_text(text= "{}, let's review the basics. Hit start when done!".format(update.effective_user.first_name),reply_markup=markup1)
        bot.sendDocument(chat_id=update.effective_message.chat_id, document='https://media.giphy.com/media/2Yc0g11QsZ7vqxmzTn/giphy.gif')


def twr_start(bot, update, user_data):

    global twr_game_questions
    global twr_game_photos
    reply_markup_twr = InlineKeyboardMarkup([[InlineKeyboardButton("Project A", callback_data='Project A'),InlineKeyboardButton("Project B", callback_data='Project B')]])

    if user_data['twr1_pick'] == None:
        text = twr_game_questions[0]
        photo = twr_game_photos[0]
        update.message.reply_text(text=text, reply_markup=reply_markup_twr)
        bot.send_photo(update.effective_message.chat_id, photo=photo)


    elif user_data ['twr2_pick'] == None:
        text = twr_game_questions[1]
        photo = twr_game_photos[1]
        update.message.reply_text(text=text, reply_markup=reply_markup_twr)
        bot.send_photo(update.effective_message.chat_id, photo=photo)

    elif user_data ['twr3_pick'] == None:
        text = twr_game_questions[2]
        photo = twr_game_photos[2]
        update.message.reply_text(text=text, reply_markup=reply_markup_twr)
        bot.send_photo(update.effective_message.chat_id, photo=photo)


def twr_pick(bot, update, user_data):

    markup2= ReplyKeyboardMarkup([[str(i) for i in range(6 * j + 3, 6 * j + 9)] for j in range(3)], one_time_keyboard=True)


    if user_data['twr1_pick'] == None:
        text = str(update.callback_query.data)
        category = 'twr1_pick'
        user_data[category] = text
        updateUser(category, text, update)
        update.callback_query.message.reply_text(text="Token Left: " + str(user_data['total_balance']) + "\n Please stake tokens for {}".format(text), reply_markup=markup2)

        del user_data['twr1_pick']

    elif user_data['twr2_pick'] == None:
        value = update.callback_query.data
        category = 'twr2_pick'
        user_data[category] = value
        updateUserCallback(category, value, update)
        update.callback_query.message.reply_text(text="Token Left: " + str(user_data['total_balance']) + "\n Please stake tokens for {}".format(value), reply_markup=markup2)


    elif user_data['twr3_pick'] == None:
        value = update.callback_query.data
        category = 'twr3_pick'
        user_data[category] = value
        updateUserCallback(category, value, update)
        update.callback_query.message.reply_text(text="Token Left: " + str(user_data['total_balance']) + "\n Please stake tokens for {}".format(value), reply_markup=markup2)






def twr_stake(bot, update, user_data):

    text = update.message.text

    if user_data['twr1_stake'] == 0:

        category = 'twr1_stake'
        user_data['twr1_stake'] = text
        updateUser(category, text, update)
        total = int(user_data['total_balance'])
        last_stake = int(text)
        text = total - last_stake
        category = 'total_balance'
        user_data['total_balance'] = text
        updateUser(category, text, update)
        twr_start(bot, update, user_data)



    elif user_data['twr2_stake'] == 0:

        category = 'twr2_stake'
        user_data['twr2_stake'] = text
        updateUser(category, text, update)
        total = int(user_data['total_balance'])
        last_stake = int(text)
        text = total - last_stake
        category = 'total_balance'
        user_data['total_balance'] = text
        updateUser(category, text, update)
        twr_start(bot, update, user_data)

    elif user_data['twr3_stake'] == 0:

        category = 'twr3_stake'
        user_data['twr3_stake'] = text
        updateUser(category, text, update)
        total = int(user_data['total_balance'])
        last_stake = int(text)
        text = total - last_stake
        category = 'total_balance'
        user_data['total_balance'] = text
        updateUser(category, text, update)
        twr_start(bot, update, user_data)

    return twr_start(bot, update, user_data)


#twr_games



def regular_choice(bot, update, user_data):
    text = update.message.text
    update.message.reply_text('Your {}? Yes, I would love to hear about that!'.format(text.lower()))

#has entered
#def received_information(bot, update, user_data):
    #text = update.message.text
    #category = user_data['email']
    #user_data[category] = text
    #updateUser(category, text, update)
    #del user_data['email']

    #update.message.reply_text("Neat! Just so you know, this is what you already told me:"
                             # "{}"
                              #"You can tell me more, or change your opinion on something.".format(
                                #  facts_to_str(user_data)), reply_markup=markup)
    #return CHOOSING


def done(bot, update, user_data):
    if 'email' in user_data:
        del user_data['email']

    update.message.reply_text("I learned these facts about you:"
                              "{}"
                              "Until next time!".format(facts_to_str(user_data)))

    user_data.clear()


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater("604744099:AAHImp03yylJO8Qjod3bfhEw5AmmV2fDK4w")
    print("Connection to Telegram established; starting bot.")
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler with the states GENDER, PHOTO, LOCATION and BIO

    dp.add_handler(CommandHandler('start', start, pass_user_data=True))
    dp.add_handler(RegexHandler('(\w+[.|\w])*@(\w+[.])*\w+', email, pass_user_data=True))

    dp.add_handler(CallbackQueryHandler(twr_pick, pattern=r"Project"))

    dp.add_handler(RegexHandler('^[1-2]?[0-9]$|^2[0]$', twr_stake, pass_user_data=True))
    dp.add_handler(RegexHandler('^Start the Game$', twr_start, pass_user_data=True))
    dp.add_handler(RegexHandler('^How to Play$', how_play, pass_user_data=True))



    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()

if __name__ == '__main__':
    ### load SQLite databasse ###
    loadDB()
    main()
