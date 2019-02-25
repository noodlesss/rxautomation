import pika, json, requests, threading, logging, network_create_v2
from amnesia import nutanixApiv3


#telegram import libraries
import telepot, time, re, sys
from telepot.loop import MessageLoop, Orderer
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.delegate import (
    per_chat_id, per_callback_query_origin, create_open, pave_event_space)

#logging config
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)




#publisher 
def publisher(message):
    connection_reply = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel_reply = connection_reply.channel()
    channel_reply.queue_declare(queue='reply')
    channel_reply.basic_publish(exchange='',
                      routing_key='reply',
                      body=json.dumps(message))
    logging.info('published result %s' %message)
    

#checking to see if cluster install is finished, so we can run actions.
def check_cluster_status(base_url, username, password):
    api = nutanixApiv3(base_url, username, password)
    while True:
        try:
            data = api.network_list()
            if data.status_code == 200:
                logging.info('counting...')
                time.sleep(120)
                logging.info('True')
                return True
            else:
                logging.info('waiting...')
                time.sleep(900)
        except (requests.exceptions.ConnectTimeout, urllib3.exceptions.MaxRetryError) as e:
            logging.info('waiting')
            time.sleep(900)


def callback(ch, method, properties, body):
    body = json.loads(body)
    logging.info("[x] Received %r" % body)
    action = body['action']
    if action == 'checkcluster':    # check cluster  status
        cluster_status = check_cluster_status(body['apidata']['base_url'], body['apidata']['username'], body['apidata']['password'])
        if cluster_status == True:
            publisher({'task':'cluster_status', 'result': 'cluster up'})
        else:
            publisher({'task':'cluster_status', 'result': 'check failed'})
    elif action == 'create_network':  # create network 
        create_network = network_create_v2.netcreate(body)
        publisher({'task': 'create_network', 'result': create_network.status_code}) # status codee 201 means task accepted. 
    elif action == 'deploy_pc':  # deploy pc
        pc = deploy_pc.
    logging.info(" [x] Done")


# init Rabbitmq queue and listen for commands.
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='deployer')    # deployer queue for actions to run on cluster
channel.basic_consume(callback, queue='deployer', no_ack=True)
logging.info('consumer started. listening..')
channel.start_consuming()




