from pyVim.connect import SmartConnect
from pyVmomi import vim, VmomiSupport
import ssl
import json


def connect(host, user, pwd):
    connection_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    connection_context.verify_mode = ssl.CERT_NONE
    connection = SmartConnect(
        host=host, user=user, pwd=pwd, sslContext=connection_context)
    content = connection.content
    return content


def get_dcs(content):
    return get_all_objs(content, [vim.Datacenter])


def get_vms(content, dc):
    return get_all_objs(content, [vim.VirtualMachine], dc)


def get_vapps(content, dc):
    return get_all_objs(content, [vim.VirtualApp], dc)


def get_networks(content, dc):
    return get_all_objs(content, [vim.Network], dc)


def get_dvswitches(content, dc):
    return get_all_objs(content, [vim.DistributedVirtualSwitch], dc)


def get_dvpgroups(content, dc):
    return get_all_objs(content, [vim.dvs.DistributedVirtualPortgroup], dc)


def getVlans(pg):
    vlan_info = pg.config.defaultPortConfig.vlan
    vlan_spec = vim.dvs.VmwareDistributedVirtualSwitch.TrunkVlanSpec
    if isinstance(vlan_info, vlan_spec):
        vlanlist = []
        for item in vlan_info.vlanId:
            if item.start == item.end:
                vlanlist.append(str(item.start))
            else:
                vlanlist.append(str(item.start)+' - '+str(item.end))
        return vlanlist
    else:
        return [str(vlan_info.vlanId)]


def get_all_objs(content, vimtype, folder=None):
    obj = []
    if folder == None:
        folder = content.rootFolder
    container = content.viewManager.CreateContainerView(
        folder, vimtype, True)
    for managed_object_ref in container.view:
        obj.append(managed_object_ref)
    return obj


def json(objects):
    return [convert_to_json(object) for object in objects]


def convert_to_json(obj):
    return json.loads(json.dumps(obj, cls=VmomiSupport.VmomiJSONEncoder))