import yaml
from advanced import cloudapi


def export_dms(config):

    cloudregion = config["cloudregion"]
    cloudproject = config["cloudproject"]
    tenant = config["tenant"]
    dc = config["dc"]
    company_domain = config["company_domain"]
    exportpath = config["output"]

    dmss = cloudapi.get_scloud(
        service='dms', s_type=None, region=cloudregion, project=cloudproject, item=None)

    result = {'seaf.ta.reverse.cloud_ru.advanced.dmss': {}}
    for dms in dmss['instances']:
        id = dms['instance_id']

        if 'management_connect_address' in dms:
            mca = dms['management_connect_address']
        else:
            mca = ''

        yaml_structure = {
            'id': id,
            'name': dms['name'],
            'engine': dms['engine'],
            'engine_version': dms['engine_version'],
            'port': dms['port'],
            'address': dms['connect_address'],
            'vpc_id': dms['vpc_id'],
            'subnet_id': dms['subnet_id'],
            'status': dms['status'],
            'type': dms['type'],
            'specification': dms['specification'],
            'security_groups': [dms['security_group_id']],
            'available_az': dms['available_zones'],
            'storage_space': dms['storage_space'],
            'total_storage_space': dms['total_storage_space'],
            'used_storage_space': dms['used_storage_space'],
            'storage_spec_code': dms['storage_spec_code'],
            'management': mca,
            'support_features': dms['support_features'],
            'node_num': dms['node_num'],
            'disk_encrypted': dms['disk_encrypted'],
            'tenant': tenant,
            'DC': dc
        }
        result['seaf.ta.reverse.cloud_ru.advanced.dmss']["sber.{}.dmss.{}".format(
            company_domain, id)] = yaml_structure

    save(result, exportpath, "dmss")


def export_secgroups(config):

    cloudregion = config["cloudregion"]
    cloudproject = config["cloudproject"]
    tenant = config["tenant"]
    dc = config["dc"]
    company_domain = config["company_domain"]
    exportpath = config["output"]

    secgroups = cloudapi.get_scloud(
        service='vpc', s_type='security-groups', region=cloudregion, project=cloudproject, item=None)
    result = {'seaf.ta.reverse.cloud_ru.advanced.security_groups': {}}
    for sg in secgroups['security_groups']:
        id = sg['id']
        yaml_structure = {
            'id': id,
            'name': sg['name'],
            'description': sg['description'],
            'rules': [],
            'tenant': tenant,
            'DC': dc
        }

        rules = []
        for rule in sg['security_group_rules']:

            if rule['port_range_max'] and rule['port_range_min'] != None:
                if rule['port_range_max'] == rule['port_range_min']:
                    protocol_port = rule['port_range_max']
                else:
                    protocol_port = "{} -  {}".format(
                        rule['port_range_max'], rule['port_range_min'])
            else:
                protocol_port = 'All'

            tmp = {
                'description': rule['description'],
                'direction': rule['direction'],
                'ethertype': rule['ethertype'],
                'protocol_port': protocol_port,
                'protocol': rule['protocol'],
                'remote_group_id': rule['remote_group_id'],
                'remote_ip_prefix': rule['remote_ip_prefix'],
                'remote_address_group_id': rule['remote_address_group_id']
            }

            rules.append(tmp)

        yaml_structure['rules'] = rules
        result['seaf.ta.reverse.cloud_ru.advanced.security_groups']["sber.{}.security_groups.{}".format(
            company_domain, id)] = yaml_structure

    save(result, exportpath, "security_groups")


def export_cces(config):

    cloudregion = config["cloudregion"]
    cloudproject = config["cloudproject"]
    tenant = config["tenant"]
    dc = config["dc"]
    company_domain = config["company_domain"]
    exportpath = config["output"]

    cces = cloudapi.get_scloud(
        service='cce', s_type='clusters', region=cloudregion, project=cloudproject, item=None)
    result = {'seaf.ta.reverse.cloud_ru.advanced.cces': {}}
    for cce in cces['items']:
        id = cce['metadata']['uid']

        master_az = []
        for az in cce['spec']['masters']:
            if az['availabilityZone'] not in master_az:
                master_az.append(az['availabilityZone'])

        endpoints = []
        addresses = []
        for ep in cce['status']['endpoints']:
            endpoints.append(ep)
            address = ep['url'].split('//', 1)[1].split(':')[0]
            if address not in addresses:
                addresses.append(address)

        if 'platformVersion' in cce['spec']:
            pv = cce['spec']['platformVersion']
        else:
            pv = ''

        yaml_structure = {
            'name': cce['metadata']['name'],
            'id': cce['metadata']['uid'],
            'alias': cce['metadata']['alias'],
            'flavor': cce['spec']['flavor'],
            'version': cce['spec']['version'],
            'platform_version': pv,
            'vpc_id': cce['spec']['hostNetwork']['vpc'],
            'subnet_id': cce['spec']['hostNetwork']['subnet'],
            'addresses': addresses,
            'security_groups': cce['spec']['hostNetwork']['SecurityGroup'],
            'container_network': cce['spec']['containerNetwork']['cidr'] if cce['spec']['containerNetwork'].get('cidr') is not None else '',
            'service_network': cce['spec']['serviceNetwork']['IPv4CIDR'],
            'authentication': cce['spec']['authentication']['mode'],
            'masters_az': master_az,
            'supportistio': cce['spec']['supportIstio'],
            'endpoints': endpoints,
            'tenant': tenant,
            'DC': dc
        }

        result['seaf.ta.reverse.cloud_ru.advanced.cces']["sber.{}.cces.{}".format(
            company_domain, id)] = yaml_structure

    save(result, exportpath, "cces")


def export_nat_gateways(config):

    cloudregion = config["cloudregion"]
    cloudproject = config["cloudproject"]
    dc = config["dc"]
    company_domain = config["company_domain"]
    exportpath = config["output"]

    natgateways = cloudapi.get_scloud(service='nat', s_type='gateway',
                                      region=cloudregion, project=cloudproject, item=None)
    snatrules = cloudapi.get_scloud(service='nat', s_type='snat',
                                    region=cloudregion, project=cloudproject, item=None)

    result = {'seaf.ta.reverse.cloud_ru.advanced.nat_gateways': {}}
    for gw in natgateways['nat_gateways']:
        port = cloudapi.get_scloud(service='vpc', s_type='port_filter', region=cloudregion,
                                   project=cloudproject, item=f"device_id={gw['id']}")
        id = gw['id']
        snrules = []
        for snatrule in snatrules['snat_rules']:
            if snatrule['nat_gateway_id'] == id:
                eipid = snatrule['floating_ip_id'].split(',')
                eipaddress = snatrule['floating_ip_address'].split(',')
                if 'cidr' in snatrule:
                    cidr = snatrule['cidr']
                else:
                    cidr = ''
                tmp_yaml = {
                    'id': snatrule['id'],
                    'eip_id': [],
                    'eip_address': [],
                    'status': snatrule['status'],
                    'subnet_id': snatrule['network_id'],
                    'cidr': cidr,
                    'source_type': snatrule['source_type']
                }
                snrules.append(tmp_yaml)
                tmp_yaml['eip_id'] = eipid
                tmp_yaml['eip_address'] = eipaddress
        yaml_structure = {
            'id': gw['id'],
            'name': gw['name'],
            'description': gw['description'],
            'subnet_id': gw['internal_network_id'],
            'status': gw['status'],
            'address': port['ports'][0]['fixed_ips'][0]['ip_address'],
            'snat_rules': [],
            'dnat_rules': [],
            'tenant': gw['tenant_id'],
            'DC': dc
        }
        yaml_structure['snat_rules'] = snrules
        result['seaf.ta.reverse.cloud_ru.advanced.nat_gateways']["sber.{}.nat_gateways.{}".format(
            company_domain, id)] = yaml_structure

    save(result, exportpath, "nat_gateways")


def export_elbs(config):

    cloudregion = config["cloudregion"]
    cloudproject = config["cloudproject"]
    dc = config["dc"]
    company_domain = config["company_domain"]
    exportpath = config["output"]

    elbs = cloudapi.get_scloud(
        service='elb', s_type='lb', region=cloudregion, project=cloudproject, item=None)
    result = {'seaf.ta.reverse.cloud_ru.advanced.elbs': {}}
    for elb in elbs['loadbalancers']:
        id = elb['id']
        listeners = []
        pools = []
        fwpolicy = []
        for listener in elb['listeners']:
            listeners.append(cloudapi.get_scloud(service='elb', s_type='listeners',
                             region=cloudregion, project=cloudproject, item=listener['id'])['listener'])
            print(listener['id'])
            forwardingpolicies = cloudapi.get_scloud(
                service='elb', s_type='l7policies', region=cloudregion, project=cloudproject, item=None)
            if forwardingpolicies != None:
                fwpolicy.append(forwardingpolicies)
        for pool in elb['pools']:
            pools.append(cloudapi.get_scloud(service='elb', s_type='pools',
                         region=cloudregion, project=cloudproject, item=pool['id'])['pool'])

        port = cloudapi.get_scloud(
            service='vpc', s_type='port', region=cloudregion, project=cloudproject, item=elb['vip_port_id'])

        vips = []
        tmp = cloudapi.get_scloud(service='vpc', s_type='port_filter', region=cloudregion,
                                  project=cloudproject, item=f"fixed_ips=subnet_id={port['port']['fixed_ips'][0]['subnet_id']}")
        ip = elb['vip_address']
        for item in tmp['ports']:
            for ippair in item['allowed_address_pairs']:
                if ippair['ip_address'] == ip:
                    if item['fixed_ips'][0]['ip_address'] not in vips:
                        vips.append(item['fixed_ips'][0]['ip_address'])

        yaml_structure = {
            'id': id,
            'name': elb['name'],
            'description': elb['description'],
            'subnet_id': port['port']['network_id'],
            'port_id': elb['vip_port_id'],
            'address': elb['vip_address'],
            'operating_status': elb['operating_status'],
            'provisioning_status': elb['provisioning_status'],
            'listeners': [],
            'pools': [],
            'tags': [],
            'forwardingpolicy': [],
            'tenant': elb['tenant_id'],
            'DC': dc,
        }

        for listener in listeners:
            tmp = {
                'id': listener['id'],
                'name': listener['name'],
                'default_pool_id': listener['default_pool_id'],
                'protocol_port': listener['protocol_port'],
                'protocol': listener['protocol']
            }
            yaml_structure['listeners'].append(tmp)
        for pool in pools:
            tmp = {
                'id': pool['id'],
                'name': pool['name'],
                'lb_algorithm': pool['lb_algorithm'],
                'members': []
            }
            members = cloudapi.get_scloud(
                service='elb', s_type='poolmembers', region=cloudregion, project=cloudproject, item=pool['id'])
            if 'members' in members:
                for member in members['members']:
                    tmp2 = {
                        'id': member['id'],
                        'address': member['address'],
                        'name': member['name']
                    }
                    tmp['members'].append(tmp2)
            yaml_structure['pools'].append(tmp)
        result['seaf.ta.reverse.cloud_ru.advanced.elbs']["sber.{}.elbs.{}".format(
            company_domain, id)] = yaml_structure

    save(result, exportpath, "elbs")


def export_servers(config):

    cloudregion = config["cloudregion"]
    cloudproject = config["cloudproject"]
    dc = config["dc"]
    tenant = config["tenant"]
    company_domain = config["company_domain"]
    exportpath = config["output"]

    servers = cloudapi.get_scloud(service='ecs', region=cloudregion,
                                  project=cloudproject, item=None, s_type=None)
    result = {'seaf.ta.reverse.cloud_ru.advanced.ecss': {}}

    eips = cloudapi.get_scloud(service='eip', s_type=None,
                               region=cloudregion, project=cloudproject, item=None)

    for server in servers:
        print(server['name'])
        ports = []
        vips = []
        for nic in server["addresses"]:
            for portid in server['addresses'][nic]:
                physical_port = cloudapi.get_scloud(
                    service='vpc', s_type='port', region=cloudregion, project=cloudproject, item=portid['OS-EXT-IPS:port_id'])

                for fixed_ip in physical_port['port']['fixed_ips']:
                    tmp = {'network_id': physical_port['port']['network_id'],
                           'subnet_id': fixed_ip['subnet_id'], 'ip_address': fixed_ip['ip_address']}
                    if tmp not in ports:
                        ports.append(tmp)

        for port in ports:
            tmp = cloudapi.get_scloud(service='vpc', s_type='port_filter', region=cloudregion, project=cloudproject,
                                      item=f"device_owner=neutron:VIP_PORT&fixed_ips=subnet_id={port['subnet_id']}")
            ip = port['ip_address']
            for item in tmp['ports']:
                for ippair in item['allowed_address_pairs']:
                    if ippair['ip_address'] == ip:
                        if item['fixed_ips'][0]['ip_address'] not in vips:
                            vips.append(item['fixed_ips'][0]['ip_address'])

        for eip in eips['publicips']:
            if 'private_ip_address' in eip:
                if eip['private_ip_address'] in vips:
                    if eip['public_ip_address'] not in vips:
                        vips.append(eip['public_ip_address'])

        id = server['id']
        yaml_structure = {
            'id': server['id'],
            'name': server['name'],
            'description': server['description'],
            'status': server['status'],
            'flavor': server['flavor']['id'],
            'os': {'type': server['metadata']['os_type'], 'bit': server['metadata']['os_bit']},
            'vpc_id': server['metadata']['vpc_id'],
            'az': server['OS-EXT-AZ:availability_zone'],
            'cpu': {'cores': int(server['flavor']['vcpus']), 'frequency': '', 'arch': ''},
            'ram': int(server['flavor']['ram']),
            'nic_qty': int(),
            'addresses': [],
            'subnets': [],
            'disks': [],
            'tags': [],
            'security_groups': [],
            'type': "vm",
            'tenant': tenant,
            'DC': dc
        }

        yaml_secgroups = []
        for sg in server['security_groups']:
            if sg['id'] not in yaml_secgroups:
                yaml_secgroups.append(sg['id'])

        yaml_ip = []

        nic_ports = []
        for nic in server["addresses"]:
            for item in server['addresses'][nic]:
                yaml_ip.append(item['addr'])
                if item['OS-EXT-IPS:port_id'] not in nic_ports:
                    nic_ports.append(item['OS-EXT-IPS:port_id'])

        nic_count = int(len(nic_ports))

        for vip in vips:
            yaml_ip.append(vip)

        yaml_subnets = []
        for port in ports:
            if port['network_id'] not in yaml_subnets:
                yaml_subnets.append(port['network_id'])

        yaml_disks = []
        for disk in server["os-extended-volumes:volumes_attached"]:
            evs_obj = cloudapi.get_scloud(
                service='evs', region=cloudregion, project=cloudproject, item=disk['id'])
            yaml_disks.append({disk['id']: {
                'device': disk['device'],
                'size': evs_obj['volume']['size'],
                'az': evs_obj['volume']['availability_zone'],
                'type': evs_obj['volume']['volume_type']
            }})

        yaml_tags = []
        for tag in server['tags']:
            key = tag.split("=", 1)[0]
            value = tag.split("=", 1)[1]
            yaml_tags.append({'key': key, 'value': value})

        yaml_structure['security_groups'] = yaml_secgroups
        yaml_structure['nic_qty'] = nic_count
        yaml_structure['addresses'] = yaml_ip
        yaml_structure['disks'] = yaml_disks
        yaml_structure['tags'] = yaml_tags
        yaml_structure['subnets'] = yaml_subnets
        result['seaf.ta.reverse.cloud_ru.advanced.ecss']["sber.{}.ecss.{}".format(
            company_domain, id)] = yaml_structure

    save(result, exportpath, "ecss")


def export_vpcs(config):

    cloudregion = config["cloudregion"]
    cloudproject = config["cloudproject"]
    dc = config["dc"]
    tenant = config["tenant"]
    company_domain = config["company_domain"]
    exportpath = config["output"]

    vpcs = cloudapi.get_scloud(
        service='vpc', region=cloudregion, s_type=None, project=cloudproject, item=None)
    result = {'seaf.ta.reverse.cloud_ru.advanced.vpcs': {}}
    for vpc in vpcs['vpcs']:
        id = vpc['id']
        yaml_vpc = {
            'id': id,
            'name': vpc['name'],
            'cidr': vpc['cidr'],
            'description': vpc['description'],
            'tenant': tenant,
            'DC': dc
        }
        result['seaf.ta.reverse.cloud_ru.advanced.vpcs']["sber.{}.vpcs.{}".format(
            company_domain, id)] = yaml_vpc

    save(result, exportpath, "vpcs")


def export_subnets(config):

    cloudregion = config["cloudregion"]
    cloudproject = config["cloudproject"]
    dc = config["dc"]
    tenant = config["tenant"]
    company_domain = config["company_domain"]
    exportpath = config["output"]

    subnets = cloudapi.get_scloud(
        service='vpc', region=cloudregion, project=cloudproject, s_type='subnet', item=None)
    result = {'seaf.ta.reverse.cloud_ru.advanced.subnets': {}}
    for subnet in subnets['subnets']:
        id = subnet['id']
        yaml_subnet = {
            'id': id,
            'name': subnet['name'],
            'cidr': subnet['cidr'],
            'description': subnet['description'],
            'gateway': subnet['gateway_ip'],
            'dns_list': subnet['dnsList'],
            'vpc': subnet['vpc_id'],
            'tenant': tenant,
            'DC': dc
        }
        result['seaf.ta.reverse.cloud_ru.advanced.subnets']["sber.{}.subnets.{}".format(
            company_domain, id)] = yaml_subnet

    save(result, exportpath, "subnets")


def export_peerings(config):

    cloudregion = config["cloudregion"]
    cloudproject = config["cloudproject"]
    dc = config["dc"]
    tenant = config["tenant"]
    company_domain = config["company_domain"]
    exportpath = config["output"]

    peerings = cloudapi.get_scloud(
        service='vpc', region=cloudregion, project=cloudproject, s_type='peering', item=None)
    result = {'seaf.ta.reverse.cloud_ru.advanced.peerings': {}}
    for peering in peerings['peerings']:
        id = peering['id']
        yaml_peering = {
            'id': id,
            'name': peering['name'],
            'request_vpc': peering['request_vpc_info']['vpc_id'],
            'accept_vpc': peering['accept_vpc_info']['vpc_id'],
            'description': peering['description'],
            'status': peering['status'],
            'tenant': tenant,
            'DC': dc
        }
        result['seaf.ta.reverse.cloud_ru.advanced.peerings']["sber.{}.peerings.{}".format(
            company_domain, id)] = yaml_peering

    save(result, exportpath, "peerings")


def export_eips(config):

    cloudregion = config["cloudregion"]
    cloudproject = config["cloudproject"]
    dc = config["dc"]
    tenant = config["tenant"]
    company_domain = config["company_domain"]
    exportpath = config["output"]

    eips = cloudapi.get_scloud(
        service='eip', s_type=None, region=cloudregion, project=cloudproject, item=None)
    result = {'seaf.ta.reverse.cloud_ru.advanced.eips': {}}

    for eip in eips['publicips']:
        id = eip['id']
        if 'private_ip_address' in eip:
            int_address = eip['private_ip_address']
        else:
            int_address = ''
        if 'port_id' in eip:
            port = eip['port_id']
        else:
            port = ''
        yaml_eip = {
            'id': id,
            'type': eip['type'],
            'port_id': port,
            'ext_address': eip['public_ip_address'],
            'int_address': int_address,
            'limit': {'type': eip['bandwidth_share_type'],
                      'throughput': eip['bandwidth_size'],
                      'rule_id': eip['bandwidth_id'],
                      'rule_name': eip['bandwidth_name']
                      },
            'tenant': tenant,
            'DC': dc
        }
        result['seaf.ta.reverse.cloud_ru.advanced.eips']["sber.{}.eips.{}".format(
            company_domain, id)] = yaml_eip

    save(result, exportpath, "eips")


def export_vaults(config):

    cloudregion = config["cloudregion"]
    cloudproject = config["cloudproject"]
    dc = config["dc"]
    tenant = config["tenant"]
    company_domain = config["company_domain"]
    exportpath = config["output"]

    vaults = cloudapi.get_scloud(
        service='cbr', region=cloudregion, project=cloudproject, s_type='vault', item=None)
    result = {'seaf.ta.reverse.cloud_ru.advanced.vaults': {}}
    for vault in vaults['vaults']:
        id = vault['id']
        yaml_vault = {
            'id': id,
            'name': vault['name'],
            'description': vault['description'],
            'resources': vault['resources'],
            'tenant': tenant,
            'DC': dc
        }
        result['seaf.ta.reverse.cloud_ru.advanced.vaults']["sber.{}.vaults.{}".format(
            company_domain, id)] = yaml_vault

    save(result, exportpath, "vaults")


def export_backup_policies(config):

    cloudregion = config["cloudregion"]
    cloudproject = config["cloudproject"]
    dc = config["dc"]
    tenant = config["tenant"]
    company_domain = config["company_domain"]
    exportpath = config["output"]

    bpolicy = cloudapi.get_scloud(
        service='cbr', region=cloudregion, project=cloudproject, s_type='policy', item=None)

    result = {'seaf.ta.reverse.cloud_ru.advanced.backup_policies': {}}
    for policy in bpolicy['policies']:
        id = policy['id']
        yaml_vault = {
            'id': id,
            'name': policy['name'],
            'operation_type': policy['operation_type'],
            'enabled': policy['enabled'],
            'operation_definition': policy['operation_definition'],
            'trigger': policy['trigger'],
            'associated_vaults': policy['associated_vaults'],
            'tenant': tenant,
            'DC': dc
        }
        result['seaf.ta.reverse.cloud_ru.advanced.backup_policies']["sber.{}.backup_policies.{}".format(
            company_domain, id)] = yaml_vault

    save(result, exportpath, "backup_policies")


def export_rdss(config):

    cloudregion = config["cloudregion"]
    cloudproject = config["cloudproject"]
    dc = config["dc"]
    tenant = config["tenant"]
    company_domain = config["company_domain"]
    exportpath = config["output"]

    rdses = cloudapi.get_scloud(service='rds', region=cloudregion,
                                project=cloudproject, s_type=None, item=None)

    result = {'seaf.ta.reverse.cloud_ru.advanced.rdss': {}}
    for db in rdses['instances']:
        id = db['id']
        yaml_db = {
            'id': id,
            'name': db['name'],
            'status': db['status'],
            'type': db['type'],
            'datastore': db['datastore'],
            'vpc_id': db['vpc_id'],
            'subnet_id': db['subnet_id'],
            'volume': db['volume'],
            'private_ips': db['private_ips'],
            'public_ips': db['public_ips'],
            'nodes': db['nodes'],
            'flavor': db['flavor_ref'],
            'switch_strategy': db['switch_strategy'],
            'backup_strategy': db['backup_strategy'],
            'az': db['region'],
            'tags': db['tags'],
            'tenant': tenant,
            'DC': dc
        }
        result['seaf.ta.reverse.cloud_ru.advanced.rdss']["sber.{}.rdss.{}".format(
            company_domain, id)] = yaml_db

    save(result, exportpath, "rdss")


def save(object, path, name):
    filename = "{}/{}.yaml".format(path, name)
    with open(filename, "w", encoding="utf-8") as outfile:
        yaml.dump(object, outfile, allow_unicode=True,
                  encoding="utf-8", sort_keys=False)
        print("saved", filename)
    return filename
