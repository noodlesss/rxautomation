import pika, json, requests, threading, logging
from amnesia import nutanixApiv3

#telegram import libraries
import telepot, time, re, sys
from telepot.loop import MessageLoop, Orderer
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.delegate import (
    per_chat_id, per_callback_query_origin, create_open, pave_event_space)

#logging config
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)

#bot config
token = '168023423:AAFa-zgvR_8Xw8iRuyG2QxIyQdNCwMqDHA8'
bot = telepot.Bot(token)
chat_id = '165756165'



#publisher 
def publisher(message):
    connection_reply = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel_reply = connection_reply.channel()
    channel_reply.queue_declare(queue='reply')
    channel_reply.basic_publish(exchange='',
                      routing_key='reply',
                      body=json.dumps(message))
    logging.info('publisher started')
    

#checking to see if cluster install is finished, so we can run actions.
def check_cluster_status(base_url, username, password):
    api = nutanixApiv3(base_url, username, password)
    while True:
        try:
            data = api.network_list()
            print(data.status_code, data.text)
            if data.status_code == 200:
                print('counting...')
                time.sleep(120)
                print('True')
                return True
            else:
                print('waiting...')
                time.sleep(900)
        except requests.exceptions.ConnectTimeout as e:
            print('waiting')
            time.sleep(900)


def callback(ch, method, properties, body):
    body = json.loads(body)
    print ("[x] Received %r" % body)
    action = body['action']
    if action == 'checkcluster':
        cluster_status = check_cluster_status(body['data']['base_url'], body['data']['username'], body['data']['password'])
        if cluster_status == True:
            publisher(json.dumps({'task':'cluster_status', 'result': 'cluster up'}))
        else:
            publisher(json.dumps({'task':'cluster_status', 'result': 'check failed'}))
    print (" [x] Done")


connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='deployer')
channel.basic_consume(callback, queue='deployer', no_ack=True)
logging.info('consumer started. listening..')
channel.start_consuming()




