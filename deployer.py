import pika, json, requests, threading, logging, network_create_v2, deploy_prism_central, time
from amnesia import nutanixApiv3


#telegram import libraries
import telepot, time, re, sys
from telepot.loop import MessageLoop, Orderer
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.delegate import (
    per_chat_id, per_callback_query_origin, create_open, pave_event_space)

#logging config
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)

threads = []


#publisher 
def publisher(message):
    connection_reply = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel_reply = connection_reply.channel()
    channel_reply.queue_declare(queue='reply')
    channel_reply.basic_publish(exchange='',
                      routing_key='reply',
                      body=json.dumps(message))
    logging.info('published result %s' %message)
    
#thread function for task status check
def check_task_status(task_uuid, body):
    username = body['apidata']['username']
    password = body['apidata']['password']
    base_url = body['apidata']['base_url']
    api = nutanixApiv3(base_url, username, password)
    n = 0
    while n < 3:
        data = api.task_status(task_uuid)
        if data.status_code == 200 and data.json()['status'] == 'COMPLETE':
            publisher({'task': 'deploy_pc', 'result': 'completed'})
            return
        elif data.status_code == 200 and data.json()['status'] == 'RUNNING':
            logging.info('task status: RUNNING' )
            logging.info('task check sleeping 2 minutes')
            time.sleep(120)
        else:
            logging.info('task status: %s' %data.text)
            n+=1
    return

# thread creator
def thread_func(task_uuid, body):
    t = threading.Thread(target=check_task_status, args=(task_uuid, body))
    threads.append(t)
    t.start()

#checking to see if cluster install is finished, so we can run actions.
def check_cluster_status(body):
    username = body['apidata']['username']
    password = body['apidata']['password']
    base_url = body['apidata']['base_url']
    api = nutanixApiv3(base_url, username, password)
    while True:
        try:
            data = api.network_list()
            if data.status_code == 200:
                logging.info('one minute please..')
                time.sleep(60)
                logging.info('True')
                return True
            else:
                logging.info('CLuster is not ready. sleeping 15 mins...')
                time.sleep(900)
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError) as e:
            logging.info('exception - %s\n sleeping 15 mins' %e)
            publisher({'task' : 'cluster_status', 'result': 'error: %s' %e})
            time.sleep(900)


def callback(ch, method, properties, body):
    body = json.loads(body)
    logging.info("[x] Received %r" % body)
    action = body['action']
    if action == 'checkcluster':    # check cluster  status
        cluster_status = check_cluster_status(body)
        if cluster_status == True:
            publisher({'task':'cluster_status', 'result': 'cluster up'})
        else:
            publisher({'task':'cluster_status', 'result': 'check failed'})
    elif action == 'create_network':  # create network 
        create_network = network_create_v2.netcreate(body)
        publisher({'task': 'create_network', 'result': create_network.status_code}) # status code 201 means task accepted. 
    elif action == 'deploy_pc':  # deploy pc
        deploypc = deploy_prism_central.deploy_pc(body)
        publisher({'task': 'deploy_pc', 'result': deploypc.status_code}) # status code publsihed to main
        if deploypc.status_code == 202:
            task_uuid = deploypc.json()
            thread_func(task_uuid, body)
    logging.info(" [x] Done")


# init Rabbitmq queue and listen for commands.
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='deployer')    # deployer queue for actions to run on cluster
channel.basic_consume(callback, queue='deployer', no_ack=True)
logging.info('consumer started. listening..')
channel.start_consuming()




