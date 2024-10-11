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


def get_datacenters(content):
    return get_all_objs(content, [vim.Datacenter])


def get_vms(content, dc):
    return get_all_objs(content, [vim.VirtualMachine], dc)


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
