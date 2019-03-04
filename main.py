import os,json, time, logging, requests, pika
# import variable constructors
import var_construct
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
    if body['task'] == 'cluster_status' and body['result'] == 'cluster up':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
               [InlineKeyboardButton(text='Create network', callback_data='create_network')], 
               [InlineKeyboardButton(text='Deploy Prism Central', callback_data='deploy_pc')]
           ])
        bot.sendMessage(chat_id, 'cluster %s:\n ' %envars['cluster_ip'], reply_markup=keyboard)
    else:
        bot.sendMessage(chat_id, '%s: %s' %(body['task'], body['result']))


# Telegram handler
def handler(msg):
    print(msg['text'])

# Telegram callback
def bot_callback(msg):
    print(msg)
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    logging.info('Callback Query: %s' %(query_data))
    message = {'action': query_data, 'data': envars}
    channel_deployer.basic_publish(exchange='',
                  routing_key='deployer',
                  body=json.dumps(message))
    bot.answerCallbackQuery(query_id, text='action %s send to queue' %message['action'])

# Log object
logging.basicConfig(filename='main_ctr.log', format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)
logging.info('container started')
#init vars
logging.info('envars: %s' % os.environ.keys)
envars = var_construct.envars()
# deployer queue channel
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel_deployer = connection.channel()
channel_deployer.queue_declare(queue='deployer')
#telegram token for bot
token = '168023423:AAFa-zgvR_8Xw8iRuyG2QxIyQdNCwMqDHA8'
chat_id = '165756165'
logging.info('Token: %s' %token)
  #initialize bot
bot = telepot.Bot(token)
MessageLoop(bot, {'chat': handler,
                  'callback_query': bot_callback}).run_as_thread()
logging.info('bot started listening')
bot.sendMessage(chat_id, 'container started')
# start checking process?
keyboard = InlineKeyboardMarkup(inline_keyboard=[
               [InlineKeyboardButton(text='start cluster_ip: %s' %envars['cluster_ip'], callback_data='start')],
           ])
bot.sendMessage(chat_id, 'a', reply_markup=keyboard)
# Rabbitmq reply channel init
channel_reply = connection.channel()
channel_reply.queue_declare(queue='reply')
channel_reply.basic_consume(reply_queue_callback, queue='reply', no_ack=True)
logging.info('consumer started. listening..')
channel_reply.start_consuming()


