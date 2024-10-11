import requests

from pyVim.connect import SmartConnect
from pyVmomi import vim, VmomiSupport
import ssl
import yaml
import json


def get_all_objs(content, vimtype, folder=None):
    obj = []
    if folder == None:
        folder = content.rootFolder
    container = content.viewManager.CreateContainerView(
        folder, vimtype, True)
    for managed_object_ref in container.view:
        obj.append(managed_object_ref)
    return obj


def get_all_datacenters(content):
    return get_all_objs(content, [vim.Datacenter])


def get_datacenters(getAllDCs):
    alldcs_json = {"seaf.ta.reverse.vmwareonprem.vdcs": {}}
    alldcs_list = []
    for dc in getAllDCs:
        try:
            json_dc = json.loads(json.dumps(
                dc, cls=VmomiSupport.VmomiJSONEncoder))
            alldcs_list.append(json_dc)
        except:
            print(Exception)

        prefix = ""
        location = ""

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

    return alldcs_json


def vsphere_connect(host, user, pwd):
    connection_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    connection_context.verify_mode = ssl.CERT_NONE
    connection = SmartConnect(
        host=host, user=user, pwd=pwd, sslContext=connection_context)
    content = connection.content
    return content


def save(object, path, name):
    filename = "{}/{}.yaml".format(path, name)
    with open(filename, "w", encoding="utf-8") as outfile:
        yaml.dump(object, outfile, allow_unicode=True,
                  encoding="utf-8", sort_keys=False)
        print("saved", filename)
    return filename
