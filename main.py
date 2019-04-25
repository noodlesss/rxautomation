import os, json, time, logging, requests, pika
# import variable constructors
import var_construct, parse_info
#telegram import libraries
import telepot, time, re, sys
from telepot.loop import MessageLoop, Orderer
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.delegate import (
    per_chat_id, per_callback_query_origin, create_open, pave_event_space)



# Rabbitmq reply queue callback
# called when received a message from reply queue. results of tasks.
def reply_queue_callback(ch, method, properties, body):
    body = json.loads(body)
    logging.info('task: %s\n result: %s' %(body['task'], body['result']))
    if body['task'] == 'checkcluster' and body['result'] == 'cluster up':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
               [InlineKeyboardButton(text='Create network', callback_data='create_network')], 
               [InlineKeyboardButton(text='Deploy Prism Central', callback_data='deploypc')],
               [InlineKeyboardButton(text='Set pub key', callback_data='set_pub_key')]
           ])
        bot.sendMessage(chat_id, 'cluster %s:\n ' %envars['cluster_ip'], reply_markup=keyboard)
    elif body['task'] == 'deploypc' and body['result'] == 'SUCCEEDED':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text='Register pc', callback_data='register_pc')]])
        bot.sendMessage(chat_id, 'PC ready', reply_markup=keyboard)
    else:
        bot.sendMessage(chat_id, '%s: %s' %(body['task'], body['result']))


# Telegram handler
def handler(msg):
    global waiting_for_vars
    content_type, chat_type, chat_id = telepot.glance(msg)
    if content_type == 'text': data = msg['text']
    logging.info('msg handler: %s' %msg['text'])
    if waiting_for_vars:
        global envars
        vars_from_bot = data
        try:
            envars = parse_info.get_vars_from_bot(vars_from_bot)
        except Exception as e:
            logging.error('ERROR in handler: %s' %e)
            bot.sendMessage(chat_id, text='error: %s' %e)
        if envars: 
            waiting_for_vars = False
            logging.info('vars:\n%s' %envars)
            keyboard = InlineKeyboardMarkup(inline_keyboard=[
               [InlineKeyboardButton(text='start cluster_ip: %s' %envars['cluster_ip'], callback_data='checkcluster')],
               ])
            bot.sendMessage(chat_id,text='start', reply_markup=keyboard)
    elif waiting_for_vars == False and msg['text'] == 'reset':
        logging.info('reset vars')
        waiting_for_vars = True
        envars = None
        bot.sendMessage(chat_id, 'variables reset. send vars')
    if data == 'cmd':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
               [InlineKeyboardButton(text='Create network', callback_data='create_network')], 
               [InlineKeyboardButton(text='Deploy Prism Central', callback_data='deploypc')],
               [InlineKeyboardButton(text='Register pc', callback_data='register_pc')],
               [InlineKeyboardButton(text='Set pub key', callback_data='set_pub_key')]
           ])
        bot.sendMessage(chat_id, 'cluster %s:\n ' %envars['cluster_ip'], reply_markup=keyboard)



# Telegram callback
def bot_callback(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    logging.info('Callback Query: %s' %(query_data))
    if envars == None:
        logging.info('no vars')
        bot.answerCallbackQuery(query_id, text='no vars')
        return None
    message = {'action': query_data, 'data': envars}
    channel_deployer.basic_publish(exchange='',
                  routing_key='deployer',
                  body=json.dumps(message))
    bot.answerCallbackQuery(query_id, text='action %s send to queue' %message['action'])

# Log object
logging.basicConfig(filename='main_ctr.log', format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)
logging.info('container started')
#init vars
#logging.info('envars: %s' % os.environ.keys)
#envars = var_construct.envars()
envars = {}
waiting_for_vars = False
# deployer queue channel
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel_deployer = connection.channel()
channel_deployer.queue_declare(queue='deployer')
#telegram token for bot
token = os.environ['token']
chat_id = '165756165'
logging.info('Token: %s' %token)
  #initialize bot
bot = telepot.Bot(token)
MessageLoop(bot, {'chat': handler,
                  'callback_query': bot_callback}).run_as_thread()
logging.info('bot started listening')
bot.sendMessage(chat_id, 'container started')
# ask how to collect vars process?
'''keyboard = InlineKeyboardMarkup(inline_keyboard=[
               [InlineKeyboardButton(text='start cluster_ip: %s' %envars['cluster_ip'], callback_data='checkcluster')],
           ])'''
bot.sendMessage(chat_id, 'send variables')
waiting_for_vars = True
# Rabbitmq reply channel init
channel_reply = connection.channel()
channel_reply.queue_declare(queue='reply')
channel_reply.basic_consume(reply_queue_callback, queue='reply', no_ack=True)
logging.info('consumer started. listening..')
channel_reply.start_consuming()


