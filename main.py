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

def callback(ch, method, properties, body):
    body = json.loads(body)
    botik.bot.sendMessage(chat_id, body)
    logging.INFO('task: %s\n result: %s') %(body['task'], body['result'])

class Botik(object):
    def __init__(self, token, api3_vars):
        self.token = token
        self.connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        self.channel = self.connection.channel()
        self.channel.queue_declare(queue='deployer')
        self.api3_vars = api3_vars
        self.bot = telepot.Bot(self.token)
        MessageLoop(self.bot, {'chat': self.handler,
                  'callback_query': self.callback}).run_as_thread()
        logging.info('bot started listening')


    def handler(self, msg):
        print(msg['text'])


    def callback(self, msg):
        print(msg)
        query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
        logging.info('Callback Query: %s' %(query_data))
        if query_data == 'start':    ## checking call back data, and starting cluster status check process
            message = {'action':'checkcluster', 'data':self.api3_vars}
            self.channel.basic_publish(exchange='',
                      routing_key='hello',
                      body=json.dumps(message))
            self.bot.answerCallbackQuery(query_id, text='action %s send to queue' %message['action'])


def main():
    # Log object
    logging.basicConfig(filename='telegram_ctr.log', format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)
    #init vars
    print(os.environ.keys)
    network_vars = network()
    pc_vars = pc()
    api3_vars = api3()
    api2_vars = api2()
    deploy_ctr_ip = os.environ['deploy_ctr_ip']
    #telegram token for bot
    token = '168023423:AAFa-zgvR_8Xw8iRuyG2QxIyQdNCwMqDHA8'
    logging.info('Token: %s' %token)
    #initialize bot
    botik = Botik(token, api3_vars)
    chat_id = '165756165'
    logging.info('container started')
    botik.bot.sendMessage(chat_id, 'container started')
    logging.info('bot started listening')
    # start checking process?
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text='start cluster_ip: %s' %api3_vars['cluster_ip'], callback_data='start')],
               ])
    botik.bot.sendMessage(chat_id, 'a', reply_markup=keyboard)
    # while loop to keep bot listening..
    connection_reply = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel_reply = connection_reply.channel()
    channel_reply.queue_declare(queue='reply')
    channel_reply.basic_consume(callback, queue='reply', no_ack=True)
    logging.INFO('consumer started. listening..')
    channel_reply.start_consuming()

    





if __name__ == '__main__':
    main()


