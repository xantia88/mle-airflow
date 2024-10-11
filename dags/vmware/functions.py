import yaml
from typing import Iterable


def export_datacenters(dcs, exportpath):
    prefix = ""
    location = ""
    alldcs_json = {"seaf.ta.reverse.vmwareonprem.vdcs": {}}
    for json_dc in dcs:

        dc_id = prefix + "vdcs." + json_dc.get("_vimid")
        dc_dict = {
            "id": json_dc.get("_vimid"),
            "original_id": json_dc.get("_vimref"),
            "title": json_dc.get("name"),
            "datastores": json_dc.get("datastore"),
            "networks": [f"{prefix}network.{x.split(':')[-1]}" for x in json_dc.get("network")],
            "dc": location
        }

        alldcs_json["seaf.ta.reverse.vmwareonprem.vdcs"][f"{dc_id}"] = dc_dict

    save(alldcs_json, exportpath, "dcs")


def export_vms(vms, dc, exportpath):
    prefix = ""
    allvms_json = {"seaf.ta.components.server": {}}
    allvms_list = []
    for json_vm in vms:
        allvms_list.append(json_vm)
        vm_id = prefix + "server." + json_vm.get("_vimid")
        dc_id = prefix + "vdcs." + dc._moId

        vapp_id = [f"{prefix}vapps.{x.split(':')[-1]}" if not (
            x in {None, "", "null"}) else '' for x in json_vm.get("parentVApp", "") or []]

        yaml_structure = {
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
                'vdc_title': dc.name
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

        yaml_structure['disks'] = disks

        allvms_json["seaf.ta.components.server"][f"{vm_id}"] = yaml_structure

    save(allvms_json, exportpath, f"vms_{dc._moId}")


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
