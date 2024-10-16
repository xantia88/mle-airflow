import yaml
from typing import Iterable


def export_dcs(dcs, config):

    prefix = config["prefix"]
    location = config["location"]
    exportpath = config["output"]

    alldcs_json = {"seaf.ta.reverse.vmwareonprem.vdcs": {}}
    for json_dc in dcs:

        dc_id = get_id(prefix, "vdcs", json_dc.get("_vimid"))

        alldcs_json["seaf.ta.reverse.vmwareonprem.vdcs"][dc_id] = {
            "id": json_dc.get("_vimid"),
            "original_id": json_dc.get("_vimref"),
            "title": json_dc.get("name"),
            "datastores": json_dc.get("datastore"),
            "networks": [f"{prefix}network.{x.split(':')[-1]}" for x in json_dc.get("network")],
            "dc": location
        }

    save(alldcs_json, exportpath, "dcs")


def export_vms(vms, dc, config):

    prefix = config["prefix"]
    exportpath = config["output"]

    allvms_json = {"seaf.ta.components.server": {}}
    for json_vm in vms:

        vm_id = get_id(prefix, "server", json_vm.get("_vimid"))
        vapp_id = [f"{prefix}vapps.{x.split(':')[-1]}" if not (
            x in {None, "", "null"}) else '' for x in json_vm.get("parentVApp", "") or []]

        allvms_json["seaf.ta.components.server"][vm_id] = {
            'id': json_vm.get("_vimid"),
            'type': 'Виртуальный',
            'title': json_vm.get("name"),
            'fqdn': json_vm.get("guest").get("hostName"),
            'description': json_vm.get("config").get("annotation"),
            'os': {
                'type': json_vm.get("config").get("guestFullName", ""),
                'bit': json_vm.get("config").get("guestId", "")
            },
            'cpu': {
                'cores': json_vm["config"]["hardware"].get("numCPU", ""),
                'frequency': "",
            },
            'ram': json_vm.get("config").get("hardware").get("memoryMB"),
            'nic_qty': len(json_vm.get("guest").get("net")),
            'subnets': [f"{prefix}network.{x.split(':')[-1]}" for x in json_vm.get("network") if not (x in {None, ""})],
            'disks': [],
            'reverse': {
                'reverse_type': 'VMwareOnprem',
                'original_id': json_vm.get("_vimref"),
                'addresses': list(flatten([x.get("ipAddress") for x in json_vm.get("guest").get("net") if x.get("connected") == True])),
                'subnet_titles': list(flatten([x.get("network") for x in json_vm.get("guest").get("net")])),
                'tags': [],
                'vapp': vapp_id,
                'vdc': get_dc_id(prefix, "vdcs", dc),
                'vdc_title': dc.get("name")
            }
        }

        disks = []
        for disk in [x for x in json_vm.get("config").get("hardware").get("device") if x.get("_vimtype") == "vim.vm.device.VirtualDisk"]:
            disk_id = disk.get("key")
            bus = ""
            for device in json_vm.get("config").get("hardware").get("device"):
                if [str(x) == str(disk_id) for x in device.get("device", "")]:
                    bus = device
            disks.append({disk_id: {
                'device': f"{bus.get('busNumber')}/{disk.get('unitNumber')}",
                'size': int(disk.get("capacityInKB")/1024/1024)
            }})

        allvms_json["seaf.ta.components.server"][vm_id]['disks'] = disks

    save(allvms_json, exportpath, get_file_name("vms", dc))


def export_vapps(vapps, dc, config):

    prefix = config["prefix"]
    exportpath = config["output"]

    allvapps_json = {"seaf.ta.reverse.vmwareonprem.vapps": {}}
    for json_vapp in vapps:

        vapp_id = get_id(prefix, "vapps", json_vapp.get("_vimid"))

        allvapps_json["seaf.ta.reverse.vmwareonprem.vapps"][vapp_id] = {
            'id': json_vapp.get("_vimid"),
            'original_id': json_vapp.get("_vimref"),
            'title': json_vapp.get("name"),
            'description': json_vapp.get("config").get("annotation"),
            'tags': [],
            'vdc': get_dc_id(prefix, "vdc", dc),
            'vdc_tile': dc.get("name")
        }

    save(allvapps_json, exportpath, get_file_name("vapps", dc))


def export_networks(networks, dc, config):

    prefix = config["prefix"]
    location = config["location"]
    exportpath = config["output"]

    allnetworks_json = {"seaf.ta.services.network": {}}
    for json_network in networks:

        network_id = get_id(prefix, "network", json_network.get("_vimid"))

        allnetworks_json["seaf.ta.services.network"][network_id] = {
            'id': json_network.get("_vimid"),
            'original_id': json_network.get("_vimref"),
            'title': json_network.get("name"),
            'description': '',
            'type': 'LAN',
            'lan_type': 'Проводная',
            'ipnetwork': '',
            'reverse': {
                'type': 'vmwarenetwork',
                'reverse_type': 'VMwareOnprem',
                'vdc': get_dc_id(prefix, "vdc", dc),
                'vdc_title': dc.get("name")
            },
            'dc_id': [location]
        }

    save(allnetworks_json, exportpath, get_file_name("networks", dc))


def export_dvswitches(dvss, dc, config):

    prefix = config["prefix"]
    location = config["location"]
    exportpath = config["output"]

    alldvswitches_json = {"seaf.ta.components.network": {}}
    for json_switch in dvss:

        switch_id = get_id(prefix, "network", json_switch.get("_vimid"))

        alldvswitches_json["seaf.ta.components.network"][switch_id] = {
            'id': json_switch.get("_vimid"),
            'title': json_switch.get("name"),
            'description': '',
            'realization_type': 'Виртуальный',
            'placement_type': 'Периметр',
            'subnets': '',
            'reverse': {
                'type': 'dvswitch',
                'reverse_type': 'VMwareOnprem',
                'original_id': json_switch.get("_vimref"),
                'vdc': get_dc_id(prefix, "vdc", dc),
                'vdc_title': dc.get("name")
            },
            'dc': location
        }

    save(alldvswitches_json, exportpath, get_file_name("dvswitches", dc))


def export_dvpgroups(dvpgs, dc, config):

    prefix = config["prefix"]
    exportpath = config["output"]

    alldvportgroups_json = {"seaf.ta.reverse.vmwareonprem.dvportgroups": {}}
    for json_pg in dvpgs:

        id = get_id(prefix, "dvportgroup", json_pg.get("_vimid"))

        alldvportgroups_json["seaf.ta.reverse.vmwareonprem.dvportgroups"][id] = {
            'id': json_pg.get("_vimid"),
            'original_id': json_pg.get("_vimref"),
            'title': json_pg.get("name"),
            'description': '',
            'subnets': '',
            'dvswitch': prefix + "dvswitch." + json_pg.get("config").get("distributedVirtualSwitch").split(":")[-1],
            'vlan': json_pg["vlan_id"],
            'vdc': get_dc_id(prefix, "vdc", dc),
            'vdc_title': dc.get("name")
        }

    save(alldvportgroups_json, exportpath, get_file_name("dvportgroups", dc))


def export_hosts(hosts, dc, config):

    prefix = config["prefix"]
    location = config["location"]
    exportpath = config["output"]

    allhosts_json = {"seaf.ta.reverse.vmwareonprem.hosts": {}}

    for vchost in hosts:

        # REFACTORING NEEDED !!!!! (split funtion)
        def get_hostnetwork(host_config):

            # (Function) Physical Nics
            host_pnics = []
            for pnic in host_config.get("network", "").get("pnic", ""):
                pnic_info = dict()
                pnic_info.update(
                    {
                        pnic.get("key"): {
                            'device': pnic.get("device", ""),
                            'driver': pnic.get("driver", ""),
                            'mac': pnic.get("mac", "")
                        }
                    }
                )
                host_pnics.append(pnic_info)

            # (Function) Virtual Nics
            host_vnics = []
            for vnic in host_config.get("network", "").get("vnic", ""):
                vnic_info = dict()
                vnic_info.update(
                    {
                        vnic.get("key"): {
                            'device': vnic.get("device", ""),
                            'portgroup': vnic.get("portgroup", ""),
                            'port': vnic.get("port", ""),
                            'dhcp': vnic.get("spec", "").get("ip", "").get("dhcp", ""),
                            'ipAddress': vnic.get("spec", "").get("ip", "").get("ipAddress", ""),
                            'subnetMask': vnic.get("spec", "").get("ip", "").get("subnetMask", ""),
                            'mac': vnic.get("spec", "").get("mac", ""),
                            'mtu': vnic.get("spec", "").get("mtu", "")
                        }
                    }
                )
                host_vnics.append(vnic_info)

            # (Function) Virtual Switches
            host_vswitches = []
            for vswitch in host_config.get("network", "").get("vswitch", ""):
                vswitch_info = dict()
                vswitch_pnics = []
                vswitch_portgroups = []
                for pnic in vswitch.get("pnic"):
                    vswitch_pnics.append(pnic)
                for pg in vswitch.get("portgroup"):
                    vswitch_portgroups.append(pg)
                vswitch_info.update(
                    {
                        vswitch.get("key", ""): {
                            'name': vswitch.get("name"),
                            'pnics': vswitch_pnics,
                            'portgroups': vswitch_portgroups,
                            'mtu': vswitch.get("mtu", "")
                        }
                    }
                )
                host_vswitches.append(vswitch_info)

            # (Function) Port Groups
            host_portgroups = []
            for portgroup in host_config.get("network", "").get("portgroup", ""):

                portgroup_info = dict()
                nicteamingplc = ""
                if 'nicTeaming' in portgroup.get("spec", "").get("policy", ""):
                    if portgroup.get("spec", "").get("policy", "").get("nicTeaming", "") != None:
                        nicteamingplc = portgroup.get("spec", "").get(
                            "policy", "").get("nicTeaming", "").get("policy", "")
                else:
                    nicteamingplc = None

                if portgroup.get("spec", "").get("policy", "").get("security", "") != None:
                    securitypolicy = portgroup.get("spec", "").get(
                        "policy", "").get("security", "")
                else:
                    securitypolicy = dict()

                portgroup_info.update(
                    {
                        portgroup.get("key", ""): {
                            'name': portgroup.get("spec", "").get("name", ""),
                            'vlanId': portgroup.get("spec", "").get("vlanId", ""),
                            'vswitchName': portgroup.get("spec", "").get("vswitchName", ""),
                            'vswitch_id': portgroup.get("vswitch", ""),
                            'nicTeamingPolicy': nicteamingplc,
                            'allowPromiscuous': securitypolicy.get("allowPromiscuous", ""),
                            'macChanges': securitypolicy.get("macChanges", ""),
                            'forgedTransmits': securitypolicy.get("forgedTransmits", "")
                        }
                    }
                )
                host_portgroups.append(portgroup_info)

            return {
                "pnics": host_pnics,
                "vnics": host_vnics,
                "vswitches": host_vswitches,
                "pgs": host_portgroups
            }

        json_config = vchost.get("config")

        id = get_id(prefix, "hosts", vchost.get("_moId"))

        allhosts_json["seaf.ta.reverse.vmwareonprem.hosts"][id] = {
            'id': vchost.get("_moId"),
            'original_id': vchost.get("original_id"),
            'title': vchost.get("name"),
            'description': '',
            'product': {
                "name": json_config.get("product", "").get("name", ""),
                "version": json_config.get("product", "").get("version", ""),
                "build": json_config.get("product", "").get("build", ""),
                "fullname": json_config.get("product", "").get("fullname", "")
            },
            'network': get_hostnetwork(json_config),
            'vdc': get_dc_id(prefix, "vdcs", dc),
            'vdc_title': dc.get("name"),
            'dc': location
        }

    save(allhosts_json, exportpath, get_file_name("hosts", dc))


def get_id(prefix, name, id):
    return prefix + name + "." + id


def get_dc_id(prefix, name, dc):
    return prefix + name + "." + dc.get("_moId")


def get_file_name(title, dc):
    return "{}_{}".format(title, dc.get("_moId"))


def save(object, path, name):
    filename = "{}/{}.yaml".format(path, name)
    with open(filename, "w", encoding="utf-8") as outfile:
        yaml.dump(object, outfile, allow_unicode=True,
                  encoding="utf-8", sort_keys=False)
        print("saved", filename)
    return filename


def flatten(items):
    for x in items:
        if isinstance(x, Iterable) and not isinstance(x, (str, bytes)):
            for sub_x in flatten(x):
                yield sub_x
        else:
            yield x
