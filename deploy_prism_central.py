import json, requests, logging
from amnesia import nutanixApiv3

pc_body = {  
      "resources":{  
        "version":"5.10.0.1",
        "should_auto_register":False,
        "pc_vm_list":[  
          {  
            "vm_name":"pc_api",
            "container_uuid":"ctr_uuid",
            "num_sockets":4,
            "data_disk_size_bytes":536870912000,
            "memory_size_bytes":17179869184,
            "dns_server_ip_list":[  
              "8.8.8.8",
              "8.8.4.4"
            ],
            "nic_list":[  
              {  
                "ip_list":[  
                  "pc_ip"
                ],
                "network_configuration":{  
                  "network_uuid":"net_uuid",
                  "subnet_mask":"255.255.252.0",
                  "default_gateway":"10.63.28.1"
                }
              }
            ]
          }
        ]
      }
    }


def deploy_pc(body):
    username = body['apidata']['username']
    password = body['apidata']['password']
    pc_ip = body['data']['pc_ip']
    api2_url = body['api2data']['base_url']
    base_url = body['apidata']['base_url']
    default_gateway = body['data']['default_gateway']
    api = nutanixApiv3(base_url, username, password)
  ## GETTING RX-AUtomation-Network uuid from cluster
    data = api.network_list()
    try:
      data = data.json()
      for i in data['entities']:
        if i['status']['name'] == 'autonet':
          net_uuid = i['metadata']['uuid']
          logging.info('net = %s' %net_uuid)
          break
    except Exception as e:
      logging.info(data, e)
  ## GETTING SelfServiceContainer uuid from cluster
    data_ctr = api.ctr_list(api2_url)
    try:
      ctrlist = data_ctr.json()
      for i in ctrlist['entities']:
        if i['name'] == 'SelfServiceContainer':
          ctr_uuid = i['storage_container_uuid']
          logging.info('ctr = %s' %ctr_uuid)
          break
    except Exception as e:
      logging.info(data_ctr, e)
  ## DEPLOY PC
    pc_body['resources']['pc_vm_list'][0]['container_uuid'] = ctr_uuid
    pc_body['resources']['pc_vm_list'][0]['nic_list'][0]['ip_list'][0] = pc_ip
    pc_body['resources']['pc_vm_list'][0]['nic_list'][0]['network_configuration']['network_uuid'] = net_uuid
    pc_dep = api.pc_deploy(pc_body)
    return pc_dep