import os


# read network variables from environment variables that passed to container during run.


def envars():
    environment_vars = {
        'cluster_ip': os.environ['cluster_ip'],
        'username': os.environ['username'],
        'password': os.environ['password'],
        'base_url': "https://%s:9440/api/nutanix/v3/" %os.environ['cluster_ip'],
        'api2_base_url': "https://%s:9440/PrismGateway/services/rest/v2.0/" %os.environ['cluster_ip'],
        'pc_ip': os.environ['pc_ip'],
        'vlan_id': os.environ['vlan_id'],
        'range': os.environ['range'],
        'default_gateway': os.environ['default_gateway'],
        'prefix_length': os.environ['prefix_length'],
        'network_address': os.environ['network_address'],
        'domain_name_servers': os.environ['domain_name_servers'],
        'name': os.environ['name']
    }
    return environment_vars



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
        'base_url': "https://%s:9440/api/nutanix/v3/" %os.environ['cluster_ip'],    
        'default_gateway': os.environ['default_gateway']
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