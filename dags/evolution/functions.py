import requests
import json
import yaml

def get_access_key(config):
    access_key = None
    if config.has_option('connection', 'access_key'):
        access_key = config['connection']['access_key'] if config['connection']['access_key'] not in [None, ''] else None
    return access_key

def get_secret_key(config):
    secret_key = None
    if config.has_option('connection', 'secret_key'):
        secret_key = config['connection']['secret_key']
    return secret_key

def get_access_token(config):
    access_token = None
    iam = config['connection']['iam']
    access_key = get_access_key(config)
    secret_key = get_secret_key(config)
    exportpath = config["exportpath"]
    try:
        access_token = get_cloud_iam_access_token(iam=iam, access_key=access_key, secret_key=secret_key)
    except Exception as err:
        print(err)
    else:
        # Закомментировать если не требуется сохранять ключ
        try:
           with open(f'{exportpath}/key.txt', 'w', encoding='utf-8') as outfile:
               outfile.write(access_token)
        except Exception as err:
           print(err)
    return access_token

def get_prefix(config):
    prefix = None
    if config.has_option('params', 'root'):
        prefix = (config['params']['root'] + '.') if config['params']['root'] not in (None, '') else ''
    if config.has_option('params', 'domain'):
        prefix = (prefix + config['params']['domain'] + '.') if config['params']['domain'] not in (None, '') else ''
    return prefix

# Вычисляем адрес сети
def get_cidr(*args):
    addr = args[0] if args[0] != '' else "0.0.0.0"
    mask = args[1] if args[1] != '' else "0.0.0.0"

    addr = [int(x) for x in addr.split(".")]
    mask = [int(x) for x in mask.split(".")]
    cidr = sum((bin(x).count('1') for x in mask))

    netw = [addr[i] & mask[i] for i in range(4)]

    result = "{0}/{1}".format(('.'.join(map(str, netw))), cidr)
    return result


# Аутентификация
def get_cloud_iam_access_token(**kwarg):
    iam = kwarg['iam']
    access_key = kwarg['access_key']
    secret_key = kwarg['secret_key']
    url = f'https://{iam}/auth/system/openid/token'
    header = {
        'Content-Type': 'application/x-www-form-urlencoded;charset=utf-8'
    }
    data = {
        'grant_type': 'access_key',
        'client_id': access_key,
        'client_secret': secret_key,
        'scope': 'openid'
    }
    try:
        resp = requests.post(url, headers=header, data=data)
    except Exception as err:
        print(err)
    access_token = resp.json().get("access_token")
    return access_token

def convert_cidr_to_netmask(cidr):
  cidr = int(cidr)
  mask = (0xffffffff >> (32 - cidr)) << (32 - cidr)
  return (str( (0xff000000 & mask) >> 24)   + '.' +
          str( (0x00ff0000 & mask) >> 16)   + '.' +
          str( (0x0000ff00 & mask) >> 8)    + '.' +
          str( (0x000000ff & mask)))

def get_evo_api(**kwarg):
    host = kwarg['host']
    bearer = kwarg['bearer']
    uri = kwarg['uri']
    query = 'https://' + host + uri
    header = {
        'Accept': f'application/json',
        'Authorization': 'Bearer ' + bearer
    }
    try:
        req = requests.get(query, headers=header)
    except Exception as err:
        print(err)
    return req

def get_pages(pagecount, query, access_token, api_init):
    result = []
    for page in range(2, pagecount + 1):
        query = query + f'&page={page}'
        try:
            r = get_evo_api(url=query, bearer=access_token, version=api_init)
            r_json = json.loads(r.text)
        except Exception as err:
            print(err)
        else:
             for item in r_json.get('values',''):
                result.append(item)
    return result


def export_orgs(config, access_token):

    evoapi = config['connection']['evoapi']
    prefix = get_prefix(config)
    dc = config['params']['DC']
    org = config['connection']['org']
    exportpath = config['params'].get('exportpath')

    orgs_list = {
        'seaf.ta.reverse.evo.orgs': {}
        }
    query = f'/api/v1/organizations/{org}'
    try:
        org_req = get_evo_api(host=evoapi, bearer=access_token, uri=query)
        org_json = json.loads(org_req.text)
    except Exception as err:
        print(err)
    else:
        print(f'First request status:{org_req.status_code}')
    
    org_id = org_json.get('id')
    yaml_structure = {
        'id': org_id,
        'title': org_id,
        'dc': dc
    }
    org_seaf_id = prefix + 'orgs.' + org_id
    orgs_list['seaf.ta.reverse.evo.orgs'][org_seaf_id] = yaml_structure
    save(orgs_list, exportpath, 'evolution_orgs')



def export_vms(config, access_token):

    evoapi = config['connection']['evoapi']
    prefix = get_prefix(config)
    project = config['connection']['project']
    exportpath = config['params'].get('exportpath')

    vms = []
    vms_list = {
        'seaf.ta.components.server': {}
    }
    try:
        vms_req = get_evo_api(host=evoapi, bearer=access_token, uri=f'/api/v1/vms?project_id={project}')
        vms_json = json.loads(vms_req.text)
    except Exception as err:
        print(err)
    else:
        print(f'First request status: {vms_req.status_code}')
    for item in vms_json.get('items',''):
        vms.append(item)
    
    for vm in vms:
        vm_id = vm.get('id', '')
        vm_req = get_evo_api(host=evoapi, bearer=access_token, uri=f'/api/v1/vms/{vm_id}?project_id={project}')
        vm_json = json.loads(vm_req.text)

        disks = []
        for disk in vm_json.get('disks'):
            disk_id = disk.get('id','0')
            disks.append({disk_id: {
                'device': disk.get('serial_id'),
                'size': int(disk.get('size')),
                'az': '',
                'type': disk.get('disk_type','').get('name','')
            }})

        addresses = []
        subnets = []
        subnetids = []
        for adapter in vm_json.get('interfaces'):
            if adapter.get('subnet') not in [None, 'None', '']:
                if adapter.get('subnet').get('name') not in subnets:
                    subnets.append(adapter.get('subnet').get('name'))
                if adapter.get('subnet').get('id') not in subnetids:
                    subnet_id = adapter.get('subnet').get('id')
                    subnetids.append(prefix + 'networks.' + subnet_id)
                    network_req = get_evo_api(host=evoapi, bearer=access_token, uri=f'/api/v1/subnets/{subnet_id}?project_id={project}')
                    network_yaml = json.loads(network_req.text)
                    vpc_id = network_yaml.get('vpc_id')
                    vpc_req = get_evo_api(host='console.cloud.ru/api/svp', bearer=access_token, uri=f'/vpc/v1/vpcs/{vpc_id}?projectId={project}')
                    vpc_yaml = json.loads(vpc_req.text)
                    vpc_name = vpc_yaml.get('name')
            if adapter.get('ip_address') not in addresses:
                addresses.append(adapter.get('ip_address'))

        computername = vm_json.get('name', '')

        yaml_structure = {
            'id': vm_id,
            'type': 'Виртуальный',
            'title': computername,
            'fqdn': computername,
            'description': vm_json.get('description',''),
            'os': {
                'type': vm_json.get('image', '').get('display_name', ''),
                'bit': ''
            },
            'cpu': {
                'cores': vm_json.get('flavor','').get('cpu',''),
                'frequency': '',
            },
            'ram': vm_json.get('flavor').get('ram'),
            'nic_qty': len(vm_json.get('interfaces')),
            'subnets': subnetids,
            'disks': disks,
            'reverse': {
                'reverse_type': 'Evolution',
                'original_id': vm_id,
                'flavor': vm_json.get('flavor').get('name'),
                'addresses': addresses,
                'subnet_titles': subnets,
                'tags': [],
                'vpc': prefix + 'vpcs.' + vpc_id,
                'vpc_title': vpc_name,
                'tenant': ''
            }
        }

        vm_seaf_id = prefix + 'vms.' + vm_id
        vms_list['seaf.ta.components.server'][vm_seaf_id] = yaml_structure
    save(vms_list, exportpath, 'evolution_vms')


def export_vpcs(config, access_token):

    prefix = get_prefix(config)
    project = config['connection']['project']
    dc = config['params']['DC']
    org = config['connection']['org']
    exportpath = config['params'].get('exportpath')

    vpcs_list = {'seaf.ta.reverse.evo.vpcs': {}}
    try:
        vpc_req = get_evo_api(host='console.cloud.ru/api/svp', bearer=access_token, uri=f'/vpc/v1/vpcs?projectId={project}')
        vpc_json = json.loads(vpc_req.text)
    except Exception as err:
        print(err)
    else:
        print(f'First request status:{vpc_req.status_code}')
    for vpc in vpc_json.get('vpcs'):
        vpc_id = vpc.get('id')
        yaml_structure = {
            'id': vpc_id,
            'title': vpc.get('name', ''),
            'cidr': '',
            'org_title': org,
            'org': prefix + 'orgs.' + org,
            'description': vpc.get('description', ''),
            'tenant': '',
            'dc': dc
        }
        vpc_seaf_id = prefix + 'vpcs.' + vpc_id
        vpcs_list['seaf.ta.reverse.evo.vpcs'][vpc_seaf_id] = yaml_structure
    save(vpcs_list, exportpath, 'evolution_vpcs')

def export_networks(config, access_token):

    evoapi = config['connection']['evoapi']
    prefix = get_prefix(config)
    project = config['connection']['project']
    dc = config['params']['DC']
    org = config['connection']['org']
    exportpath = config['params'].get('exportpath')

    networks = []
    networks_list = {'seaf.ta.services.network': {}}
    try:
        networks_req = get_evo_api(host=evoapi, bearer=access_token, uri=f'/api/v1/subnets?project_id={project}')
        networks_json = json.loads(networks_req.text)
    except Exception as err:
        print(err)
    else:
        print(f'First request status: {networks_req.status_code}')

    for item in networks_json.get('items',''):
        networks.append(item)

    for network in networks:
        network_id = network.get('id')
        yaml_structure = {
            'id': network_id,
            'title': network.get('name', ''),
            'description': network.get('description', ''),
            'type': 'LAN',
            'lan_type': 'Проводная',
            'az': network.get('availability_zone').get('name', ''),
            'segment': '',
            'vlan': '',
            'ipnetwork': network.get('subnet_address'),
            'purpose':'',
            'network_appliance': '',
            'reverse': {
                'original_id': network_id,
                'type': 'Network',
                'reverse_type': 'Evolution',
                'gateway': network.get('default_gateway'),
                'dns': network.get('dns_servers'),
                'vpc': prefix + 'vpcs.' + network.get('vpc_id'),
                'vpc_title': network.get('vpc_id'),
                'org': prefix + 'orgs.' + org
            }, 
            'dc_id': dc
        }
        network_seaf_id = prefix + 'networks.' + network_id
        networks_list['seaf.ta.services.network'][network_seaf_id] = yaml_structure
    save(networks_list, exportpath, 'evolution_networks')

def save(object, path, name):
    filename = "{}/{}.yaml".format(path, name)
    with open(filename, "w", encoding="utf-8") as outfile:
        yaml.dump(object, outfile, allow_unicode=True,
                  encoding="utf-8", sort_keys=False)
        print("saved", filename)
    return filename