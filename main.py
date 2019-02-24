import os,json, time, logging, requests, pika
#telegram import libraries
import telepot, time, re, sys
from telepot.loop import MessageLoop, Orderer
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.delegate import (
    per_chat_id, per_callback_query_origin, create_open, pave_event_space)


# read network variables from environment variables that passed to container during run.
def network():
    network = {
        'vlan_id': os.environ['vlan_id'],
        'range': os.environ['range'],
        'default_gateway': os.environ['default_gateway'],
        'prefix_length': os.environ['prefix_length'],
        'network_address': os.environ['network_address'],
        'domain_name_servers': os.environ['domain_name_servers'],
        'name': os.environ['name']
        }
    return network

# read vars for pc from env vars
def pc():
    pc_vars = {
        'pc_ip': os.environ['pc_ip'],
        'cluster_ip': os.environ['cluster_ip'],
        'username': os.environ['username'],
        'password': os.environ['password'],
        'base_url': "https://%s:9440/api/nutanix/v3/" %os.environ['cluster_ip']    
    }
    return pc_vars

def api3():
    cluster_vars = {
        'cluster_ip': os.environ['cluster_ip'],
        'username': os.environ['username'],
        'password': os.environ['password'],
        'base_url': "https://%s:9440/api/nutanix/v3/" %os.environ['cluster_ip']    
    }
    return cluster_vars

def api2():
    cluster_vars = {
        'cluster_ip': os.environ['cluster_ip'],
        'username': os.environ['username'],
        'password': os.environ['password'],
        'base_url': "https://%s:9440/PrismGateway/services/rest/v2.0/" %os.environ['cluster_ip'] 
    }
    return cluster_vars

# Rabbitmq queue callback
def con_callback(ch, method, properties, body):
    body = json.loads(body)
    logging.info('task: %s\n result: %s') %(body['task'], body['result'])
    if body['task'] == 'cluster_status' and body['result'] == 'cluster up':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
               [InlineKeyboardButton(text='Create network', callback_data='create_network')],
           ])
        bot.sendMessage(chat_id, 'cluster %s:\n ' %api3_vars['cluster_ip'], reply_markup=keyboard)
    else:
        bot.sendMessage(chat_id, body)



        

# Telegram handler
def handler(msg):
    print(msg['text'])

# Telegram callback
def callback(msg):
    print(msg)
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    logging.info('Callback Query: %s' %(query_data))
    if query_data == 'start':    ## checking call back data, and starting cluster status check process
        message = {'action':'checkcluster', 'apidata':api3_vars}
        channel_deployer.basic_publish(exchange='',
                  routing_key='deployer',
                  body=json.dumps(message))
        bot.answerCallbackQuery(query_id, text='action %s send to queue' %message['action'])
    elif query_data == 'create_network':
        message = {'action':'create_network', 'data':network_vars, 'apidata': api2_vars}
        channel_deployer.basic_publish(exchange='',
                  routing_key='deployer',
                  body=json.dumps(message))
        bot.answerCallbackQuery(query_id, text='action %s send to queue' %message['action'])


# Log object
logging.basicConfig(filename='main_ctr.log', format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)
logging.info('container started')
#init vars
logging.info('envars: %s' % os.environ.keys)
network_vars = network()
pc_vars = pc()
api3_vars = api3()
api2_vars = api2()
#telegram token for bot
token = '168023423:AAFa-zgvR_8Xw8iRuyG2QxIyQdNCwMqDHA8'
chat_id = '165756165'
logging.info('Token: %s' %token)
  #initialize bot
bot = telepot.Bot(token)
MessageLoop(bot, {'chat': handler,
                  'callback_query': callback}).run_as_thread()
logging.info('bot started listening')
bot.sendMessage(chat_id, 'container started')
# deployer queue channel
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel_deployer = connection.channel()
channel_deployer.queue_declare(queue='deployer')
# start checking process?
keyboard = InlineKeyboardMarkup(inline_keyboard=[
               [InlineKeyboardButton(text='start cluster_ip: %s' %api3_vars['cluster_ip'], callback_data='start')],
           ])
bot.sendMessage(chat_id, 'a', reply_markup=keyboard)
# while loop to keep bot listening..
channel_reply = connection.channel()
channel_reply.queue_declare(queue='reply')
channel_reply.basic_consume(con_callback, queue='reply', no_ack=True)
logging.info('consumer started. listening..')
channel_reply.start_consuming()


