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


def netcreate(url, username, password, network):
	api = nutanixApi(url, username, password)
	body['vlan_id'] = network['vlan_id']
	body['pool'][0]['range'] = network['range'].replace('-',' ')
	body['default_gateway'] = network['default_gateway']
	body['prefix_length'] = network['prefix_length']
	body['network_address'] = network['network_address']
	body['dhcp_options']['domain_name_servers'] = network['domain_name_servers']
	body['name'] = network['name']
	data = api.network_create(body)
	return data