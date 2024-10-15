import yaml
from typing import Iterable


def export_dcs(dcs, config):

    prefix = config["prefix"]
    location = config["location"]
    exportpath = config["output"]

    alldcs_json = {"seaf.ta.reverse.vmwareonprem.vdcs": {}}
    for json_dc in dcs:

        dc_id = prefix + "vdcs." + json_dc.get("_vimid")

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

    print("dc", dc)

    prefix = config["prefix"]
    exportpath = config["output"]

    allvms_json = {"seaf.ta.components.server": {}}
    for json_vm in vms:

        vm_id = prefix + "server." + json_vm.get("_vimid")
        dc_id = prefix + "vdcs." + dc.get("_moId")
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
                'vdc': dc_id,
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

        vapp_id = prefix + "vapps." + json_vapp.get("_vimid")
        dc_id = prefix + "vdcs." + dc.get("_moId")

        allvapps_json["seaf.ta.reverse.vmwareonprem.vapps"][vapp_id] = {
            'id': json_vapp.get("_vimid"),
            'original_id': json_vapp.get("_vimref"),
            'title': json_vapp.get("name"),
            'description': json_vapp.get("config").get("annotation"),
            'tags': [],
            'vdc': dc_id,
            'vdc_tile': dc.get("name")
        }

    save(allvapps_json, exportpath, get_file_name("vapps", dc))


def export_networks(networks, dc, config):

    prefix = config["prefix"]
    location = config["location"]
    exportpath = config["output"]

    allnetworks_json = {"seaf.ta.services.network": {}}
    for json_network in networks:

        network_id = prefix + "network." + json_network.get("_vimid")
        dc_id = prefix + "vdcs." + dc.get("_moId")

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
                'vdc': dc_id,
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

        switch_id = prefix + "network." + json_switch.get("_vimid")
        dc_id = prefix + "vdcs." + dc.get("_moId")

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
                'vdc': dc_id,
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

        id = prefix + "dvportgroups." + json_pg.get("_vimid")
        dc_id = prefix + "vdc." + dc.get("_moId")

        alldvportgroups_json["seaf.ta.reverse.vmwareonprem.dvportgroups"][id] = {
            'id': json_pg.get("_vimid"),
            'original_id': json_pg.get("_vimref"),
            'title': json_pg.get("name"),
            'description': '',
            'subnets': '',
            'dvswitch': prefix + "dvswitch." + json_pg.get("config").get("distributedVirtualSwitch").split(":")[-1],
            'vlan': json_pg["vlan_id"],
            'vdc': dc_id,
            'vdc_title': dc.get("name")
        }

    save(alldvportgroups_json, exportpath, get_file_name("dvportgroups", dc))


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
