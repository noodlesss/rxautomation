import pika, json, requests
from amnesia import nutanixApiv3

#telegram import libraries
import telepot, time, re, sys
from telepot.loop import MessageLoop, Orderer
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.delegate import (
    per_chat_id, per_callback_query_origin, create_open, pave_event_space)


connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='hello')


bot = telepot.Bot(token)
token = '168023423:AAFa-zgvR_8Xw8iRuyG2QxIyQdNCwMqDHA8'
chat_id = '165756165'

#checking to see if cluster install is finished, so we can run actions.
def check_cluster_status(base_url, username, password):
    api = nutanixApiv3(base_url, username, password)
    while True:
        try:
            data = api.network_list()
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
    print ("[x] Received %r" % body)
    action = body['action']
    if action == 'checkcluster':
        cluster_status = check_cluster_status(body['base_url'], body['username'], body['password'])
        if cluster_status == True:
            bot.sendMessage(chat_id, 'cluster ready')
        else:
        	bot.sendMessage(chat_id, 'check failed')
    print (" [x] Done")


channel.basic_consume(callback, queue='hello', no_ack=True)
print ('listening')
channel.start_consuming()




