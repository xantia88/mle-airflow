import requests

from pyVim.connect import SmartConnect
from pyVmomi import vim, VmomiSupport
import ssl

def request():
        print("zzz-xxx")
        try:
            print("01")
            r = requests.get("https://iss.moex.com/iss/history/engines/stock/markets/shares/boards/TQBR/securities/SBER?from=2014-01-01&till=2014-01-31")
            print("02")
            print(r.status_code)
            print("03")
        except Exception as e:
            print("04")
            print(e)
        print("zzz-xxx")

def vsphere_connect(host, user, pwd):
    print("01", "connecting to", host, user)
    connection_context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
    connection_context.verify_mode = ssl.CERT_NONE
    print("02", "connection prepared")
    try:
        print("03", "establishing connection")
        connection = SmartConnect(host=host, user=user, pwd=pwd, sslContext=connection_context)
        print("04", "connection established")
        content = connection.content
        print("05", "content length", len(content))
        return content
    except Exception as err:
        print(err)
    return None
