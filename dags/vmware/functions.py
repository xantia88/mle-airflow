import requests

from pyVim.connect import SmartConnect
from pyVmomi import vim, VmomiSupport
import ssl
import yaml

def vsphere_connect(host, user, pwd):
    print("01", "connecting to", host, user)
    connection_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    connection_context.verify_mode = ssl.CERT_NONE
    print("02", "connection prepared")
    try:
        print("03", "establishing connection")
        connection = SmartConnect(
            host=host, user=user, pwd=pwd, sslContext=connection_context
        )
        print("04", "connection established")
        content = connection.content
        print("05", "content length", len(content))
        return content
    except Exception as err:
        print(err)
    return None


def save(object, path, name):
    filename = "{}/{}.yaml".format(path, name)
    with open(filename, "w", encoding="utf-8") as outfile:
        yaml.dump(
            object, outfile, allow_unicode=True, encoding="utf-8", sort_keys=False
        )
    return filename
