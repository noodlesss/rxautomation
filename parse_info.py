import re, os, logging
from datetime import datetime


def get_vars_from_bot(al):
    try:
        for i in al:
            if re.match('Start Date:', i):
                start_date = re.search(r'2019-\d\d-\d\d \d\d:\d\d', i).group()
                logging.info(start_date)
            elif re.match('Cluster IP:', i):
                cluster_ip = re.search(r'\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}', i).group()
            elif re.match('Prism UI Credentials:', i):
                password = re.search(r'nx2Tech.*', i).group()
            elif re.match('Gateway:', i):
                gateway_ip = re.search(r'\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}',i).group()
                network_address = re.search(r'\d{1,3}.\d{1,3}.\d{1,3}.',o).group() +'0'
            elif re.match('Secondary Gateway:', i):
                secondary_gw = re.search(r'\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3}', i).group()
            elif re.match('Secondary IP Range:', i):
                network = re.search(r'(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})-(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})', i).group()
                pc_ip = re.search(r'(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})-(\d{1,3}.\d{1,3}.\d{1,3}.\d{1,3})', i).group(1)
    except Exception as e:
        logging.error('could not parse vars\nTraceback:%s' %e)
        return False
    variables = {'start_date': start_date,
                'cluster_ip': cluster_ip,
                'password': password,
                'username': 'admin',
                'default_gateway': gateway_ip,
                'range': network,
                'base_url': "https://%s:9440/api/nutanix/v3/" %cluster_ip,
                'api2_base_url': "https://%s:9440/PrismGateway/services/rest/v2.0/" %cluster_ip,
                'pc_ip': pc_ip,
                'vlan_id': 0,
                'prefix_length': 22,
                'domain_name_servers': os.environ['domain_name_servers'],
                'name': os.environ['name'],
                'network_address': network_address
                }
    return variables


'''if datetime.datetime.now() > datetime.datetime.strptime(sds, '%Y-%m-%d %H:%M'):
    # start process
    pass '''
