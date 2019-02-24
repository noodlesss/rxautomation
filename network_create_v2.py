import json, requests
from nutanixv2api import nutanixApi

body = {
          "annotation": "autodeployed",
          "ip_config": {
            "default_gateway": "10.10.160.1",
            "dhcp_options": {
              "domain_name_servers": "8.8.8.8,4.4.4.4"
            },
            "network_address": "10.10.160.0",
            "pool": [
              {
                "range": "10.10.160.10 10.10.160.20"
              }
            ],
            "prefix_length": 24
          },
          "name": "autodeployed",
          "vlan_id": 0
    }


def netcreate(network):
  url = network['apidata']['base_url']
  username = network['apidata']['username']
  password = network['apidata']['password']
  api = nutanixApi(url, username, password)
  body['vlan_id'] = network['data']['vlan_id']
  body['ip_config']['pool'][0]['range'] = network['data']['range'].replace('-',' ')
  body['ip_config']['default_gateway'] = network['data']['default_gateway']
  body['ip_config']['prefix_length'] = network['data']['prefix_length']
  body['ip_config']['network_address'] = network['data']['network_address']
  body['ip_config']['dhcp_options']['domain_name_servers'] = network['data']['domain_name_servers']
  body['name'] = network['data']['name']
  data = api.network_create(body)
  return data