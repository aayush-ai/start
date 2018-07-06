#!/usr/bin/env python
#attempt 1: serverless lambda, and dynamodb: issues with webhook and telegram api
#attempt 2: ec2 and sqlite: issues with concurrent calls and dB locks
#attemp 3: moving to PostGres
#this file represents a full match set:
#### SQLITE BRANCH ####
## try sleep, if sleep works chek if update successful
##
import sys
import sqlite3
user_data = {}
wave4_twr_pick = {}
wave4_twr_stake = {}
wave4_mining = {}

def loadDB():
    # Creates SQLite database to store info.
    conn = sqlite3.connect('startereum_master8.sqlite', timeout=10)
    cur = conn.cursor()
    conn.text_factory = str
    # 3 tables: userdata, match_matches, mining_matchs,
    cur.executescript('''CREATE TABLE IF NOT EXISTS userdata
    (
    id INTEGER PRIMARY KEY UNIQUE,
    username TEXT,
    firstname TEXT,
    email TEXT UNIQUE);''')

    cur.executescript('''CREATE TABLE IF NOT EXISTS wave_4_twr
    (
    id INTEGER PRIMARY KEY UNIQUE,
    email UNIQUE,
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
    match7_stake INTEGER DEFAULT 0);''')

    cur.executescript('''CREATE TABLE IF NOT EXISTS wave_4_mining
    (
    id INTEGER PRIMARY KEY UNIQUE,
    email TEXT UNIQUE,
    match3_mine TEXT,
    match3_mine_token INTEGER DEFAULT 0,
    gk1_pick TEXT,
    gk1_token INTEGER DEFAULT 0,
    verify1_text TEXT,
    verify1_token INTEGER DEFAULT 0,
    match5_mine TEXT,
    match5_mine_token INTEGER DEFAULT 0,
    gk2_pick TEXT,
    gk2_token INTEGER DEFAULT 0,
    gk3_pick TEXT,
    gk3_token INTEGER DEFAULT 0,
    mine_pick TEXT,
    priv_pick TEXT,
    frnd_email TEXT,
    mine_text TEXT);''')
    #cur.execute("ALTER TABLE userdata ADD COLUMN qs_index int(32)")
    conn.commit()
    conn.close()

def checkUser(bot, update, user_data):
    # Checks if user has visited the bot before
    # If yes, load data of user
    # If no, then create a new entry in database
    conn = sqlite3.connect('startereum_master8.sqlite')
    cur = conn.cursor()
    conn.text_factory = str


    if len(cur.execute('''SELECT id FROM userdata WHERE id = ?
            ''', (update.effective_user.id,)).fetchall())>0:
        #this loads the relevant columns in a list # impliment a better DRY loop
        c=cur.execute('''SELECT firstname, email, username FROM userdata WHERE id = ?''',
        (update.effective_user.id,)).fetchone()
        user_data['firstname']=c[0]
        user_data['email']=c[1]
        user_data['username']=c[2]

        c=cur.execute('''SELECT match1_pick, match2_pick, match3_pick, match4_pick, match5_pick, match6_pick, match7_pick
        FROM wave_4_twr WHERE id = ?''', (update.effective_user.id,)).fetchone()
        wave4_twr_pick['match1_pick']=c[0]
        wave4_twr_pick['match2_pick']=c[1]
        wave4_twr_pick['match3_pick']=c[2]
        wave4_twr_pick['match4_pick']=c[3]
        wave4_twr_pick['match5_pick']=c[4]
        wave4_twr_pick['match6_pick']=c[5]
        wave4_twr_pick['match7_pick']=c[6]

        c=cur.execute('''SELECT match1_stake, match2_stake, match3_stake, match4_stake, match5_stake,match6_stake, match7_stake, total_balance
        FROM wave_4_twr WHERE id = ?''', (update.effective_user.id,)).fetchone()
        wave4_twr_stake['match1_stake']=c[0]
        wave4_twr_stake['match2_stake']=c[1]
        wave4_twr_stake['match3_stake']=c[2]
        wave4_twr_stake['match4_stake']=c[3]
        wave4_twr_stake['match5_stake']=c[4]
        wave4_twr_stake['match6_stake']=c[5]
        wave4_twr_stake['match7_stake']=c[6]
        wave4_twr_stake['total_balance']=c[7]

        c=cur.execute('''SELECT match3_mine, match3_mine_token, gk1_pick, gk1_token, verify1_text, verify1_token, match5_mine, match5_mine_token, gk2_pick, gk2_token, gk3_pick, gk3_token, mine_pick, priv_pick, frnd_email, mine_text
        FROM wave_4_mining WHERE id = ?''', (update.effective_user.id,)).fetchone()
        wave4_mining['match3_mine']=c[0]
        wave4_mining['match3_mine_token']=c[1]
        wave4_mining['gk1_pick']=c[2]
        wave4_mining['gk1_token']=c[3]
        wave4_mining['verify1_text']=c[4]
        wave4_mining['verify1_token']=c[5]
        wave4_mining['match5_mine']=c[6]
        wave4_mining['match5_mine_token']=c[7]
        wave4_mining['gk2_pick']=c[8]
        wave4_mining['gk2_token']=c[9]
        wave4_mining['gk3_pick']=c[10]
        wave4_mining['gk3_token']=c[11]
        wave4_mining['mine_pick']=c[12]
        wave4_mining['priv_pick']=c[13]
        wave4_mining['frnd_email']=c[14]
        wave4_mining['mine_text']=c[15]

        print('Returning user', (user_data))

    else:
        cur.execute('''INSERT OR IGNORE INTO userdata (id, firstname, username) VALUES (?, ?, ?)''', \
        (update.effective_user.id, update.effective_user.first_name, update.effective_user.username,))
        cur.execute('''INSERT OR IGNORE INTO wave_4_twr (id) VALUES (?)''', \
        (update.effective_user.id,))
        cur.execute('''INSERT OR IGNORE INTO wave_4_mining (id) VALUES (?)''', \
        (update.effective_user.id,))


        print('New user')

    conn.commit()
    conn.close()

def updateUser(category, text, update):
    # Updates user info as inputted.
    conn = sqlite3.connect('startereum_master8.sqlite')
    cur = conn.cursor()
    conn.text_factory = str
    # Update SQLite database as needed.
    cur.execute('''UPDATE OR IGNORE userdata SET {} = ? WHERE id = ?'''.format(category), \
        (text, update.effective_user.id,))
    print ('Updated')
    conn.commit()
    conn.close()


def update_twr(category, text, update):
    # Updates user info as inputted.

    conn = sqlite3.connect('startereum_master8.sqlite')
    cur = conn.cursor()
    conn.text_factory = str

    # Update SQLite database as needed.
    cur.execute('''UPDATE OR IGNORE wave_4_twr SET {} = ? WHERE id = ?'''.format(category), \
        (text, update.effective_user.id,))
    print (category, text)
    conn.commit()
    conn.close()

def update_stake(category, text, update):
    # Updates user info as inputted.

    conn = sqlite3.connect('startereum_master8.sqlite')
    cur = conn.cursor()
    conn.text_factory = str

    # Update SQLite database as needed.
    cur.execute('''UPDATE OR IGNORE wave_4_twr SET {} = ? WHERE id = ?'''.format(category), \
        (text, update.effective_user.id,))
    print (category, text)
    conn.commit()
    conn.close()


def update_mining(category, text, update):
    # Updates user info as inputted.
    conn = sqlite3.connect('startereum_master8.sqlite')
    cur = conn.cursor()
    conn.text_factory = str
    # Update SQLite database as needed.
    cur.execute('''UPDATE OR IGNORE wave_4_mining SET {} = ? WHERE id = ?'''.format(category), \
        (text, update.effective_user.id,))
    print (category, text)
    conn.commit()
    conn.close()


#### Python Telegram Bot Branch ####

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton,Message, Chat, Update, Bot, User
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, RegexHandler, MessageHandler, Filters, ConversationHandler
import logging, time
import re
## declare all the list of all matchs in a match set.
match_match_questions= ['Game 1: Which project is more innovative?',
    'Game 2: Which project is more likely to execute its vision? ',
    'Game 3: Which project appears more credible?',
    'Game 5: Which project is more innovative?',
    'Game 7: Which project is more likely to execute its vision?',
    'Game 9: Which project appears more credible?',
    'Game 11: Which project is more likely to execute its vision?']

match_match_photos = ['https://docs.google.com/drawings/d/e/2PACX-1vRMhMrgSYyzMMRy6yeMIO2s4tiowDIF_jlz5YFgG0W_n6cMtrQmax8IalCgm09irTt_CQfl2PNELIxr/pub?w=1436&h=942',
'https://docs.google.com/drawings/d/e/2PACX-1vQ6ky7TyqJURoAOYH_EjoiZEQEo2WID0r3LpBj1Oqh_uwR4kebyNgVq5uADtGb5uv5QZZn8NHbeuhbp/pub?w=1430&h=942',
'https://docs.google.com/drawings/d/e/2PACX-1vT-JmUzolHLeKNtbMcFUCvAH418M1vEsG6roH7b6DsdUVTYK-lojovid-YALMNhE9at2QPgUUFqK_4s/pub?w=1432&h=939',
'https://docs.google.com/drawings/d/e/2PACX-1vQ3gXL36QPx1YR-9vjkBlAzlOpJlRkN-6WKMR7jO3ZVnuLwrpMxAnpNH8UTWJua60NSixDqG5FNuEPZ/pub?w=1433&h=940',
'https://docs.google.com/drawings/d/e/2PACX-1vTlYa8a33WbF0WHDFUAZblwQQLgfqtzoXhIOZGLcdEOeR7G2PmAVmY0uJmxM_rSn8-LhCx8BJqytaJ6/pub?w=1434&h=942',
'https://docs.google.com/drawings/d/e/2PACX-1vR6GjQKFELEZpi9NNMnr7igtl0BOkY4O94-bIb31I_mCQtvCgSz7Q-1RZU8ZjfBLXJrRzgHERUaRfGY/pub?w=1441&h=944',
'https://docs.google.com/drawings/d/e/2PACX-1vQ5gfL_xfwWHC2t67x-4AaE0qxRBY6IIlmbGNQb2kKvr1nWV0qXnXp26jYiQs5DrFP4P1hpVQ3z5ji7/pub?w=1443&h=944']


gk_qs = ['Game 4: To win a 2 token bonus, select the right answer to the question: What is sharding?\n\nA: It is not polite.\nB: Splitting a blockchain into pieces.\nC: Failing to record a state change.\nD: Betting against a cryptoasset.',
'Game 8: To win a 2 token bonus: What is segwit?\n\nA: Birth of Bitcoin Talk.\nB: Decrease in mining reward.\nC: Scooters on blockchain.\nD: A way to increase block size.',
'Game 10: To win a 2 token bonus: Critics say the problem with Delegated Proof of Stake (DPoS) is that\n\nA: It uses too much energy.\nB: It has low transaction frequency.\nC: It is prone to corruption.\nD: It is non-falsifiable.']

# Enable logging
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

#there are three types of matchs in this set match, GK, mining. match  & GK emits a callback_query,
#while mining and tokens are keyboard inputs.

def start(bot, update, user_data):

    checkUser(bot, update, user_data)

    if user_data.get('email') is None:


#this is the primary body of the match session

        update.effective_message.reply_text("Hola Cypherpunk!\n\nEnter your email ID to receive your playing balance:")

    else:
        markup_main = ReplyKeyboardMarkup([['How to Play'],['Start the game'],['Player Profile']], one_time_keyboard=True)
        update.effective_message.reply_text("Welcome back, {}!\nAre you ready for another go?".format(update.effective_user.first_name),reply_markup=markup_main)

def email(bot, update, user_data):

    if user_data.get('email') is None:
        markup_main = ReplyKeyboardMarkup([['How to Play'],['Start the game'], ['Player Profile']], one_time_keyboard=True)
        text = update.effective_message.text
        category = 'email'
        user_data[category] = text
        updateUser(category, text, update)

        update.effective_message.reply_text("Okay, you now have 100 startereum tokens to play with.\n\nIf you have already been allocated startereums in the past, these will be credited to your account after a delay.\n\nYou will receive an update on your email: {}".format(text),reply_markup=markup_main)
    else:
        text = update.effective_message.text
        category = 'frnd_email'
        user_data[category] = text
        update_mining(category, text, update)
        match_start(bot, update, user_data)


def how_play(bot,update, user_data):
    markup_main = ReplyKeyboardMarkup([['How to Play'],['Start the game'], ['Player Profile']], one_time_keyboard=True)
    text = update.effective_message.text
    if text == 'How to Play':
        update.effective_message.reply_text(text= "{}, let's review the basics. Hit start when done!".format(update.effective_user.first_name),reply_markup=markup_main)
        bot.sendDocument(chat_id=update.effective_message.chat_id, document='https://media.giphy.com/media/2Yc0g11QsZ7vqxmzTn/giphy.gif')

#match loop starts here:

def match_start(bot, update, user_data):

    global match_match_questions
    global match_match_photos
    reply_markup_match = InlineKeyboardMarkup([[InlineKeyboardButton("Project A", callback_data='Project A'),InlineKeyboardButton("Project B", callback_data='Project B')]])
    markup2= ReplyKeyboardMarkup([[str(i) for i in range(6 * j + 3, 6 * j + 9)] for j in range(3)], one_time_keyboard=True)
    checkUser(bot, update, user_data)
    mcq_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Option A", callback_data='Option A'),InlineKeyboardButton("Option B", callback_data='Option B')],
                                        [InlineKeyboardButton("Option C", callback_data='Option C'),InlineKeyboardButton("Option D", callback_data='Option D')]])

    if  wave4_twr_pick.get('match1_pick') is None:
        bot.send_message(update.effective_message.chat_id, text = 'Okay we are live now!\n\n')
        time.sleep(2)
        bot.send_photo(update.effective_message.chat_id, photo=match_match_photos[0])
        update.effective_message.reply_text(text=match_match_questions[0], reply_markup=reply_markup_match)

    elif wave4_twr_pick.get('match2_pick') is None:

        bot.send_photo(update.effective_message.chat_id, photo=match_match_photos[1])
        update.effective_message.reply_text(text=match_match_questions[1], reply_markup=reply_markup_match)

    elif wave4_twr_pick.get('match3_pick') is None:
        bot.send_photo(update.effective_message.chat_id, photo=match_match_photos[2])
        update.effective_message.reply_text(text=match_match_questions[2], reply_markup=reply_markup_match)


    elif wave4_mining.get('match3_mine') is None:
        update.effective_message.reply_text(text='To win a 1 token bonus, tell us why you made the previous selection?')

    elif wave4_mining.get('gk1_pick') is None:
        update.effective_message.reply_text(text=gk_qs[0], reply_markup=mcq_markup)

    elif wave4_twr_pick.get('match4_pick') is None:
        bot.send_message(update.effective_message.chat_id, text = 'Sharding is the process of splitting a blockchain into multiple data fragments.\n\n')
        time.sleep(2)

        bot.send_photo(update.effective_message.chat_id, photo=match_match_photos[3])
        update.effective_message.reply_text(text=match_match_questions[3], reply_markup=reply_markup_match)

    elif wave4_mining.get('verify1_text') is None:
        bot.send_photo(update.effective_message.chat_id, photo='https://techcoins.net/wp-content/uploads/2017/10/smart_contract.png')
        update.effective_message.reply_text(text='Game 6: Explain this diagram in a simple sentence:')

    elif wave4_twr_pick.get('match5_pick') is None:
        bot.send_photo(update.effective_message.chat_id, photo=match_match_photos[4])
        update.effective_message.reply_text(text=match_match_questions[4], reply_markup=reply_markup_match)


    elif wave4_mining.get('match5_mine') is None:
        update.effective_message.reply_text(text='To win a 1 token bonus, tell us what is wrong or bad with the project you did NOT select.')

    elif wave4_mining.get('gk2_pick') is None:
        update.effective_message.reply_text(text=gk_qs[1], reply_markup=mcq_markup)

    elif wave4_twr_pick.get('match6_pick')  is None:
        bot.send_message(update.effective_message.chat_id, text = 'Segwit is a means of increasing block size.\n\n')
        time.sleep(2)
        bot.send_photo(update.effective_message.chat_id, photo=match_match_photos[5])
        update.effective_message.reply_text(text=match_match_questions[5], reply_markup=reply_markup_match)


    elif wave4_mining.get('gk3_pick') is None:
        update.effective_message.reply_text(text=gk_qs[2], reply_markup=mcq_markup)

    elif wave4_twr_pick.get('match7_pick')  is None:
        bot.send_message(update.effective_message.chat_id, text = 'Delegated Proof of Stake may lead to corruption, autonomy or human error on the part of the delegate.\n\n')
        time.sleep(2)

        bot.send_photo(update.effective_message.chat_id, photo=match_match_photos[6])
        update.effective_message.reply_text(text=match_match_questions[6], reply_markup=reply_markup_match)

    elif wave4_mining.get('mine_pick') is None:
        update.effective_message.reply_text(text='This ends the staking matches.\n\nHow did you enjoy this match set? I feel:\n\nA: Pumped, made me some money!\nB: Stoked, learned me a bit.\nC: Chill, this was diverting.\nD: Bummed out, this stank.', reply_markup=mcq_markup)

    elif wave4_mining.get('priv_pick') is None:
        update.effective_message.reply_text(text='If you win big can we publish your name and winnings to the Leaderboard?\n\nA: Sure\nB: Yes, but use my telegram username\nC: Yes, but only name, not winnings\nD: Dont publish anything.',reply_markup=mcq_markup)

    elif wave4_mining.get('frnd_email') is None:
        update.effective_message.reply_text(text='To win an additional 10 tokens share the email of a friend who might enjoy playing this game:')




    elif wave4_mining.get('mine_text') is None:
        bot.send_message(update.effective_message.chat_id, text = 'Please share this link with your friend.\n\nhttp://bit.ly/2MP8ozf')
        time.sleep(10)
        bot.send_message(update.effective_message.chat_id, text = 'This match set is now concluded.\n\nIt may take us a few hours to collate responses and calculate final results.\n\n')
        markup_main = ReplyKeyboardMarkup([['How to Play'],['Start the game'], ['Player Profile']], one_time_keyboard=True)
        update.effective_message.reply_text(text='Any other thoughts,questions and feedback can be shared below:', reply_markup=markup_main)

    else:

        bot.send_message(update.effective_message.chat_id, text = 'This match set is now concluded.\n\nThank you for playing. Decentralize together!')



def match_pick(bot, update):

    checkUser(bot, update, user_data)

    if wave4_twr_pick.get('match1_pick') is None:
        text = update.callback_query.data
        category = 'match1_pick'
        wave4_twr_pick[category] = text
        update_twr(category, text, update)
        time.sleep(1)
        balance = str(wave4_twr_stake.get('total_balance'))
        markup2= ReplyKeyboardMarkup([[str(i) for i in range(6 * j + 3, 6 * j + 9)] for j in range(3)], one_time_keyboard=True)
        update.callback_query.message.reply_text(text="Stake your tokens for {} (Balance: ".format(text) + balance + ")", reply_markup=markup2)


    elif wave4_twr_pick.get('match2_pick') is None:
        text = update.callback_query.data
        category = 'match2_pick'
        wave4_twr_pick[category] = text
        update_twr(category, text, update)
        time.sleep(1)
        balance = str(wave4_twr_stake.get('total_balance'))
        markup2= ReplyKeyboardMarkup([[str(i) for i in range(6 * j + 3, 6 * j + 9)] for j in range(3)], one_time_keyboard=True)
        update.callback_query.message.reply_text(text="Stake your tokens for {} (Balance: ".format(text) + balance + ")", reply_markup=markup2)

    elif wave4_twr_pick.get('match3_pick') is None:
        text = update.callback_query.data
        category = 'match3_pick'
        wave4_twr_pick[category] = text
        update_twr(category, text, update)
        time.sleep(1)
        balance = str(wave4_twr_stake.get('total_balance'))
        markup2= ReplyKeyboardMarkup([[str(i) for i in range(6 * j + 3, 6 * j + 9)] for j in range(3)], one_time_keyboard=True)
        update.callback_query.message.reply_text(text="Stake your tokens for {} (Balance: ".format(text) + balance + ")", reply_markup=markup2)

    elif wave4_twr_pick.get('match4_pick') is None:
        text = update.callback_query.data
        category = 'match4_pick'
        wave4_twr_pick[category] = text
        update_twr(category, text, update)
        time.sleep(1)
        balance = str(wave4_twr_stake.get('total_balance'))
        markup2= ReplyKeyboardMarkup([[str(i) for i in range(6 * j + 3, 6 * j + 9)] for j in range(3)], one_time_keyboard=True)
        update.callback_query.message.reply_text(text="Stake your tokens for {} (Balance: ".format(text) + balance + ")", reply_markup=markup2)

    elif wave4_twr_pick.get('match5_pick') is None:
        text = update.callback_query.data
        category = 'match5_pick'
        wave4_twr_pick[category] = text
        update_twr(category, text, update)
        time.sleep(1)
        balance = str(wave4_twr_stake.get('total_balance'))
        markup2= ReplyKeyboardMarkup([[str(i) for i in range(6 * j + 3, 6 * j + 9)] for j in range(3)], one_time_keyboard=True)
        update.callback_query.message.reply_text(text="Stake your tokens for {} (Balance: ".format(text) + balance + ")", reply_markup=markup2)

    elif wave4_twr_pick.get('match6_pick') is None:
        text = update.callback_query.data
        category = 'match6_pick'
        wave4_twr_pick[category] = text
        update_twr(category, text, update)
        time.sleep(1)
        balance = str(wave4_twr_stake.get('total_balance'))
        markup2= ReplyKeyboardMarkup([[str(i) for i in range(6 * j + 3, 6 * j + 9)] for j in range(3)], one_time_keyboard=True)
        update.callback_query.message.reply_text(text="Stake your tokens for {} (Balance: ".format(text) + balance + ")", reply_markup=markup2)

    elif wave4_twr_pick.get('match7_pick') is None:
        text = update.callback_query.data
        category = 'match7_pick'
        wave4_twr_pick[category] = text
        update_twr(category, text, update)
        time.sleep(1)
        balance = str(wave4_twr_stake.get('total_balance'))
        markup2= ReplyKeyboardMarkup([[str(i) for i in range(6 * j + 3, 6 * j + 9)] for j in range(3)], one_time_keyboard=True)
        update.callback_query.message.reply_text(text="Stake your tokens for {} (Balance: ".format(text) + balance + ")", reply_markup=markup2)


#REGEX_HANDLERS
#for token_stake
def match_stake(bot, update, user_data):

    checkUser(bot, update, user_data)


    if wave4_twr_stake.get('match1_stake') == 0:
        text = update.message.text
        category = 'match1_stake'
        wave4_twr_stake[category] = text
        update_twr(category, text, update)


        text = update.message.text
        total = wave4_twr_stake.get('total_balance')
        last_stake = int(text)
        text = total - last_stake
        category = 'total_balance'
        wave4_twr_stake['total_balance'] = text
        update_twr(category, text, update)
        match_start(bot, update, user_data)

    elif wave4_twr_stake.get('match2_stake') == 0:
        text = update.message.text
        category = 'match2_stake'
        wave4_twr_stake[category] = text
        update_twr(category, text, update)


        text = update.message.text
        total = wave4_twr_stake.get('total_balance')
        last_stake = int(text)
        text = total - last_stake
        category = 'total_balance'
        wave4_twr_stake['total_balance'] = text
        update_twr(category, text, update)
        match_start(bot, update, user_data)

    elif wave4_twr_stake.get('match3_stake') == 0:
        text = update.message.text
        category = 'match3_stake'
        wave4_twr_stake[category] = text
        update_twr(category, text, update)


        text = update.message.text
        total = wave4_twr_stake.get('total_balance')
        last_stake = int(text)
        text = total - last_stake
        category = 'total_balance'
        wave4_twr_stake['total_balance'] = text
        update_twr(category, text, update)
        match_start(bot, update, user_data)

    elif wave4_twr_stake.get('match4_stake') == 0:
        text = update.message.text
        category = 'match4_stake'
        wave4_twr_stake[category] = text
        update_twr(category, text, update)


        text = update.message.text
        total = wave4_twr_stake.get('total_balance')
        last_stake = int(text)
        text = total - last_stake
        category = 'total_balance'
        wave4_twr_stake['total_balance'] = text
        update_twr(category, text, update)
        match_start(bot, update, user_data)

    elif wave4_twr_stake.get('match5_stake') == 0:
        text = update.message.text
        category = 'match5_stake'
        wave4_twr_stake[category] = text
        update_twr(category, text, update)


        text = update.message.text
        total = wave4_twr_stake.get('total_balance')
        last_stake = int(text)
        text = total - last_stake
        category = 'total_balance'
        wave4_twr_stake['total_balance'] = text
        update_twr(category, text, update)

        match_start(bot, update, user_data)

    elif wave4_twr_stake.get('match6_stake') == 0:
        text = update.message.text
        category = 'match6_stake'
        wave4_twr_stake[category] = text
        update_twr(category, text, update)


        text = update.message.text
        total = wave4_twr_stake.get('total_balance')
        last_stake = int(text)
        text = total - last_stake
        category = 'total_balance'
        wave4_twr_stake['total_balance'] = text
        update_twr(category, text, update)
        match_start(bot, update, user_data)

    elif wave4_twr_stake.get('match7_stake') == 0:
        text = update.message.text
        category = 'match7_stake'
        wave4_twr_stake[category] = text
        update_twr(category, text, update)


        text = update.message.text
        total = wave4_twr_stake.get('total_balance')
        last_stake = int(text)
        text = total - last_stake
        category = 'total_balance'
        wave4_twr_stake['total_balance'] = text
        update_twr(category, text, update)
        match_start(bot, update, user_data)

def mining_handler (bot, update, user_data):

    checkUser(bot, update, user_data)

    if wave4_mining.get('match3_mine') is None:
        text = update.message.text
        category = 'match3_mine'
        update_mining(category, text, update)

        text = 1
        category = 'match3_mine_token'
        update_mining(category, text, update)
        match_start(bot, update, user_data)


    elif wave4_mining.get('match5_mine') is None:
        text = update.message.text
        category = 'match5_mine'
        update_mining(category, text, update)


        text = 1
        category = 'match5_mine_token'
        update_mining(category, text, update)
        match_start(bot, update, user_data)

    elif wave4_mining.get('verify1_text') is None:
        text = update.message.text
        category = 'verify1_text'

        update_mining(category, text, update)

        text = 1
        category = 'verify1_token'

        update_mining(category, text, update)
        time.sleep(3)
        match_start(bot, update, user_data)


    elif wave4_mining.get('mine_text') is None:
        text = update.message.text
        category = 'mine_text'
        update_mining(category, text, update)
        match_start(bot, update, user_data)


def gk_handler(bot, update):

    if wave4_mining.get('gk1_pick') is None:
        text = update.callback_query.data
        category = 'gk1_pick'
        update_mining(category, text, update)
        update.callback_query.message.reply_text(text="Stake your tokens for {} (Balance: ".format(text) + balance + ")", reply_markup=markup2)



        text = 2
        category = 'gk1_token'
        update_mining(category, text, update)
        match_start(bot, update, user_data)

    elif wave4_mining.get('gk2_pick') is None:
        text = update.callback_query.data
        category = 'gk2_pick'
        update_mining(category, text, update)


        text = 2
        category = 'gk2_token'
        update_mining(category, text, update)
        match_start(bot, update, user_data)

    elif wave4_mining.get('gk3_pick') is None:
        text = update.callback_query.data
        category = 'gk3_pick'
        update_mining(category, text, update)

        text = 2
        category = 'gk3_token'
        update_mining(category, text, update)
        match_start(bot, update, user_data)

    elif wave4_mining.get('mine_pick') is None:
        text = update.callback_query.data
        category = 'mine_pick'
        update_mining(category, text, update)
        match_start(bot, update, user_data)

    elif wave4_mining.get('priv_pick') is None:
        text = update.callback_query.data
        category = 'priv_pick'
        update_mining(category, text, update)
        match_start(bot, update, user_data)


def profile(bot, update, user_data):
    markup_main = ReplyKeyboardMarkup([['How to Play'],['Start the game'],['Player Profile']], one_time_keyboard=True)
    update.effective_message.reply_text('{}, thanks for playing!\n\nThe profile with your earnings with be updated post-result. Stay Tuned!'.format(update.effective_user.first_name),reply_markup=markup_main)


def top_3(bot, update, user_data):


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)

def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater("604744099:AAHImp03yylJO8Qjod3bfhEw5AmmV2fDK4w")
    print("Connection to Telegram established; starting bot.")
    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    dp.add_handler(CommandHandler('start', start, pass_user_data=True))
    dp.add_handler(RegexHandler('(\w+[.|\w])*@(\w+[.])*\w+', email, pass_user_data=True))
    dp.add_handler(CallbackQueryHandler(match_pick, pattern=r"Project"))
    dp.add_handler(CallbackQueryHandler(gk_handler, pattern=r"Option"))
    dp.add_handler(RegexHandler('^[1-2]?[3-9]$|^2[0]$', match_stake, pass_user_data=True))
    dp.add_handler(RegexHandler('^How to Play$', how_play, pass_user_data=True))
    dp.add_handler(RegexHandler('^Start the game$', match_start, pass_user_data=True))
    dp.add_handler(RegexHandler('^Player Profile$', profile, pass_user_data=True))
    dp.add_handler(RegexHandler('\w+', mining_handler, pass_user_data=True))

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
