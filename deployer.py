import pika, json, requests, threading, logging, network_create_v2, deploy_prism_central, time, datetime
from amnesia import nutanixApiv3
from nutanixv2api import nutanixApi

#telegram import libraries
import telepot, time, re, sys
from telepot.loop import MessageLoop, Orderer
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.delegate import (
    per_chat_id, per_callback_query_origin, create_open, pave_event_space)

#logging config
logging.basicConfig(filename='d.log', format='%(asctime)s:%(levelname)s:%(message)s', level=logging.INFO)

threads = []

task_check_action_list = ['deploypc', 'register_pc']

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
    username = body['data']['username']
    password = body['data']['password']
    base_url = body['data']['base_url']
    action = body['action']
    api = nutanixApiv3(base_url, username, password)
    n = 0
    while n < 3:
        data = api.task_status(task_uuid)
        if data.status_code == 200 and data.json()['status'] == 'SUCCEEDED':
            publisher({'task': action, 'result': 'SUCCEEDED'})
            return
        elif data.status_code == 200 and data.json()['status'] == 'RUNNING':
            logging.info('task status: RUNNING' )
            logging.info('task check sleeping 2 minutes')
            time.sleep(120)
        else:
            logging.info('task status: %s' %data.text)
            n+=1
            time.sleep(60)
    return

# thread creator
def thread_func(task_uuid, body):
    t = threading.Thread(target=check_task_status, args=(task_uuid, body))
    threads.append(t)
    t.start()

#checking to see if cluster install is finished, so we can run actions.
def check_cluster_status(body):
    username = body['data']['username']
    password = body['data']['password']
    base_url = body['data']['base_url']
    api = nutanixApiv3(base_url, username, password)
    # calculating how many seconds we should wait to start the check process. 
    # current time will be subtracted from start date. Result will be passed to time.sleep.
    start_date = body['data']['start_date']
    start_time_in_epoch = datetime.datetime.strptime(start_date, '%Y-%m-%d %H:%M').timestamp()
    logging.info('start date: %s' %start_date)
    if start_time_in_epoch > time.time():
      wait_until_start_seconds = start_time_in_epoch - time.time()
      logging.info('waiting: %s' %wait_until_start_seconds)
      logging.info('start time epoch: %s, time now: %s' %(start_time_in_epoch, time.time()))
      time.sleep(wait_until_start_seconds+10)
    while True:
        logging.info('starting cluster status check')
        try:
            data = api.network_list()
            if data.status_code == 200:
                logging.info('Cluster is up. One minute please..')
                time.sleep(60)
                publisher({'task':'checkcluster', 'result': 'cluster up'})
                return True
            elif data.status_code == 401:
                logging.info('cluster check: auth error')
                publisher({'task':'checkcluster', 'result': 'check failed with auth'})
                return False
            else:
                logging.info('CLuster is not ready. sleeping 15 mins...')
                time.sleep(900)
        except (requests.exceptions.ConnectTimeout, requests.exceptions.ConnectionError) as e:
            logging.info('exception - %s\n sleeping 15 mins' %e)
            publisher({'task' : 'cluster_status', 'result': 'error: %s' %e})
            time.sleep(900)


## Set public key
def set_pub_key(body):
    name = 'nuran'
    with open('.ssh/nn.pub') as f:
        key = f.read()
    username = body['data']['username']
    password = body['data']['password']
    base_url = body['data']['base_url']
    api = nutanixApi(base_url, username, password)
    data = api.set_pub_key(name, key)
    return data

def callback(ch, method, properties, body):
    body = json.loads(body)
    logging.info("[x] Received %r" % body)
    action = body['action']
    try:
        action_func = action_list[action] # assign function according to action
    except Exception as e:
        logging.error('DID NOT FIND FUNCTION/ACTION: %s' %e)
        publisher({'task':action, 'result': 'error: %e' %e})
    try:
        action_result = action_func(body) # action function called
    except Exception as e:
        logging.error('ERROR IN ACTION FUNCTION %s' %e)
        publisher({'task':action, 'result': 'error: %s' %e})
    # after action returns, select action task checker below
    if action == 'checkcluster':
        pass
    elif action not in task_check_action_list:
        publisher({'task': action, 'result': action_result.text})
    elif action in task_check_action_list:
        if action_result.status_code == 201 or action_result.status_code == 202:
            task_uuid = action_result.json()['task_uuid']
            thread_func(task_uuid, body) # create thread to check task status based on uuid
    logging.info('action result %s' %action_result)
    logging.info(" [x] Done")


action_list = {
    'checkcluster': check_cluster_status,
    'create_network': network_create_v2.netcreate,
    'deploypc': deploy_prism_central.deploy_pc,
    'register_pc': deploy_prism_central.register_pc,
    'set_pub_key': set_pub_key
}

# init Rabbitmq queue and listen for commands.
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='deployer')    # deployer queue for actions to run on cluster
channel.basic_consume(callback, queue='deployer', no_ack=True)
logging.info('consumer started. listening..')
channel.start_consuming()

'''

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
            task_uuid = deploypc.json()['task_uuid']
            thread_func(task_uuid, body, check_task_status)
'''


