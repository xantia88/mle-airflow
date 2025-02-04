import yaml
import json
import re
import math
import configparser
from vmwarecloud import cloudapi


def export_orgs(config):

    site = config["site"]
    access_token = config["access_token"]
    api_init = config["api_init"]
    prefix = config["prefix"]
    dc = config["dc"]
    exportpath = config["exportpath"]

    # Receiving Organizations
    orgs = []
    orgs_list = {'seaf.ta.reverse.vmwarecloud.orgs': {}}

    query = f'https://{site}/cloudapi/1.0.0/orgs?pageSize=100'
    try:
        r = cloudapi.get_cloudapi(
            url=query, bearer=access_token, version=api_init)
        r_json = json.loads(r.text)
    except Exception as err:
        print(err.strerror)
    else:
        print(r.status_code)

    # Putting first batch to the list
    for item in r_json.get('values', ''):
        orgs.append(item)

    # Working with pages if there are more than one
    if r_json.get('pageCount', '') > 1:
        items = cloudapi.get_pages(r_json.get(
            'pageCount', ''), query, api_init, access_token)
        for item in items:
            orgs.append(item)

    for org in orgs:
        org_urn_id = org.get('id', '')
        org_id = org_urn_id.split(":")[-1]
        org_seaf_id = prefix + 'orgs.' + org_id

        yaml_structure = {
            'id': org_id,
            'original_id': org_urn_id,
            'title': org.get('name', ''),
            'description': org.get('description', ''),
            'dc': dc
        }

        orgs_list['seaf.ta.reverse.vmwarecloud.orgs'][org_seaf_id] = yaml_structure

    save(orgs_list, exportpath, "enterprise_orgs")


def export_vdcgroups(config):

    site = config["site"]
    access_token = config["access_token"]
    api_init = config["api_init"]
    prefix = config["prefix"]
    dc = config["dc"]
    exportpath = config["exportpath"]

    vdcgroups = []
    vdcgroups_list = {'seaf.ta.reverse.vmwarecloud.vdcgroups': {}}

    query = f'https://{site}/cloudapi/1.0.0/vdcGroups?pageSize=100'
    try:
        r = cloudapi.get_cloudapi(
            url=query, bearer=access_token, version=api_init)
        r_json = json.loads(r.text)
    except Exception as err:
        print(err.strerror)
    else:
        print(r.status_code)

    # Putting first batch to the list
    for item in r_json.get('values', ''):
        vdcgroups.append(item)

    # Working with pages if there are more than one
    if r_json.get('pageCount', '') > 1:
        items = cloudapi.get_pages(r_json.get('pageCount', ''),
                                   query, api_init, access_token)
        for item in items:
            vdcgroups.append(item)

    for vdcgroup in vdcgroups:
        vdcgroup_urn_id = vdcgroup.get('id', '')
        vdcgroup_id = vdcgroup_urn_id.split(':')[-1]
        vdcgroup_seaf_id = prefix + 'vdcgroups.' + vdcgroup_id

        # Getting all corresponding networks
        networks = []
        net_query = 'https://'+site+'/cloudapi/1.0.0/orgVdcNetworks?filter=ownerRef.id==' + \
            vdcgroup_urn_id+'&pageSize=100'
        try:
            net_request = cloudapi.get_cloudapi(
                url=net_query, bearer=access_token, version=api_init)
            net_json = json.loads(net_request.text)
        except Exception as err:
            print(err.strerror)

        for network in net_json.get('values', ''):
            network_urn_id = network.get('id', '')
            network_id = prefix + 'orgnets.' + network_urn_id.split(':')[-1]
            networks.append(
                {
                    'id': network_id,
                    'title': network.get('name', '')
                }
            )

        # Getting all corresponding vdcs
        vdcs = []
        for orgvdc in vdcgroup.get('participatingOrgVdcs', ''):
            orgvdc_seaf_id = prefix + 'vdcs.' + \
                orgvdc.get('vdcRef', '').get('id', '').split(':')[-1]
            org_seaf_id = prefix + 'orgs.' + \
                orgvdc.get('orgRef', '').get('id', '').split(':')[-1]
            vdcs.append(
                {
                    'id': orgvdc_seaf_id,
                    'title': orgvdc.get('vdcRef', '').get('name'),
                    'org': org_seaf_id,
                    'org_title': orgvdc.get('orgRef', '').get('name')
                }
            )

        org_id = prefix + 'orgs.' + vdcgroup.get('orgId', '').split(":")[-1]
        netpool_id = prefix + 'netpools.' + \
            vdcgroup.get('networkPoolId', '').split(":")[-1]

        yaml_structure = {
            'id': vdcgroup_id,
            'original_id': vdcgroup_urn_id,
            'title': vdcgroup.get('name', ''),
            'networkprovidertype': vdcgroup.get('networkProviderType', ''),
            'type': vdcgroup.get('type', ''),
            'networkpoolid': netpool_id,
            'localegress': vdcgroup.get('localEgress', ''),
            'dfwenabled': vdcgroup.get('dfwEnabled', ''),
            'org': org_id,
            'networks': [],
            'vdcs': [],
            'dc': dc
        }
        yaml_structure['networks'] = networks
        yaml_structure['vdcs'] = vdcs

        vdcgroups_list['seaf.ta.reverse.vmwarecloud.vdcgroups'][vdcgroup_seaf_id] = yaml_structure

    save(vdcgroups_list, exportpath, "enterprise_vdcgroups")


def export_vdcs(config):

    site = config["site"]
    access_token = config["access_token"]
    api_init = config["api_init"]
    prefix = config["prefix"]
    dc = config["dc"]
    exportpath = config["exportpath"]

    # Receiving VDCs
    vdcs = []
    vdcs_list = {'seaf.ta.reverse.vmwarecloud.vdcs': {}}

    query = f'https://{site}/cloudapi/1.0.0/vdcs?pageSize=100'
    try:
        r = cloudapi.get_cloudapi(
            url=query, bearer=access_token, version=api_init)
        r_json = json.loads(r.text)
    except Exception as err:
        print(err.strerror)
    else:
        print(r.status_code)

    # Putting first batch to the list
    for item in r_json.get('values', ''):
        vdcs.append(item)

    # Working with pages if there are more than one
    if r_json.get('pageCount', '') > 1:
        items = cloudapi.get_pages(r_json.get(
            'pageCount', ''), query, api_init, access_token)
        for item in items:
            vdcs.append(item)

    for vdc in vdcs:
        vdc_urn_id = vdc.get('id', '')
        vdc_id = vdc_urn_id.split(':')[-1]
        vdc_seaf_id = prefix + 'vdcs.' + vdc_id

        networks = []
        net_query = 'https://'+site + \
            '/cloudapi/1.0.0/orgVdcNetworks?filter=orgVdc.id=='+vdc_urn_id+'&pageSize=100'
        try:
            net_request = cloudapi.get_cloudapi(
                url=net_query, bearer=access_token, version=api_init)
            net_json = json.loads(net_request.text)
        except Exception as err:
            print(err.strerror)

        for network in net_json.get('values', ''):
            network_urn_id = network.get('id', '')
            network_id = prefix + 'orgnets.' + network_urn_id.split(':')[-1]
            networks.append(
                {
                    'id': network_id,
                    'title': network.get('name', '')
                }
            )

        org_id = prefix + 'orgs.' + vdc.get('org', '').get('id', '')

        yaml_structure = {
            'id': vdc_id,
            'original_id': vdc_urn_id,
            'title': vdc.get('name', ''),
            'allocationtype': vdc.get('allocationType', ''),
            'org_title': vdc.get('org', '').get('name', ''),
            'org': org_id,
            'availablenetworks': [],
            'dc': dc
        }
        yaml_structure['availablenetworks'] = networks

        vdcs_list['seaf.ta.reverse.vmwarecloud.vdcs'][vdc_seaf_id] = yaml_structure

    save(vdcs_list, exportpath, "enterprise_vdcs")


def export_orgnetworks(config):

    site = config["site"]
    access_token = config["access_token"]
    api_init = config["api_init"]
    prefix = config["prefix"]
    dc = config["dc"]
    exportpath = config["exportpath"]

    orgnetworks = []
    orgnetworks_list = {'seaf.ta.services.network': {}}

    query = f'https://{site}/cloudapi/1.0.0/orgVdcNetworks?pageSize=100'
    try:
        r = cloudapi.get_cloudapi(
            url=query, bearer=access_token, version=api_init)
    except Exception as err:
        print(err.strerror)
    else:
        print(r.status_code)
        r_json = json.loads(r.text)

    # Putting first batch to the list
    for item in r_json.get('values', ''):
        orgnetworks.append(item)

    # Working with pages if there are more than one
    if r_json.get('pageCount', '') > 1:
        items = cloudapi.get_pages(r_json.get(
            'pageCount', ''), query, api_init, access_token)
        for item in items:
            orgnetworks.append(item)

    for orgnet in orgnetworks:
        orgnet_urn_id = orgnet.get('id', '')
        orgnet_id = orgnet_urn_id.split(':')[-1]
        orgnet_seaf_id = prefix + 'orgnets.' + orgnet_id

        # Getting all DNS server address in subnets
        dns = []
        for item in orgnet.get('subnets', '').get('values', ''):
            dns1 = item.get('dnsServer1', '')
            dns2 = item.get('dnsServer2', '')
            if dns1 not in [None, '', dns]:
                dns.append(dns1)
            if dns2 not in [None, '', dns]:
                dns.append(dns2)

        if orgnet.get('orgVdc', '') not in [None, '']:
            vdc_name = orgnet.get('orgVdc', '').get('name', '')
            vdc_id = prefix + 'vdcs.' + \
                orgnet.get('orgVdc', '').get('id', '').split(':')[-1]
        else:
            vdc_name = None
            vdc_id = None

        if orgnet.get('ownerRef', '') not in [None, '']:
            if re.match(r'.*:vdcGroup:.*', orgnet.get('ownerRef').get('id')):
                vdcgroup_id = prefix + 'vdcgroups.' + \
                    orgnet.get('ownerRef', '').get('id', '').split(':')[-1]
                vdcgroup_name = orgnet.get('ownerRef', '').get('name', '')
            else:
                vdcgroup_name = None
                vdcgroup_id = None
        else:
            vdcgroup_name = None
            vdcgroup_id = None

        org_id = prefix + 'orgs.' + \
            orgnet.get('orgRef', '').get('id', '').split(":")[-1]
        parentnetwork_id = prefix + 'orgnets.' + \
            orgnet.get('parentNetworkId', '') if orgnet.get(
                'parentNetworkId', '') not in [None, ''] else None

        if orgnet.get('connection', '') not in ['', None]:
            if orgnet.get('connection').get('connected') not in ['', None]:
                connected = orgnet.get('connection').get('connected')
            else:
                connected = False
        else:
            connected = False

        yaml_structure = {
            'id': orgnet_id,
            'title': orgnet.get('name', ''),
            'description': orgnet.get('description', ''),
            'type': 'Проводная',
            'lan_type': 'LAN',
            'az': '',
            'segment': '',
            'vlan': '',
            'ipnetwork': '',
            'purpose': '',
            'network_appliance_id': '',
            'reverse': {
                'reverse_type': 'VMwareCloud',
                'original_id': orgnet_urn_id,
                'type': 'orgNetwork',
                'netmask': '',
                'gateway': '',
                'parentnetwork': parentnetwork_id,
                'backingnetworktype': orgnet.get('backingNetworkType', ''),
                'networkpool': '',
                'networkpool_title': '',
                'isdefaultnetwork': orgnet.get('isDefaultNetwork', ''),
                'shared': orgnet.get('shared', ''),
                'status': orgnet.get('status', ''),
                'org': org_id,
                'vdc': vdc_id,
                'vdc_title':  vdc_name,
                'vdcgroup': vdcgroup_id,
                'vdcgroup_title': vdcgroup_name,
                'connected': connected,
                'dns': dns,
                'fencemode': orgnet.get('networkType', ''),
                'ipscopes': []
            },
            'dc': dc
        }

        # Getting All Networks
        ipscope = []
        for scope in orgnet.get('subnets', '').get('values', ''):
            if scope.get('ipRanges', '').get('values', '') != None:
                for item in scope.get('ipRanges', '').get('values', ''):
                    ipranges = map(lambda w: {'startaddress': w['startAddress'],
                                              'endaddress': w['endAddress']}, scope['ipRanges']['values'])
                netmask = cloudapi.convert_cidr_to_netmask(
                    scope.get('prefixLength', ''))
                yaml_scope = {
                    'gateway': scope.get('gateway', ''),
                    'netmask': netmask,
                    'subnetprefixlength': scope.get('prefixLength', ''),
                    'ipranges': [x for x in ipranges]
                }
                ipscope.append(yaml_scope)
        yaml_structure['reverse']['ipscopes'] = ipscope
        netmask = [x.get('netmask', '')
                   for x in ipscope if x.get('netmask') not in [None, '']]
        gateway = [x.get('gateway', '')
                   for x in ipscope if x.get('gateway') not in [None, '']]
        yaml_structure['reverse']['netmask'] = netmask[0] if netmask not in [
            None, '', []] else ''
        yaml_structure['reverse']['gateway'] = gateway[0] if gateway not in [
            None, '', []] else ''
        if re.match(r':', yaml_structure['reverse']['gateway']):
            ipnetwork = yaml_structure['reverse']['gateway']
        else:
            ipnetwork = cloudapi.get_cidr(
                yaml_structure['reverse']['gateway'], yaml_structure['reverse']['netmask'])
        yaml_structure['ipnetwork'] = ipnetwork

        orgnetworks_list['seaf.ta.services.network'][orgnet_seaf_id] = yaml_structure

    save(orgnetworks_list, exportpath, "enterprise_orgnets")


def export_edgegw(config):

    site = config["site"]
    access_token = config["access_token"]
    api_init = config["api_init"]
    prefix = config["prefix"]
    dc = config["dc"]
    exportpath = config["exportpath"]

    # Receiving Edge Gateways
    egws = []
    egw_list = {'seaf.ta.components.network': {}}

    query = f'https://{site}/cloudapi/1.0.0/edgeGateways?pageSize=100'
    try:
        r = cloudapi.get_cloudapi(
            url=query, bearer=access_token, version=api_init)
    except Exception as err:
        print(err.strerror)
    else:
        print(r.status_code)
        r_json = json.loads(r.text)

    # Putting first batch to the list
    for item in r_json.get('values', ''):
        egws.append(item)

    # Working with pages if there are more than one
    if r_json.get('pageCount', '') > 1:
        items = cloudapi.get_pages(r_json.get(
            'pageCount', ''), query, api_init, access_token)
        for item in items:
            egws.append(item)

    for gw in egws:
        gw_urn_id = gw.get('id', '')
        gw_id = gw_urn_id.split(':')[-1]
        gw_seaf_id = prefix + 'egws.' + gw_id

        # Getting networks
        networks = []
        nquery = 'https://'+site + \
            '/cloudapi/1.0.0/orgVdcNetworks?filter=connection.routerRef.id==' + \
            gw_urn_id+'&pageSize=100'
        try:
            r = cloudapi.get_cloudapi(
                url=nquery, bearer=access_token, version=api_init)
        except Exception as err:
            print(err.strerror)
        else:
            r_network = json.loads(r.text)

            # Putting first batch to the list
            for item in r_network.get('values', ''):
                networks.append(item)

            # Working with pages if there are more than one
            if r_network.get('pageCount', '') > 1:
                items = cloudapi.get_pages(r_network.get(
                    'pageCount', ''), nquery, api_init, access_token)
                for item in items:
                    networks.append(item)

            # Appending networks and uplinks to interfaces
            interfaces = []
            # uplinks
            for item in gw.get('edgeGatewayUplinks', ''):
                uplink_ref_id = item.get('uplinkId', '')
                uplink_id = uplink_ref_id.split(':')[-1]
                uplink_seaf_id = prefix + 'orgnets.' + uplink_id

                yaml_if = {
                    'title': item.get('uplinkName', ''),
                    'network': uplink_seaf_id,
                    'iftype': 'uplink',
                    'usefordefaultroute': 'No idea where to get from new API',
                    'connected': item.get('connected', ''),
                    'subnetparticipation': []
                }

                subnets = []
                for subnet in [x for x in item.get('subnets', '').get('values', '') if x.get('primaryIp', '') not in [None, '']]:
                    netmask = cloudapi.convert_cidr_to_netmask(
                        subnet.get('prefixLength', ''))
                    yaml_subn = {
                        'gateway': subnet.get('gateway', ''),
                        'netmask': netmask,
                        'ipaddress': subnet.get('primaryIp'),
                        'ipranges': []
                    }

                    ipranges = []
                    if subnet.get('ipRanges').get('values', '') == None:
                        continue
                    for range in subnet.get('ipRanges').get('values', ''):
                        yaml_ranges = {
                            'startaddress': range.get('startAddress', ''),
                            'endaddress': range.get('endAddress', '')
                        }
                        ipranges.append(yaml_ranges)
                    yaml_subn['ipranges'] = ipranges
                    subnets.append(yaml_subn)

                yaml_if['subnetparticipation'] = subnets
                interfaces.append(yaml_if)

        # Internal networks
        for item in networks:
            network_ref_id = item.get('id', '')
            network_id = network_ref_id.split(':')[-1]
            network_seaf_id = prefix + 'orgnets.' + network_id

            if item.get('connection', '') not in ['', None]:
                if item.get('connection').get('connected') not in ['', None]:
                    connected = item.get('connection').get('connected')
                else:
                    connected = False
            else:
                connected = False

            if item.get('isDefaultNetwork', '') not in [None, '']:
                usefordefaultroute = item.get('isDefaultNetwork')
            else:
                usefordefaultroute = False

            yaml_if = {
                'title': item.get('name', ''),
                'network': network_seaf_id,
                'iftype': item.get('connection', '').get('connectionType', ''),
                'usefordefaultroute': usefordefaultroute,
                'connected': connected,
                'subnetparticipation': []
            }

            subnets = []
            for subnet in item.get('subnets', '').get('values', ''):
                netmask = cloudapi.convert_cidr_to_netmask(
                    subnet.get('prefixLength', ''))

                ipaddresses = []
                ipquery = 'https://'+site+'/cloudapi/1.0.0/orgVdcNetworks/' + \
                    network_ref_id+'/allocatedIpAddresses'
                try:
                    r = cloudapi.get_cloudapi(
                        url=ipquery, bearer=access_token, version=api_init)
                except Exception as err:
                    print(err.strerror)
                    ipaddress = "Not found (error)"
                else:
                    r_ip = json.loads(r.text)

                    # Putting first batch to the list
                    for item in r_ip.get('values', ''):
                        ipaddresses.append(item)

                    # Working with pages if there are more than one
                    if r_ip.get('pageCount', '') > 1:
                        items = cloudapi.get_pages(
                            r_ip.get('pageCount', ''), ipquery, api_init, access_token)
                        for item in items:
                            ipaddresses.append(item)

                    ipaddress = next(iter([x.get('ipAddress') for x in ipaddresses if x.get(
                        'allocationType') == 'VSM_ALLOCATED']), None)

                yaml_subn = {
                    'gateway': subnet.get('gateway', ''),
                    'netmask': netmask,
                    'ipaddress': ipaddress,
                    'ipranges': []
                }

                ipranges = []
                if subnet.get('ipRanges', '').get('values', '') not in [None, '']:
                    for range in subnet.get('ipRanges').get('values', ''):
                        yaml_ranges = {
                            'startaddress': range.get('startAddress', ''),
                            'endaddress': range.get('endAddress', '')
                        }
                        ipranges.append(yaml_ranges)
                    yaml_subn['ipranges'] = ipranges
                    subnets.append(yaml_subn)

            yaml_if['subnetparticipation'] = subnets
            interfaces.append(yaml_if)

        if gw.get('orgVdc', '') not in [None, '']:
            vdc_name = gw.get('orgVdc', '').get('name', '')
            vdc_id = prefix + 'vdcs.' + \
                gw.get('orgVdc', '').get('id', '').split(':')[-1]
        else:
            vdc_name = None
            vdc_id = None

        if gw.get('ownerRef', '') not in [None, '']:
            if re.match(r'.*:vdcGroup:.*', gw.get('ownerRef').get('id')):
                vdcgroup_id = prefix + 'vdcgroups.' + \
                    gw.get('ownerRef', '').get('id', '').split(':')[-1]
                vdcgroup_name = gw.get('ownerRef', '').get('name', '')
            else:
                vdcgroup_name = None
                vdcgroup_id = None
        else:
            vdcgroup_name = None
            vdcgroup_id = None

        org_id = prefix + 'orgs.' + \
            gw.get('orgRef', '').get('id', None).split(':')[-1]
        yaml_structure = {
            'id': gw_id,
            'original_id': gw_urn_id,
            'title': gw.get('name'),
            'description': gw.get('description', ''),
            'type': gw.get('gatewayBacking', '').get('gatewayType'),
            'vdc': vdc_id,
            'vdc_title': vdc_name,
            'vdcgroup': vdcgroup_id,
            'vdcgroup_title': vdcgroup_name,
            'org': org_id,
            'gatewayinterfaces': [],
            'dc': dc
        }
        yaml_structure['gatewayinterfaces'] = interfaces

        egw_list['seaf.ta.components.network'][gw_seaf_id] = yaml_structure

    save(egw_list, exportpath, "enterprise_egws")


def export_vms(config):

    site = config["site"]
    access_token = config["access_token"]
    api_init = config["api_init"]
    prefix = config["prefix"]
    dc = config["dc"]
    exportpath = config["exportpath"]

    # Получаем список VM
    vms = []
    vms_list = {'seaf.ta.components.server': {}}

    # Initial request
    query = f'https://{site}/api/query?type=vm&pageSize=100'
    try:
        vms_request = cloudapi.get_cloud_enterprise_req(
            url=query, bearer=access_token, version=api_init)
        vms_json = json.loads(vms_request.text)
    except Exception as err:
        print(err.strerror)
    else:
        print(vms_request.status_code)

    # Putting first batch to the list
    for item in vms_json.get('record', ''):
        vms.append(item)

    # Working with pages if there are more than one
    pagecount = math.ceil(vms_json.get('total') / vms_json.get('pageSize'))
    if pagecount > 1:
        items = cloudapi.get_pages(pagecount, query, api_init, access_token)
        for item in items:
            vms.append(item)

    # Getting vm details
    for vm in vms:

        # Не выгружаем Template
        if vm.get('isVAppTemplate') == True:
            continue

        query = vm.get('href', '')
        try:
            vm_request = cloudapi.get_cloud_enterprise_req(
                url=query, bearer=access_token, version=api_init)
            if not vm_request.ok:
                continue
            vm_json = json.loads(vm_request.text)
        except Exception as err:
            continue

        vm_urn_id = vm_json.get('id', '')
        vm_id = vm_urn_id.split(':')[-1]
        vm_seaf_id = prefix + 'vms.' + vm_id

        disks = []
        vmspec = [x for x in vm_json.get('section') if x.get(
            '_type', '') == 'VmSpecSectionType']
        disksettings = [x.get('diskSection').get('diskSettings')
                        for x in vmspec if x.get('diskSection', '') not in [None, '']]
        for disk in [x[0] for x in disksettings]:
            disk_id = disk.get('diskId', '0')
            disks.append({disk_id: {
                'device': f'{disk.get("busNumber")}/{disk.get("unitNumber")}',
                'size': int(disk.get('sizeMb', 1024)/1024),
                'az': '',
                'type': disk.get('storageProfile', '').get('name', '')
            }})

        addresses = []
        subnets = []
        subnetids = []
        computername = [x for x in vm_json['section'] if x['_type']
                        == 'GuestCustomizationSectionType'][0]['computerName']

        for adapter in [x for x in vm_json['section'] if x['_type'] == 'NetworkConnectionSectionType'][0]['networkConnection']:
            addresses.append(adapter['ipAddress'])

            query = 'https://'+site+'/api/query?type=vAppNetwork&filter=name==' + \
                adapter.get("network")+';vAppName=='+vm.get("containerName")
            try:
                subnet_request = cloudapi.get_cloud_enterprise_req(
                    url=query, bearer=access_token, version=api_init)
                s = json.loads(subnet_request.text)
            except Exception as err:
                continue
            else:
                if adapter['network'] not in subnets:
                    subnets.append(adapter['network'])
                if len(s['record']) > 0:
                    networkid = prefix + 'vappnets.' + \
                        s['record'][0]['href'].split('/')[-1]
                else:
                    networkid = None
                if networkid not in subnetids:
                    subnetids.append(networkid)

        vdc_id = prefix + 'vdcs.' + vm['vdc'].split('/')[-1]
        vapp_id = prefix + 'vapps.' + \
            vm['container'].split('/')[-1].split('-', 1)[-1]

        yaml_structure = {
            'id': vm_id,
            'type': 'Виртуальный',
            'title': computername,
            'fqdn': computername,
            'description': vm_json['description'],
            'os': {
                'type': [x for x in vm_json['section'] if x['_type'] == 'OperatingSystemSectionType'][0]['description']['value'],
                'bit': [x for x in vm_json['section'] if x['_type'] == 'VmSpecSectionType'][0]['virtualCpuType'].split('_')[-1]
            },
            'cpu': {
                'cores': [x for x in vm_json['section'] if x['_type'] == 'VmSpecSectionType'][0]['numCpus'],
                'frequency': '',
            },
            'ram': [x for x in vm_json['section'] if x['_type'] == 'VmSpecSectionType'][0]['memoryResourceMb']['configured'],
            'nic_qty': len([x for x in vm_json['section'] if x['_type'] == 'NetworkConnectionSectionType'][0]['networkConnection']),
            'subnets': [],
            'disks': [],
            'reverse': {
                'reverse_type': 'VMwareCloud',
                'original_id': vm_urn_id,
                'addresses': [],
                'subnet_titles': [],
                'tags': [],
                'vdc': vdc_id,
                'vdc_title': vm['vdcName'],
                'vapp': vapp_id,
                'tenant': dc
            }
        }

        yaml_structure['disks'] = disks
        yaml_structure['reverse']['addresses'] = addresses
        yaml_structure['subnets'] = subnetids
        yaml_structure['reverse']['subnet_titles'] = subnets

        vms_list['seaf.ta.components.server'][vm_seaf_id] = yaml_structure

    save(vms_list, exportpath, 'enterprise_vms')


def export_vapps(config):

    site = config["site"]
    access_token = config["access_token"]
    api_init = config["api_init"]
    prefix = config["prefix"]
    dc = config["dc"]
    exportpath = config["exportpath"]

    # Получаем vApps
    vapps = []
    vapps_list = {'seaf.ta.reverse.vmwarecloud.vapps': {}}

    # Initial request
    query = f'https://{site}/api/query?type=vApp&pageSize=100'
    try:
        vapps_request = cloudapi.get_cloud_enterprise_req(
            url=query, bearer=access_token, version=api_init)
        vapps_json = json.loads(vapps_request.text)
    except Exception as err:
        print(err.strerror)
    else:
        print(vapps_request.status_code)

    # Putting first batch to the list
    for vapp in vapps_json.get('record', ''):
        vapps.append(vapp)

    # Working with pages if there are more than one
    pagecount = math.ceil(vapps_json.get('total') / vapps_json.get('pageSize'))
    if pagecount > 1:
        items = cloudapi.get_pages(pagecount, query, api_init, access_token)
        for item in items:
            vapps.append(item)

    # Getting vapp details
    for vapp in vapps:
        query = vapp['href']
        try:
            vapp_details_req = cloudapi.get_cloud_enterprise_req(
                url=query, bearer=access_token, version=api_init)
            vapp_details_json = json.loads(vapp_details_req.text)
        except ExceptionGroup as err:
            continue

        vapp_urn_id = vapp_details_json.get('id', '')
        vapp_id = vapp_urn_id.split(':')[-1]
        vapp_seaf_id = prefix + 'vapps.' + vapp_id

        vdc_id = prefix + 'vdcs.' + vapp.get('vdc', '').split('/')[-1]

        yaml_structure = {
            'id': vapp_id,
            'original_id': vapp_urn_id,
            'title': vapp.get('name', ''),
            'description': vapp.get('description', ''),
            'vdc': vdc_id,
            'vdc_title': vapp.get('vdcName', ''),
            'dc': dc
        }
        vapps_list['seaf.ta.reverse.vmwarecloud.vapps'][vapp_seaf_id] = yaml_structure

    save(vapps_list, exportpath, 'enterprise_vapps')


def export_vappnets(config):

    site = config["site"]
    access_token = config["access_token"]
    api_init = config["api_init"]
    prefix = config["prefix"]
    dc = config["dc"]
    exportpath = config["exportpath"]

    # Получаем vAppNets
    vappnets = []
    vappnet_list = {'seaf.ta.services.network': {}}

    # Initial request
    query = f'https://{site}/api/query?type=vAppNetwork&format=records&pageSize=100'
    try:
        vappnets_request = cloudapi.get_cloud_enterprise_req(
            url=query, bearer=access_token, version=api_init)
        vappnets_json = json.loads(vappnets_request.text)
    except Exception as err:
        print(err.strerror)
    else:
        print(vappnets_request.status_code)

    # Putting first batch to the list
    for vappnet in vappnets_json.get('record', ''):
        vappnets.append(vappnet)

    # Working with pages if there are more than one
    pagecount = math.ceil(vappnets_json.get('total') /
                          vappnets_json.get('pageSize'))
    if pagecount > 1:
        items = cloudapi.get_pages(pagecount, query, api_init, access_token)
        for item in items:
            vappnets.append(item)

    # Getting vappnet details
    for vappnet in vappnets:
        query = vappnet['href']
        try:
            vappnet_details_req = cloudapi.get_cloud_enterprise_req(
                url=query, bearer=access_token, version=api_init)
            vappnet_details = json.loads(vappnet_details_req.text)
        except Exception as err:
            continue

        dns = []
        iter = []
        if vappnet['dns1'] is not None and vappnet['dns1'] is not None:
            iter = [vappnet['dns1'], vappnet['dns2']]
        elif vappnet['dns1'] is not None:
            iter = [vappnet['dns1']]
        elif vappnet['dns2'] is not None:
            iter = [vappnet['dns2']]
        for item in iter:
            if re.match(r'^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}', item):
                dns.append(item)
        if 'parentNetwork' in vappnet_details['configuration']:
            if vappnet_details['configuration']['parentNetwork'] != None:
                parentnetwork_id = prefix + 'orgnets.' + \
                    vappnet_details['configuration']['parentNetwork']['id'].split(
                        ':')[-1]
            else:
                parentnetwork_id = None
        else:
            parentnetwork_id = None

        vappnet_urn_id = vappnet_details.get('id')
        vappnet_id = vappnet_urn_id.split(':')[-1]
        vappnet_seaf_id = prefix + 'vappnets.' + vappnet_id

        vapp_id = prefix + "vapps." + \
            vappnet['vApp'].split('/')[-1].split('-', 1)[-1]

        if vappnet['otherAttributes']['isLinked'] == 'true':
            islinked = True
        else:
            islinked = False

        yaml_structure = {
            'id': vappnet_id,
            'title': vappnet['name'],
            'type': 'Проводная',
            'lan_type': 'LAN',
            'az': '',
            'segment': '',
            'vlan': '',
            'ipnetwork': '',
            'purpose': '',
            'network_appliance_id': '',
            'reverse': {
                'reverse_type': 'VMwareCloud',
                'type': 'vAppNetwork',
                'original_id': vappnet_urn_id,
                'vapp': vapp_id,
                'gateway': vappnet['gateway'],
                'netmask': vappnet['netmask'],
                'dns': dns,
                'fencemode': vappnet_details['configuration']['fenceMode'],
                'connected': islinked,
                'parentnetwork': parentnetwork_id,
                'ipscopes': []
            },
            'dc': dc
        }

        ipscope = []
        if 'ipScopes' in vappnet_details['configuration']:
            for scope in vappnet_details['configuration']['ipScopes']['ipScope']:
                if scope['ipRanges'] != None:
                    ipranges = map(lambda w: {'startaddress': w['startAddress'],
                                              'endaddress': w['endAddress']}, scope['ipRanges']['ipRange'])
                    yaml_scope = {
                        'gateway': scope.get('gateway', ''),
                        'netmask': scope.get('netmask', ''),
                        'subnetprefixlength': scope.get('subnetPrefixLength', ''),
                        'ipranges': [x for x in ipranges]
                    }
                    ipscope.append(yaml_scope)
        yaml_structure['reverse']['ipscopes'] = ipscope

        vappnet_list['seaf.ta.services.network'][vappnet_seaf_id] = yaml_structure

    save(vappnet_list, exportpath, 'enterprise_vappnets')


def export_edgenat(config):

    site = config["site"]
    access_token = config["access_token"]
    api_init = config["api_init"]
    prefix = config["prefix"]
    dc = config["dc"]
    exportpath = config["exportpath"]

    # Получаем edgeGWNat
    egws = []
    nat_list = {'seaf.ta.reverse.vmwarecloud.egws_nat': {}}

    # Initial request
    query = f'https://{site}/api/query?type=edgeGateway&format=records&pageSize=100'
    try:
        r = cloudapi.get_cloud_enterprise_req(
            url=query, bearer=access_token, version=api_init)
        r_json = json.loads(r.text)
    except Exception as err:
        print(err.strerror)
    else:
        print(r.status_code)

    # Putting first batch to the list
    for item in r_json.get('record', ''):
        egws.append(item)

    # Working with pages if there are more than one
    pagecount = math.ceil(r_json.get('total') / r_json.get('pageSize'))
    if pagecount > 1:
        items = cloudapi.get_pages(pagecount, query, api_init, access_token)
        for item in items:
            egws.append(item)

    for gw in egws:
        gw_id = gw['href'].split('/')[-1]
        gw_seaf_id = prefix + 'egws.' + gw_id
        gw_urn_id = 'urn:vcloud:gateway:' + gw_id

        # Получаем данные о NAT правилах
        query = f'https://{site}/cloudapi/1.0.0/edgeGateways/{gw_urn_id}/nat/rules'
        try:
            r = cloudapi.get_cloudapi(
                url=query, bearer=access_token, version=api_init)
            r_json = json.loads(r.text)
        except Exception as err:
            print(err.strerror)
            continue

        for value in r_json['values']:
            id = value['id']
            seaf_id = prefix + 'egws_nat.' + id
            name = value.get('name', '')

            yaml_structure = {
                'id': id,
                'gw': gw_seaf_id,
                'title': name,
                'description': value.get('description', ''),
                'enabled': value.get('enabled', ''),
                'type': value.get('type', ''),
                'rule_type': value.get('ruleType', ''),
                'external_address': value.get('externalAddresses', ''),
                'internal_address': value.get('internalAddresses', ''),
                'system_rule': value.get('systemRule', ''),
                'snat_dst_address': value.get('snatDestinationAddresses', ''),
                'dnat_ext_port': value.get('dnatExternalPort', ''),
                'fw_match': value.get('firewallMatch', ''),
                'dc': dc
            }
            nat_list['seaf.ta.reverse.vmwarecloud.egws_nat'][seaf_id] = yaml_structure

    save(nat_list, exportpath, 'enterprise_egws_nat')


def export_edgefw(config):

    site = config["site"]
    access_token = config["access_token"]
    api_init = config["api_init"]
    prefix = config["prefix"]
    dc = config["dc"]
    exportpath = config["exportpath"]

    egws = []
    fw_list = {'seaf.ta.reverse.vmwarecloud.egws_fw': {}}

    query = f'https://{site}/api/query?type=edgeGateway&format=records&pageSize=100'
    try:
        r = cloudapi.get_cloud_enterprise_req(
            url=query, bearer=access_token, version=api_init)
        r_json = json.loads(r.text)
    except Exception as err:
        print(err.strerror)
    else:
        print(r.status_code)

    # Putting first batch to the list
    for item in r_json.get('record', ''):
        egws.append(item)

    # Working with pages if there are more than one
    pagecount = math.ceil(r_json.get('total') / r_json.get('pageSize'))
    if pagecount > 1:
        items = cloudapi.get_pages(pagecount, query, api_init, access_token)
        for item in items:
            egws.append(item)

    for gw in egws:
        gw_id = gw['href'].split('/')[-1]
        gw_seaf_id = prefix + 'egws.' + gw_id
        gw_urn_id = 'urn:vcloud:gateway:' + gw_id

        # Получаем данные о FW правилах
        query = f'https://{site}/cloudapi/1.0.0/edgeGateways/{gw_urn_id}/firewall/rules'
        try:
            r = cloudapi.get_cloudapi(
                url=query, bearer=access_token, version=api_init)
            r_json = json.loads(r.text)
        except Exception as err:
            print(err.strerror)
            continue

        if 'userDefinedRules' not in r_json or r_json['userDefinedRules'] is None:
            continue
        for rule in r_json.get('userDefinedRules'):
            id = rule['id']
            seaf_id = prefix + 'egws_fw.' + id
            name = rule.get('name', '')

            yaml_structure = {
                'id': id,
                'gw': gw_seaf_id,
                'title': name,
                'description': rule.get('description', ''),
                'enabled': rule.get('enabled'),
                'sourceFirewallGroups': rule.get('sourceFirewallGroups', ''),
                'destinationFirewallGroups': rule.get('destinationFirewallGroups', ''),
                'ip_protocol': rule.get('ipProtocol', ''),
                'action': rule.get('action', ''),
                'action_value': rule.get('actionValue', ''),
                'direction': rule.get('direction', ''),
                'port_profiles': [],
                'dc': dc
            }

            src_fw_groups = {}
            if rule['sourceFirewallGroups'] != None:
                for group in rule['sourceFirewallGroups']:
                    fw_group_id = group['id']
                    query = f'https://{site}/cloudapi/1.0.0/firewallGroups/{fw_group_id}'
                    try:
                        r = cloudapi.get_cloudapi(
                            url=query, bearer=access_token, version=api_init)
                        r_json = json.loads(r.text)
                    except Exception as err:
                        print(err.strerror)
                        continue

                    srcmembers = []
                    if r_json['members'] != None:
                        src_mem_list = [x['id'] for x in r_json['members']]
                        for item in src_mem_list:
                            if re.match(r'.*:network:.*', item):
                                item_id = prefix + 'orgnets.' + \
                                    item.split(':')[-1]
                                srcmembers.append(item_id)
                            elif re.match(r'.*:vm:.*', item):
                                item_id = prefix + 'vms.' + item.split(':')[-1]
                                srcmembers.append(item_id)
                            else:
                                srcmembers.append(item)

                    else:
                        srcmembers = None

                    yaml_src_fw = {
                        'type': r_json['type'],
                        'ip_addresses': r_json['ipAddresses'],
                        'members': srcmembers
                    }

                    src_fw_groups[fw_group_id] = yaml_src_fw

            yaml_structure['sourceFirewallGroups'] = src_fw_groups

            dst_fw_groups = {}
            if rule['destinationFirewallGroups'] != None:
                for group in rule['destinationFirewallGroups']:
                    fw_group_id = group['id']
                    query = f'https://{site}/cloudapi/1.0.0/firewallGroups/{fw_group_id}'
                    try:
                        r = cloudapi.get_cloudapi(
                            url=query, bearer=access_token, version=api_init)
                        r_json = json.loads(r.text)
                    except Exception as err:
                        print(err.strerror)
                        continue

                    dstmembers = []
                    if r_json['members'] != None:
                        dst_mem_list = [x['id'] for x in r_json['members']]
                        for item in dst_mem_list:
                            if re.match(r'.*:network:.*', item):
                                item_id = prefix + 'networks.' + \
                                    item.split(':')[-1]
                                dstmembers.append(item_id)
                            elif re.match(r'.*:vm:.*', item):
                                item_id = prefix + 'vms.' + item.split(':')[-1]
                                dstmembers.append(item_id)
                            else:
                                dstmembers.append(item)

                    else:
                        dstmembers = None
                    print(dstmembers)
                    yaml_dst_fw = {
                        'type': r_json['type'],
                        'ip_addresses': r_json['ipAddresses'],
                        'members': dstmembers
                    }

                    dst_fw_groups[fw_group_id] = yaml_dst_fw

            yaml_structure['destinationFirewallGroups'] = dst_fw_groups

            port_profiles = {}
            if 'applicationPortProfiles' in rule and rule['applicationPortProfiles'] != None:
                for profile in rule['applicationPortProfiles']:
                    profile_id = profile['id']
                    query = 'https://'+site+'/cloudapi/1.0.0/applicationPortProfiles/'+profile_id
                    try:
                        r = cloudapi.get_cloudapi(
                            url=query, bearer=access_token, version=api_init)
                        r_json = json.loads(r.text)
                    except Exception as err:
                        print(err.strerror)
                        continue

                    name = profile['name']
                    ports = []
                    for port in r_json['applicationPorts']:
                        yaml_port = {
                            'protocol': port['protocol'],
                            'dst_ports': port['destinationPorts']
                        }
                        ports.append(yaml_port)
                    port_profiles[name] = ports

                yaml_structure['port_profiles'] = port_profiles
            fw_list['seaf.ta.reverse.vmwarecloud.egws_fw'][seaf_id] = yaml_structure

    save(fw_list, exportpath, 'enterprise_egws_fw')


def init_config(script_path, config_file):

    configpath = script_path + '/' + config_file
    config = configparser.ConfigParser()
    config.read(configpath)

    # Setting Connection properties
    site = config['connection']['host']
    tenant = config['connection']['tenant']
    dc = config['params']['DC']

    # Setting Access or Refresh Token
    if config.has_option('connection', 'access_token'):
        access_token = {'access_token': config['connection']['access_token']
                        } if config['connection']['access_token'] not in [None, ''] else None
    if config.has_option('connection', 'refresh_token'):
        refresh_token = config['connection']['refresh_token']

    # Setting prefix
    prefix = ''
    if config.has_option('params', 'root'):
        prefix = (config['params']['root'] +
                  '.') if config['params']['root'] not in (None, '') else ''
    if config.has_option('params', 'domain'):
        prefix = (prefix + config['params']['domain'] +
                  '.') if config['params']['domain'] not in (None, '') else ''

    # Setting export path
    exportpath = config['params'].get('exportpath', script_path)

    # get access token
    if access_token == None:
        try:
            token_request = cloudapi.get_cloud_enterprise_auth(
                site=site, tenant=tenant, token=refresh_token)
            access_token = json.loads(token_request.text)
        except Exception as err:
            print(err.strerror)
        else:
            try:
                with open(f'{exportpath}/key.txt', 'w', encoding='utf-8') as outfile:
                    outfile.write(token_request.text)
            except Exception as err:
                print(err.strerror)

    return {
        "site": site,
        "tentant": tenant,
        "dc": dc,
        "prefix": prefix,
        "exportpath": exportpath,
        "access_token": access_token,
        "api_init": cloudapi.get_api_versions(site=site)
    }


def save(object, path, name):
    filename = "{}/{}.yaml".format(path, name)
    with open(filename, "w", encoding="utf-8") as outfile:
        yaml.dump(object, outfile, allow_unicode=True,
                  encoding="utf-8", sort_keys=False)
        print("saved", filename)
    return filename
