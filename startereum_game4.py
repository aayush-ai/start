#!/usr/bin/env python
#attempt 1: serverless lambda, and dynamodb: issues with webhook and telegram api
#attempt 2: ec2 and sqlite: issues with concurrent calls and dB locks
#attemp 3: moving to PostGres
#this file represents a full game set:
#### SQLITE BRANCH ####
import sys
import sqlite3

def loadDB():
    # Creates SQLite database to store info.
    conn = sqlite3.connect('startereum_master.sqlite', timeout=10)
    cur = conn.cursor()
    conn.text_factory = str
    # 3 tables: userdata, match_matches, feedback_games, 
    cur.executescript('''CREATE TABLE IF NOT EXISTS userdata
    (
    id INTEGER PRIMARY KEY UNIQUE,
    username TEXT,
    firstname TEXT,
    email TEXT UNIQUE);'''
    
    cur.executescript('''CREATE TABLE IF NOT EXISTS wave_4_twr
    (
    email PRIMARY KEY UNIQUE,
    total_balance INTEGER DEFAULT 100,
    match1_pick TEXT,
    match1_stake INTEGER DEFAULT 0,
    match2_pick TEXT,
    match2_stake INTEGER DEFAULT 0,
    match3_pick TEXT,
    match3_stake INTEGER DEFAULT 0,
    match4_pick TEXT,
    match4_stake INTEGER DEFAULT 0,
    match5_pick TEXT,
    match5_stake INTEGER DEFAULT 0,
    match6_pick TEXT,
    match6_stake INTEGER DEFAULT 0,
    match7_pick TEXT,
    match7_stake INTEGER DEFAULT 0);'''
    
    cur.executescript('''CREATE TABLE IF NOT EXISTS wave_5_feedback
    (
    id INTEGER PRIMARY KEY UNIQUE,
    email TEXT UNIQUE,
    match3_feed TEXT,
    match3_feed_token INTEGER DEFAULT 0,
    gk1_pick TEXT,
    gk1_token INTEGER DEFAULT 0,
    match4_feed TEXT,
    match4_feed_token INTEGER DEFAULT 0,
    verify1_text TEXT,
    verify1_token INTEGER DEFAULT 0,
    match5_feed TEXT,
    match5_feed_token INTEGER DEFAULT 0,
    gk2_pick TEXT,
    gk2_token INTEGER DEFAULT 0,
    gk3_pick TEXT,
    gk3_token INTEGER DEFAULT 0,
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
    conn = sqlite3.connect('startereum_master.sqlite')
    cur = conn.cursor()
    conn.text_factory = str

    if len(cur.execute('''SELECT id FROM userdata WHERE id = ?
            ''', (update.effective_message.from_user.id,)).fetchall())>0:
        #this loads the relevant columns in a list # impliment a better DRY loop
        c=cur.execute('''SELECT firstname, email username FROM userdata WHERE id = ?''', 
        (update.effective_message.from_user.id,)).fetchone()
        user_data['firstname','email', 'username']=c[0]

        c=cur.execute('''SELECT match1_pick, match2_pick, match3_pick, match4_pick, match5_pick, match6_pick, match7_pick
        FROM wave_4_twr WHERE id = ?''', (update.effective_message.from_user.id,)).fetchone() 
        wave4_twr_pick['match1_pick','match2_pick','match3_pick','match4_pick','match5_pick','match6_pick','match7_pick']=c[0]

        c=cur.execute('''SELECT match1_stake, match2_stake, match3_pick, match3_stake, match4_pick, match4_stake, match5_pick, match5_stake, match6_pick, match6_stake, match7_pick, match7_stake, total_balance
        FROM wave_4_twr WHERE id = ?''', (update.effective_message.from_user.id,)).fetchone() 
        wave4_twr_stake[, 'match1_stake','match2_stake','match3_stake','match4_stake','match5_stake','match6_stake','match7_stake','total_balance']=c[0]

        c=cur.execute('''SELECT match3_feed, match3_feed_token, gk1_pick, gk1_token, match4_feed, match4_feed_token, verify1_text, verify1_token, match5_feed, match5_feed_token, gk2_pick, gk2_token, gk3_pick, gk3_token, feed_pick, priv_pick, frnd_email, feed_text
        FROM wave_4_feedback WHERE id = ?''', (update.effective_message.from_user.id,)).fetchone()
        wave4_feedback['match3_feed', 'match3_feed_token', 'gk1_pick', 'gk1_token', 'match4_feed', 'match4_feed_token', 'verify1_text', 'verify1_token', 'match5_feed', 'match5_feed_token','gk2_pick','gk2_token','gk3_pick', 'gk3_token','feed_pick', 'priv_pick','frnd_email','feed_text']=c[0]

        print('Returning user')

    else:
        cur.execute('''INSERT OR IGNORE INTO userdata (id, firstname, username) VALUES (?, ?)''', \
        (update.effective_message.from_user.id, update.effective_message.from_user.username, update.effective_message.from_user.first_name,))

        print('New user')
        
    conn.commit()
    conn.close()

def updateUser(category, text, update):
    # Updates user info as inputted.
    conn = sqlite3.connect('startereum_master.sqlite')
    cur = conn.cursor()
    conn.text_factory = str
    # Update SQLite database as needed.
    cur.execute('''UPDATE OR IGNORE userdata SET {} = ? WHERE id = ?'''.format(category), \
        (text, update.effective_message.from_user.id,))
    print (category, text)
    conn.commit()
    conn.close()

def update_twr(category, text, update):
    # Updates user info as inputted.
    conn = sqlite3.connect('startereum_master.sqlite')
    cur = conn.cursor()
    conn.text_factory = str
    # Update SQLite database as needed.
    cur.execute('''UPDATE OR IGNORE wave_4_twr SET {} = ? WHERE id = ?'''.format(category), \
        (text, update.effective_message.from_user.id,))
    print (category, text)
    conn.commit()
    conn.close()
    
def update_feedback(category, text, update):
    # Updates user info as inputted.
    conn = sqlite3.connect('startereum_master.sqlite')
    cur = conn.cursor()
    conn.text_factory = str
    # Update SQLite database as needed.
    cur.execute('''UPDATE OR IGNORE wave_4_feeback SET {} = ? WHERE id = ?'''.format(category), \
        (text, update.effective_message.from_user.id,))
    print (category, text)
    conn.commit()
    conn.close()


#### Python Telegram Bot Branch ####

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton,Message, Chat, Update, Bot, User
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, RegexHandler, MessageHandler, Filters, ConversationHandler
import logging
import re
## declare all the list of all games in a game set.
match_game_questions= ['match 1: Which project is more innovative?',
    'match 2: Which project is more likely to execute its vision? ',
    'match 3: Which project appears more credible?',
    'match 4: Which project is more innovative?',
    'match 5: Which project is more likely to execute its vision?',
    'match 6: Which project appears more credible?',
    'match 7: Which project is more likely to execute its vision?']

match_game_photos = ['https://docs.google.com/drawings/d/e/2PACX-1vQX1mRsidYvG_yX6xxKziZpl9I6aOv69dJ_zoKKfaBWqOuLQabTwWnogidWCxox-CVIKeg2R6Pv8OlL/pub?w=960&h=720',
    'https://docs.google.com/drawings/d/e/2PACX-1vS-9DriXrKG7eX1P7UPeMQq-K7hqP8FmrhrO13QodCcD4-xu8IgJ_eBJieEobta3FYbCuBXRAWiQkjm/pub?w=960&h=720',
    'https://docs.google.com/drawings/d/e/2PACX-1vT5r7zia0xewHls11ET4u9OSmErWKwDn1PNJwX_YwowawI0xRn391LxdQSCI1UG6rB2JCUSQKBqJz5Y/pub?w=960&h=720',
    'https://docs.google.com/drawings/d/e/2PACX-1vQ8wUF0CNqgQv6TSXHKYRupOAP1Hm5TkLgtAsQEjrH-Dymwir7biqEuMEBJmEpDxYg6DpVri-hTrtAW/pub?w=960&h=720',
    'https://docs.google.com/drawings/d/e/2PACX-1vTm7BAwz2uJdyToHDqzBGz7ahjlz-0A-f5piFTtuxIy5YCgSgBfSYYgVOuVwnaNQ58qEIJHVsuv1J0l/pub?w=960&h=720',
    'https://docs.google.com/drawings/d/e/2PACX-1vSkfxq6n5bFI6iNgFgjMBwPira45A-sZA-krBPBkn4utUxwnUnOlPME2R3cvzRJBh9wA2KzRzva45o5/pub?w=960&h=720',
    'https://docs.google.com/drawings/d/e/2PACX-1vTOlb_Z7P2heP5_BGvPzykQgUPmxLxW9b54oFmXWBFfZ94QF5J87Z2tEbezyPFneEWhMOQkq1CJM43r/pub?w=960&h=720']

gk_qs = ['To win a 2 token bonus, select the right answer to the question: What is sharding?\n\nA: It is not polite.\nB: Splitting a blockchain into pieces.\nC: Failing to record a state change.\nD: Betting against a cryptoasset.', 
'To win a 2 token bonus, select the right answer to the question: What is segwit?\n\nA: Birth of Bitcoin Talk.\nB: Decrease in mining reward.\nC: Scooters on blockchain.\n D: A way to increase block size.', 
'To win a 2 token bonus, select the right option to complete the sentence: Critics say the problem with Delegated Proof of Stake (DPoS) is that\n\nA: It uses too much energy.\nB: It has low transaction frequency.\nC: It is prone to corruption.\nD: It is non-falsifiable.']

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

#global keyboards




feedback_markup =

#there are three types of games in this set match, GK, Feedback. match  & GK emits a callback_query,
#while feedback and tokens are keyboard inputs.  

def start(bot, update, user_data):

#this is the primary body of the game content
    markup_main = ReplyKeyboardMarkup([['How to Play'],['Start the Game'], ['Start the Game']], one_time_keyboard=True)
    if  == "New User":
        update.effective_message.reply_text("Hola Cypherpunk!\nEnter your email ID to receive your playing balance:")

    elif update.effective_message.reply_text("Welcome back, {}!\nAre you ready for another go?".format(update.effective_user.first_name),reply_markup=markup_main)

def email(bot, update, user_data):
    markup_main = ReplyKeyboardMarkup([['How to Play'],['Start the Game'], ['Start the Game']], one_time_keyboard=True)
    text = update.effective.text
    category = 'email'
    user_data[category] = text
    updateUser(category, text, update)
    update.effective_message.reply_text("Okay, you now have 100 startereum tokens to play with.\n\nIf you have already been allocated startereums in the past, these will be credited to your account after a delay.\n\nYou will receive an update on your email: ",reply_markup=markup_main)

def how_play(bot,update, user_data):
    markup_main = ReplyKeyboardMarkup([['How to Play'],['Start the Game'], ['Start the Game']], one_time_keyboard=True)
    text = update.effective_message.text
    if text == 'How to Play':
        update.effective_message.reply_text(text= "{}, let's review the basics. Hit start when done!".format(update.effective_user.first_name),reply_markup=markup_main)
        bot.sendDocument(chat_id=update.effective_message.chat_id, document='https://media.giphy.com/media/2Yc0g11QsZ7vqxmzTn/giphy.gif')
        
#game loop starts here:

def match_start(bot, update, user_data):

    global match_game_questions
    global match_game_photos
    reply_markup_match = InlineKeyboardMarkup([[InlineKeyboardButton("Project A", callback_data='Project A'),InlineKeyboardButton("Project B", callback_data='Project B')]])
    markup2= ReplyKeyboardMarkup([[str(i) for i in range(6 * j + 3, 6 * j + 9)] for j in range(3)], one_time_keyboard=True)
    checkUser(update, wave4_twr, wave4_feedback)
    
    if wave4_twr['match1_pick'] == None:
        text = match_game_questions[0]
        photo = match_game_photos[0]
        update.effective_message.reply_text(text=text, reply_markup=reply_markup_match)
        bot.send_photo(update.effective_message.chat_id, photo=photo)
    elif wave4_twr['match2_pick'] == None:
        text = match_game_questions[1]
        photo = match_game_photos[1]
        update.effective_message.reply_text(text=text, reply_markup=reply_markup_match)
        bot.send_photo(update.effective_message.chat_id, photo=photo)
    elif wave4_twr['match3_pick'] == None:
        text = match_game_questions[2]
        photo = match_game_photos[2]
        update.effective_message.reply_text(text=text, reply_markup=reply_markup_match)
        bot.send_photo(update.effective_message.chat_id, photo=photo)
    elif wave4_twr_feeback['match3_feed'] == None:
        
    elif wave4_twr_feedback['gk1_pick'] == None:

    elif wave4_twr['match4_pick'] == None:
        text = match_game_questions[3]
        photo = match_game_photos[3]
        update.effective_message.reply_text(text=text, reply_markup=reply_markup_match)
        bot.send_photo(update.effective_message.chat_id, photo=photo)

    elif wave4_twr['match4_stake'] == None:

    elif wave4_twr_feedback['match4_feed'] == None:

    elif wave4_twr_feedback['verify1_text'] == None:

    elif wave4_twr['match5_pick'] == None:
        text = match_game_questions[3]
        photo = match_game_photos[3]
        update.effective_message.reply_text(text=text, reply_markup=reply_markup_match)
        bot.send_photo(update.effective_message.chat_id, photo=photo)

    elif wave4_twr['match5_stake'] == None:

    elif wave4_twr_feedback['match5_feed'] == None:

    elif wave4_twr_feedback['gk2_pick'] == None:

    elif wave4_twr_feedback['match6_pick'] == None:
        text = match_game_questions[3]
        photo = match_game_photos[3]
        update.effective_message.reply_text(text=text, reply_markup=reply_markup_match)
        bot.send_photo(update.effective_message.chat_id, photo=photo)

    elif wave4_twr_feedback['match6_stake'] == None:

    elif wave4_twr_feedback['gk3_pick'] == None:

    elif wave4_twr['match7_pick'] == None:
        text = match_game_questions[3]
        photo = match_game_photos[3]
        update.effective_message.reply_text(text=text, reply_markup=reply_markup_match)
        bot.send_photo(update.effective_message.chat_id, photo=photo)

    elif wave4_twr['match7_stake'] == None:

    elif wave4_twr_feedback['feed_pick'] == None:

    elif wave4_twr_feedback['priv_pick'] == None:

    elif wave4_twr_feedback['frnd_email'] == None:

    elif wave4_twr_feedback['feed_text'] == None:

def match_pick(bot, update, wave4_twr):
    text = update.callback_query.data
    if text == '^Project$':
        markup2= ReplyKeyboardMarkup([[str(i) for i in range(6 * j + 3, 6 * j + 9)] for j in range(3)], one_time_keyboard=True)
        checkUser(update, wave4_twr_pick)
        for i in range[6]:
            if wave4_twr_pick[i] == None: 
                text = str(update.callback_query.data)
                category = wave4_twr[i]
                update_twr(category, text, update)
                update.callback_query.message.reply_text(text="Token Left: " + str(user_data['total_balance']) + "\n Please stake tokens for {}".format(text), reply_markup=markup2)
                match_start(bot, update, user_data)
    else text == '^Option$':
        mcq_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Option A", callback_data='Option A'),InlineKeyboardButton("Project B", callback_data='Project B')]])

#REGEX_HANDLERS             
#for token_stake
def match_stake(bot, update, wave4_twr_stake):
    
    checkUser(update, wave4_twr_stake)
    text = update.message.text
    for i in range[6]:
        if wave4_twr_stake[i] == 0:
            category = 'wave4_twr_stake[i]''
        wave4_twr_stake[category] = text
        updateUser(category, text, update)
        
    #balance update
        total = int(wave4_twr_stake['total_balance'])
        last_stake = int(text)
        text = total - last_stake
        category = 'total_balance'
        user_data['total_balance'] = text
        updateUser(category, text, update)
        match_start(bot, update, wave4_twr_stake)


def feedback_handler (bot, update):
    checkUser(update, wave4_feedback)

def gk_handler(bot, update):
    



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
    updater = Updater("TELEGRAM_TOKEN")
    print("Connection to Telegram established; starting bot.")
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start, pass_user_data=True))
    dp.add_handler(RegexHandler('(\w+[.|\w])*@(\w+[.])*\w+', email, pass_user_data=True))
    dp.add_handler(CallbackQueryHandler(match_pick, pattern=r"Project"))
    dp.add_handler(CallbackQueryHandler('^[1-2]?[3-9]$|^2[0]$', match_stake, pass_user_data=True))
    dp.add_handler(RegexHandler('^How to Play$', how_play, pass_user_data=True))
    dp.add_handler(RegexHandler('^Start the Game$', match_start, pass_user_data=True))

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
