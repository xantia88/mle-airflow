import requests
import json
import lxml.etree as ET


def get_cloudapi(**kwarg):
    url = kwarg['url']
    bearer = kwarg['bearer']
    version = kwarg['version']['version']
    header = {
        'Accept': f'application/json;version={str(version)}',
        'Authorization': 'Bearer ' + bearer['access_token']
    }
    req = requests.get(url, headers=header)
    return req


def get_pages(pagecount, query, api_init, access_token):
    result = []
    for page in range(2, pagecount + 1):
        query = query + f'&page={page}'
        try:
            r = get_cloudapi(url=query, bearer=access_token, version=api_init)
            r_json = json.loads(r.text)
        except Exception as err:
            print(err.strerror)
        else:
            for item in r_json.get('values', ''):
                result.append(item)
    return result


def convert_cidr_to_netmask(cidr):
    cidr = int(cidr)
    mask = (0xffffffff >> (32 - cidr)) << (32 - cidr)
    return (str((0xff000000 & mask) >> 24) + '.' +
            str((0x00ff0000 & mask) >> 16) + '.' +
            str((0x0000ff00 & mask) >> 8) + '.' +
            str((0x000000ff & mask)))


def get_cidr(*args):
    addr = args[0] if args[0] != '' else "0.0.0.0"
    mask = args[1] if args[1] != '' else "0.0.0.0"

    addr = [int(x) for x in addr.split(".")]
    mask = [int(x) for x in mask.split(".")]
    cidr = sum((bin(x).count('1') for x in mask))

    netw = [addr[i] & mask[i] for i in range(4)]

    result = "{0}/{1}".format(('.'.join(map(str, netw))), cidr)
    return result


def get_cloud_enterprise_req(**kwarg):
    url = kwarg['url']
    bearer = kwarg['bearer']
    version = kwarg['version']['version']
    header = {
        'Accept': f'application/*+json;version={str(version)}',
        'Authorization': 'Bearer ' + bearer['access_token']
    }
    req = requests.get(url, headers=header)
    return req


def get_cloud_enterprise_auth(**kwarg):
    site = kwarg['site']
    tenant = kwarg['tenant']
    token = kwarg['token']
    url = f'https://{site}/oauth/tenant/{tenant}/token'
    header = {
        'Accept': 'application/json',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Content-Length': '71'
    }
    data = {
        'grant_type': 'refresh_token',
        'refresh_token': token
    }

    result = requests.post(url, headers=header, data=data)
    return result


def get_api_versions(**kwarg):
    # Определение URL аутентификации
    site = kwarg['site']
    url_ver = f'https://{site}/api/versions'
    res = requests.get(url_ver)
    res_xml = res.text
    parser = ET.XMLParser(ns_clean=True)
    root = ET.fromstring(bytes(res_xml, encoding='utf-8'), parser)

    # Creating namespace for find() and findall()
    ns = '{' + root.nsmap.pop(None) + '}'

    # Choosing latest version
    current_ver = float(0)
    login_url = ''
    for item in root.findall(f'{ns}VersionInfo'):
        if item.get('deprecated') == 'false':
            item_ver = item.findall(f'{ns}Version')[0].text
            if current_ver < float(item_ver):
                current_ver = float(item_ver)
                login_url = item.findall(f'{ns}LoginUrl')[0].text

    result = {'version': current_ver, 'url': login_url}
    return result
