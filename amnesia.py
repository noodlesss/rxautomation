import json, requests


class nutanixApiv3(object):
  def __init__(self, base_url, username, password):
    self.base_url = base_url
    self.username = username
    self.password = password

  def vm_create(self, body):
    '''required params in body:
            {memory_mb, name, num_vcpus ,cluster_reference{kind, uuid}, metadata{"kind": "vm"}}
    '''
    requests.packages.urllib3.disable_warnings()
    s = requests.Session()
    s.auth = (self.username, self.password)
    s.headers.update({'Content-Type': 'application/json; charset=utf-8'})
    data = s.post(self.base_url + 'vms', json=body, verify=False)
    return data

  def vm_update(self, vm_uuid, body):
    '''required params in body:
        {memory_mb, name, num_vcpus ,cluster_reference{kind, uuid},  metadata{"kind": "vm", "spec_version"}, "hardware_clock_timezone"}
    '''
    requests.packages.urllib3.disable_warnings()
    s = requests.Session()
    s.auth = (self.username, self.password)
    s.headers.update({'Content-Type': 'application/json; charset=utf-8'})
    data = s.put(self.base_url + 'vms/%s' %vm_uuid, json=body, verify=False)
    return data

  def net_create(self, body):
    requests.packages.urllib3.disable_warnings()
    s = requests.Session()
    s.auth = (self.username, self.password)
    s.headers.update({'Content-Type': 'application/json; charset=utf-8'})
    data = s.post(self.base_url + 'subnets', json=body, verify=False)
    return data

  def pc_deploy(self, body):
    '''network_uuid is required field'''
    requests.packages.urllib3.disable_warnings()
    s = requests.Session()
    s.auth = (self.username, self.password)
    s.headers.update({'Content-Type': 'application/json; charset=utf-8'})
    data = s.post(self.base_url + 'prism_central' , json=body ,verify=False)
    return data

  def network_list(self):
    requests.packages.urllib3.disable_warnings()
    s = requests.Session()
    s.auth = (self.username, self.password)
    s.headers.update({'Content-Type': 'application/json; charset=utf-8'})
    body = {
      "kind": "subnet"
    }
    data = s.post(self.base_url + 'subnets/list' , json=body ,verify=False)
    return data

  def ctr_list(self, url):
    requests.packages.urllib3.disable_warnings()
    s = requests.Session()
    s.auth = (self.username, self.password)
    s.headers.update({'Content-Type': 'application/json; charset=utf-8'})
    data = s.get(url + 'storage_containers/' ,verify=False)
    return data


  def task_status(self, task_uuid):
    requests.packages.urllib3.disable_warnings()
    s = requests.Session()
    s.auth = (self.username, self.password)
    s.headers.update({'Content-Type': 'application/json; charset=utf-8'})
    data = s.get(self.base_url + 'tasks/%s' %task_uuid, verify=False)
    return data



class nutanixApiv1(object):
  def __init__(self, cluster_ip, username, password):
    self.base_url = 'https://%s:9440/PrismGateway/services/rest/v1/' %cluster_ip
    self.username = username
    self.password = password

  def pc_register(self, body):
    requests.packages.urllib3.disable_warnings()
    s = requests.Session()
    s.auth = (self.username, self.password)
    s.headers.update({'Content-Type': 'application/json; charset=utf-8'})
    data = s.post(self.base_url + 'multicluster/prism_central/register', json=body, verify=False)
    return data





