import os, time, logging, requests
#telegram import libraries
import telepot, time, re, sys
from telepot.loop import MessageLoop, Orderer
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
from telepot.delegate import (
    per_chat_id, per_callback_query_origin, create_open, pave_event_space)


# initialize Deploy(ctr) object.
class Deploy(object):
    def __init__(self, deploy_ctr_ip):
        self.base_url = 'http://%s:8000/deployer' %deploy_ctr_ip
        self.deploy_ctr_ip = deploy_ctr_ip
        requests.packages.urllib3.disable_warnings()
        self.s = requests.Session()
        #self.s.auth = (self.username, self.password)
        self.s.headers.update({'Content-Type': 'application/json; charset=utf-8'})
        

    # Send check cluster request to deployer ctr
    def check_cluster_status(self, body):
        print('check cluster status, body: %s' %body)
        return 'checking cluster status'
        
    def __str__(self):
        return self.deploy_ctr_ip

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

    

def handler(msg):
    print(msg['text'])


def callback(msg):
    nonlocal api2_vars
    print(msg)
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print('Callback Query:', query_id, from_id, query_data)
    if query_data == 'start':    ## checking call back data, and starting cluster status check process
        cluster_status = deploy.check_cluster_status(api2_vars)    ## sending api2vars to deploy.check_cluster_status call to send to deployer ctr. 
        bot.answerCallbackQuery(query_id, text='data: %s' %cluster_status)


def main():
    # Log object
    logging.basicConfig(filename='telegram_ctr.log', format='%(asctime)s:%(levelname)s:%(message)s', level=6)
    #init vars
    print(os.environ.keys)
    network_vars = network()
    pc_vars = pc()
    api3_vars = api3()
    api2_vars = api2()
    deploy_ctr_ip = os.environ['deploy_ctr_ip']
    # Initialize Deploy object
    global deploy # declaring deploy global to make sure that callback function can access it
    deploy = Deploy(deploy_ctr_ip)
    print(deploy)
    logging.info('initialized deploy object')
    #telegram token for bot
    token = '168023423:AAFa-zgvR_8Xw8iRuyG2QxIyQdNCwMqDHA8'
    logging.info('Token: %s' %token)
    #initialize bot
    bot = telepot.Bot(token)
    chat_id = '165756165'
    logging.info('container started')
    bot.sendMessage(chat_id, 'container started')
    MessageLoop(bot, {'chat': handler,
                  'callback_query': callback}).run_as_thread()
    logging.info('bot started listening')
    # start checking process?
    keyboard = InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text='start cluster_ip: %s' %api3_vars['cluster_ip'], callback_data='start')],
               ])
    bot.sendMessage(chat_id, 'a', reply_markup=keyboard)
    # while loop to keep bot listening..
    while 1:
        time.sleep(10)

    





if __name__ == '__main__':
    main()


