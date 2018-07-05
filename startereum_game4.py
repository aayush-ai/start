#!/usr/bin/env python
#attempt 1: serverless lambda, and dynamodb: issues with webhook and telegram api
#attempt 2: ec2 and sqlite: issues with concurrent calls and dB locks
#attemp 3: moving to PostGres
#this file represents a full game set:
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
    conn = sqlite3.connect('startereum_master2.sqlite', timeout=10)
    cur = conn.cursor()
    conn.text_factory = str
    # 3 tables: userdata, match_matches, mining_games,
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
    conn = sqlite3.connect('startereum_master2.sqlite')
    cur = conn.cursor()
    conn.text_factory = str


    if len(cur.execute('''SELECT id FROM userdata WHERE id = ?
            ''', (update.effective_message.from_user.id,)).fetchall())>0:
        #this loads the relevant columns in a list # impliment a better DRY loop
        c=cur.execute('''SELECT firstname, email, username FROM userdata WHERE id = ?''',
        (update.effective_message.from_user.id,)).fetchone()
        user_data['firstname']=c[0]
        user_data['email']=c[1]
        user_data['username']=c[2]

        c=cur.execute('''SELECT match1_pick, match2_pick, match3_pick, match4_pick, match5_pick, match6_pick, match7_pick
        FROM wave_4_twr WHERE id = ?''', (update.effective_message.from_user.id,)).fetchone()
        wave4_twr_pick['match1_pick']=c[0]
        wave4_twr_pick['match2_pick']=c[1]
        wave4_twr_pick['match3_pick']=c[2]
        wave4_twr_pick['match4_pick']=c[3]
        wave4_twr_pick['match5_pick']=c[4]
        wave4_twr_pick['match6_pick']=c[5]
        wave4_twr_pick['match7_pick']=c[6]

        c=cur.execute('''SELECT match1_stake, match2_stake, match3_pick, match3_stake, match4_pick, match4_stake, match5_pick, match5_stake, match6_pick, match6_stake, match7_pick, match7_stake, total_balance
        FROM wave_4_twr WHERE id = ?''', (update.effective_message.from_user.id,)).fetchone()
        wave4_twr_stake['match1_stake']=c[0]
        wave4_twr_stake['match2_stake']=c[1]
        wave4_twr_stake['match3_stake']=c[2]
        wave4_twr_stake['match4_stake']=c[3]
        wave4_twr_stake['match5_stake']=c[4]
        wave4_twr_stake['match6_stake']=c[5]
        wave4_twr_stake['match7_stake']=c[6]
        wave4_twr_stake['total_balance']=c[7]

        c=cur.execute('''SELECT match3_mine, match3_mine_token, gk1_pick, gk1_token, verify1_text, verify1_token, match5_mine, match5_mine_token, gk2_pick, gk2_token, gk3_pick, gk3_token, mine_pick, priv_pick, frnd_email, mine_text
        FROM wave_4_mining WHERE id = ?''', (update.effective_message.from_user.id,)).fetchone()
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

        print('Returning user')

    else:
        cur.execute('''INSERT OR IGNORE INTO userdata (id, firstname, username) VALUES (?, ?, ?)''', \
        (update.effective_message.from_user.id, update.effective_message.from_user.first_name, update.effective_message.from_user.username,))
        cur.execute('''INSERT OR IGNORE INTO wave_4_twr (id) VALUES (?)''', \
        (update.effective_message.from_user.id,))
        cur.execute('''INSERT OR IGNORE INTO wave_4_mining (id) VALUES (?)''', \
        (update.effective_message.from_user.id,))


        print('New user')

    conn.commit()
    conn.close()

def updateUser(category, text, update):
    # Updates user info as inputted.
    conn = sqlite3.connect('startereum_master2.sqlite')
    cur = conn.cursor()
    conn.text_factory = str
    # Update SQLite database as needed.
    cur.execute('''UPDATE OR IGNORE userdata SET {} = ? WHERE id = ?'''.format(category), \
        (text, update.effective_message.from_user.id,))
    print ('Updated')
    conn.commit()
    conn.close()


def update_twr(category, text, update):
    # Updates user info as inputted.
    conn = sqlite3.connect('startereum_master2.sqlite')
    cur = conn.cursor()
    conn.text_factory = str
    # Update SQLite database as needed.
    cur.execute('''UPDATE OR IGNORE wave_4_twr SET {} = ? WHERE id = ?'''.format(category), \
        (text, update.message.from_user.id,))
    print (category, text)
    conn.commit()
    conn.close()


def update_mining(category, text, update):
    # Updates user info as inputted.
    conn = sqlite3.connect('startereum_master2.sqlite')
    cur = conn.cursor()
    conn.text_factory = str
    # Update SQLite database as needed.
    cur.execute('''UPDATE OR IGNORE wave4_feeback SET {} = ? WHERE id = ?'''.format(category), \
        (text, update.message.from_user.id,))
    print (category, text)
    conn.commit()
    conn.close()


#### Python Telegram Bot Branch ####

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton,Message, Chat, Update, Bot, User
from telegram.ext import Updater, CommandHandler, CallbackQueryHandler, RegexHandler, MessageHandler, Filters, ConversationHandler
import logging, time
import re
## declare all the list of all games in a game set.
match_game_questions= ['Match 1: Which project is more innovative?',
    'Match 2: Which project is more likely to execute its vision? ',
    'Match 3: Which project appears more credible?',
    'Match 4: Which project is more innovative?',
    'Match 5: Which project is more likely to execute its vision?',
    'Match 6: Which project appears more credible?',
    'Match 7: Which project is more likely to execute its vision?']

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

#there are three types of games in this set match, GK, mining. match  & GK emits a callback_query,
#while mining and tokens are keyboard inputs.

def start(bot, update, user_data):

    checkUser(bot, update, user_data)

    if user_data.get('email') is None:


#this is the primary body of the game session

        update.effective_message.reply_text("Hola Cypherpunk!\nEnter your email ID to receive your playing balance:")

    else:
        markup_main = ReplyKeyboardMarkup([['How to Play'],['Start the Game'],['Player Profile']], one_time_keyboard=True)
        update.effective_message.reply_text("Welcome back, {}!\nAre you ready for another go?".format(update.effective_user.first_name),reply_markup=markup_main)

def email(bot, update, user_data):
    if user_data.get('email') is None:
        markup_main = ReplyKeyboardMarkup([['How to Play'],['Start the Game'], ['Player Profile']], one_time_keyboard=True)
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
        match_start(bot, update, user_data, wave4_twr, wave4_mining)


def how_play(bot,update, user_data):
    markup_main = ReplyKeyboardMarkup([['How to Play'],['Start the Game'], ['Player Profile']], one_time_keyboard=True)
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
    checkUser(bot, update, user_data)
    mcq_markup = InlineKeyboardMarkup([[InlineKeyboardButton("Option A", callback_data='Option A'),InlineKeyboardButton("Option B", callback_data='Option B')],
                                        [InlineKeyboardButton("Option C", callback_data='Option C'),InlineKeyboardButton("Option D", callback_data='Option D')]])

    if  wave4_twr_pick.get('match1_pick') is None:
        update.effective_message.reply_text(text=match_game_questions[0], reply_markup=reply_markup_match)
        bot.send_photo(update.effective_message.chat_id, photo=match_game_photos[0])
    elif wave4_twr_pick.get('match1_pick') is None:
        update.effective_message.reply_text(text=match_game_questions[1], reply_markup=reply_markup_match)
        bot.send_photo(update.effective_message.chat_id, photo=match_game_photos[1])
    elif wave4_twr_pick[2] == None:
        update.effective_message.reply_text(text=match_game_questions[2], reply_markup=reply_markup_match)
        bot.send_photo(update.effective_message.chat_id, photo=match_game_photos[2])

    elif wave4_twr_mining['match3_mine'] == None:
        update.effective_message.reply_text(text='Mining Game #1: To win a 1 token bonus, tell us why you made the previous selection?')

    elif wave4_twr_mining['gk1_pick'] == None:
        update.effective_message.reply_text(text=gk_qs[0], reply_markup=mcq_markup)

    elif wave4_twr_pick[3] == None:
        bot.send_message(update.effective_message.chat_id, text = 'Sharding is the process of splitting a blockchain into multiple data fragments.\n\n')
        time.sleep(2)
        update.effective_message.reply_text(text=match_game_questions[3], reply_markup=reply_markup_match)
        bot.send_photo(update.effective_message.chat_id, photo=match_game_photos[3])

    elif wave4_twr_mining['verify1_text'] == None:
        update.effective_message.reply_text(text='Mining Game #2: To win a 1 token bonus, organize the text fragments below into a simple sentence.\n\n"brown lazy over fox quick dog jumped the the"')

    elif wave4_twr_pick[4] == None:
        update.effective_message.reply_text(text=match_game_questions[4], reply_markup=reply_markup_match)
        bot.send_photo(update.effective_message.chat_id, photo=match_game_photos[4])

    elif wave4_twr_mining['match5_mine'] == None:
        update.effective_message.reply_text(text='Mining Game #3: To win a 1 token bonus, tell us why you made previous selection?')

    elif wave4_twr_mining['gk2_pick'] == None:
        update.effective_message.reply_text(text=gk_qs[1], reply_markup=mcq_markup)

    elif wave4_twr_pick[5] == None:
        bot.send_message(update.effective_message.chat_id, text = 'Segwit is a means of increasing block size.\n\n')
        time.sleep(2)
        update.effective_message.reply_text(text=match_game_questions[5], reply_markup=reply_markup_match)
        bot.send_photo(update.effective_message.chat_id, photo=match_game_photos[5])

    elif wave4_twr_mining['gk3_pick'] == None:
        update.effective_message.reply_text(text=gk_qs[2], reply_markup=mcq_markup)

    elif wave4_twr_pick['match7_pick'] == None:
        bot.send_message(update.effective_message.chat_id, text = 'Delegated Proof of Stake may lead to corruption, autonomy or human error on the part of the delegate.\n\n')
        time.sleep(2)
        update.effective_message.reply_text(text=match_game_questions[6], reply_markup=reply_markup_match)
        bot.send_photo(update.effective_message.chat_id, photo=match_game_photos[6])

    elif wave4_twr_mining['mine_pick'] == None:
        update.effective_message.reply_text(text='How did you enjoy this game set? I feel:\n\nA: Pumped, made me some money!\nB: Stoked, learned me a bit.\nOption C: Chill, this was diverting.\nD: Bummed out, this stank.', reply_markup=mcq_markup)

    elif wave4_twr_mining['priv_pick'] == None:
        update.effective_message.reply_text(text='If you win big can we publish your name and winnings to the Leaderboard?\n\nA: Sure\nB: Yes, but use my telegram username\nC: Yes, but only name, not winnings\nD: Dont publish anything.',reply_markup=mcq_markup)

    elif wave4_twr_mining['frnd_email'] == None:
        update.effective_message.reply_text(text='To win a 10 token bonus, share this link with this game to a friend who might enjoy playing it.\n\nhttp://bit.ly/2MP8ozf\n\nAfter sharing, enter his or her email id here:')


    elif wave4_twr_mining['mine_text'] == None:
        bot.send_message(update.effective_message.chat_id, text = 'This game set is now concluded.\n\nIt may take us a few hours to collate responses and calculate final results.\n\n')
        time.sleep(2)
        update.effective_message.reply_text(text='Any other thoughts,questions and feedback can be shared below:', reply_markup=markup_main)
    else:
        bot.send_message(update.effective_message.chat_id, text = 'Thank you for playing. Decentralize together!')



def match_pick(bot, update):

    checkUser(bot, update, user_data)

    if wave4_twr_pick.get('match1_pick') is None:
        text = update.callback_query.data
        category = 'match1_pick'
        wave4_twr_pick[category] = text
        update_twr(category, text, update)
        markup2= ReplyKeyboardMarkup([[str(i) for i in range(6 * j + 3, 6 * j + 9)] for j in range(3)], one_time_keyboard=True)
        update.callback_query.message.reply_text(text="Token Left: " + str(user_data.get('total_balance')) + "\n Please stake tokens for {}".format(text), reply_markup=markup2)




#REGEX_HANDLERS
#for token_stake
def match_stake(bot, update, wave4_twr_stake):

    checkUser(bot, update, user_data)
    text = update.message.text
    for i in range[6]:
        if wave4_twr_stake[i] == 0:
            category = 'wave4_twr_stake[i]'
            wave4_twr_stake[category] = text
            update_twr(category, text, update)

            if update_twr(category, text, update) == "Complete":

                total = int(wave4_twr_stake['total_balance'])
                last_stake = int(text)
                text = total - last_stake
                category = 'total_balance'
                user_data['total_balance'] = text
                update_twr(category, text, update)
                match_start(bot, update, user_data, wave4_twr_pick, wave4_twr_mining)



def mining_handler (bot, update, wave4_mining):

    checkUser(bot, update, user_data)

    if wave4_mining['match3_mine'] == None:
        text = update.message.text
        category = 'match3_mine'
        update_mining(category, text, update)
        if update_mining(category, text, update) == 'Complete':
            text = 1
            category = 'match3_mine_token'
            update_mining(category, text, update)
            match_start(bot, update, user_data, wave4_twr_pick, wave4_twr_mining)


    elif wave4_mining['match5_mine'] == None:
        text = update.message.text
        category = 'match5_mine'
        update_mining(category, text, update)

        if update_mining(category, text, update) == 'Complete':
            text = 1
            category = 'match5_mine_token'
            update_mining(category, text, update)
            match_start(bot, update, user_data, wave4_twr_pick, wave4_twr_mining)

    elif wave4_mining['verify1_text'] == None:
        text = update.message.text
        category = 'match5_mine'
        update_mining(category, text, update)

        if update_mining(category, text, update) == 'Complete':
            text = 1
            category = 'verify1_token'
            update_mining(category, text, update)
            match_start(bot, update, user_data, wave4_twr_pick, wave4_twr_mining)


    elif wave4_mining['mine_text'] == None:
        text = update.message.text
        category = 'mine_text'
        update_mining(category, text, update)


def gk_handler(bot, update):

    if wave4_mining['gk1_pick'] == 0:
        text = update.callback_query.data
        category = 'gk1_pick'
        update_mining(category, text, update)

        if update_mining(category, text, update) == 'Complete':
            text = 2
            category = 'gk1_token'
            update_mining(category, text, update)
            match_start(bot, update, user_data, wave4_twr_pick, wave4_twr_mining)

    elif wave4_mining['gk2_pick'] == 0:
        text = update.callback_query.data
        category = 'gk2_pick'
        update_mining(category, text, update)

        if update_mining(category, text, update) == 'Complete':
            text = 2
            category = 'gk2_token'
            update_mining(category, text, update)
            match_start(bot, update, user_data, wave4_twr_pick, wave4_twr_mining)

    elif wave4_mining['gk3_pick'] == 0:
        text = update.callback_query.data
        category = 'gk3_pick'
        update_mining(category, text, update)

        if update_mining(category, text, update) == 'Complete':
            text = 2
            category = 'gk3_token'
            update_mining(category, text, update)
            match_start(bot, update, user_data, wave4_twr_pick, wave4_twr_mining)

    elif wave4_mining['mine_pick'] == 0:
        text = update.callback_query.data
        category = 'gk2_pick'
        update_mining(category, text, update)
        match_start(bot, update, user_data, wave4_twr_pick, wave4_twr_mining)

    elif wave4_mining['priv_pick'] == 0:
        text = update.callback_query.data
        category = 'gk3_pick'
        update_mining(category, text, update)
        match_start(bot, update, user_data, wave4_twr_pick, wave4_twr_mining)



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
    dp.add_handler(RegexHandler('^Start the Game$', match_start, pass_user_data=True))
    dp.add_handler(RegexHandler('w+', mining_handler, pass_user_data=True))

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
