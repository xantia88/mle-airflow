from advanced import signer
import csv
import requests
import json


def get_scloud(**kwarg):

    with open(kwarg['credentials']) as credentials_file:
        csv_reader = csv.DictReader(credentials_file, delimiter=",")
        for row in csv_reader:
            access_key = row['Access Key Id']
            secret_key = row['Secret Access Key']
    ######################################################
    # Creating Signature object for further use as a request
    sig = signer.Signer()
    sig.Key = access_key
    sig.Secret = secret_key
    ######################################################

    # Working with request according to parameters set
    if kwarg['service'] == 'ecs' and kwarg['item'] == None and kwarg['s_type'] == None:

        cloud_query = 'https://' + kwarg['service'] + '.' + kwarg['region'] + \
            '.hc.sbercloud.ru/v1/' + \
            kwarg['project'] + '/cloudservers/detail?limit=50'

        paginated = True
    elif kwarg['service'] == 'ecs' and kwarg['s_type'] == 'nic':

        cloud_query = 'https://' + kwarg['service'] + '.' + kwarg['region'] + \
            '.hc.sbercloud.ru/v1/'+kwarg['project'] + \
            '/cloudservers/'+kwarg['item']+'/os-interface'

        paginated = False
    elif kwarg['service'] == 'vpc' and kwarg['s_type'] == None:

        cloud_query = 'https://' + \
            kwarg['service']+'.'+kwarg['region'] + \
            '.hc.sbercloud.ru/v1/'+kwarg['project']+'/vpcs'

        paginated = False
    elif kwarg['service'] == 'eip' and kwarg['s_type'] == None:

        cloud_query = 'https://vpc.' + \
            kwarg['region']+'.hc.sbercloud.ru/v1/' + \
            kwarg['project']+'/publicips'

        paginated = False
    elif kwarg['service'] == 'evs':

        cloud_query = 'https://'+kwarg['service']+'.'+kwarg['region'] + \
            '.hc.sbercloud.ru/v2/'+kwarg['project'] + \
            '/os-vendor-volumes/'+kwarg['item']

        paginated = False
    elif kwarg['service'] == 'vpc' and kwarg['s_type'] == 'subnet':

        cloud_query = 'https://' + \
            kwarg['service']+'.'+kwarg['region'] + \
            '.hc.sbercloud.ru/v1/'+kwarg['project']+'/subnets'

        paginated = False
    elif kwarg['service'] == 'vpc' and kwarg['s_type'] == 'security-groups':

        cloud_query = 'https://'+kwarg['service']+'.'+kwarg['region'] + \
            '.hc.sbercloud.ru/v1/'+kwarg['project']+'/'+kwarg['s_type']

        paginated = False
    elif kwarg['service'] == 'vpc' and kwarg['s_type'] == 'peering':

        cloud_query = 'https://' + \
            kwarg['service']+'.'+kwarg['region'] + \
            '.hc.sbercloud.ru/v2.0/vpc/peerings'

        paginated = False
    elif kwarg['service'] == 'vpc' and kwarg['s_type'] == 'routes':

        cloud_query = 'https://'+kwarg['service']+'.' + \
            kwarg['region']+'.hc.sbercloud.ru/v2.0/vpc/routes'

        paginated = False
    elif kwarg['service'] == 'cbr' and kwarg['s_type'] == 'vault':

        cloud_query = 'https://' + \
            kwarg['service']+'.'+kwarg['region'] + \
            '.hc.sbercloud.ru/v3/'+kwarg['project']+'/vaults'

        paginated = False
    elif kwarg['service'] == 'cbr' and kwarg['s_type'] == 'policy':

        cloud_query = 'https://' + \
            kwarg['service']+'.'+kwarg['region'] + \
            '.hc.sbercloud.ru/v3/'+kwarg['project']+'/policies'

        paginated = False
    elif kwarg['service'] == 'rds' and kwarg['s_type'] == None:

        cloud_query = 'https://'+kwarg['service']+'.'+kwarg['region'] + \
            '.hc.sbercloud.ru/v3/'+kwarg['project']+'/instances'

        paginated = False
    elif kwarg['service'] == 'iam':

        cloud_query = 'https://'+kwarg['service']+'.' + \
            kwarg['region']+'.hc.sbercloud.ru/v3/projects'

        paginated = False
    elif kwarg['service'] == 'vpc' and kwarg['s_type'] == 'port' and kwarg['item'] != None:

        cloud_query = 'https://' + \
            kwarg['service']+'.'+kwarg['region'] + \
            '.hc.sbercloud.ru/v1/ports/'+kwarg['item']

        paginated = False
    elif kwarg['service'] == 'vpc' and kwarg['s_type'] == 'ports':

        cloud_query = 'https://'+kwarg['service']+'.'+kwarg['region'] + \
            '.hc.sbercloud.ru/v1/ports?device_id='+kwarg['item']

        paginated = False
    elif kwarg['service'] == 'vpc' and kwarg['s_type'] == 'port_filter' and kwarg['item'] != None:

        cloud_query = 'https://' + \
            kwarg['service']+'.'+kwarg['region'] + \
            '.hc.sbercloud.ru/v1/ports?'+kwarg['item']

        paginated = False
    elif kwarg['service'] == 'vpc' and kwarg['s_type'] == 'privateips':

        cloud_query = 'https://'+kwarg['service']+'.'+kwarg['region'] + \
            '.hc.sbercloud.ru/v1/'+kwarg['project'] + \
            '/subnets/'+kwarg['item']+'/privateips'

        paginated = False
    elif kwarg['service'] == 'nat' and kwarg['s_type'] == 'gateway' and kwarg['item'] == None:

        cloud_query = 'https://'+kwarg['service']+'.'+kwarg['region'] + \
            '.hc.sbercloud.ru/v2/'+kwarg['project']+'/nat_gateways'

        paginated = False
    elif kwarg['service'] == 'nat' and (kwarg['s_type'] == 'snat' or kwarg['s_type'] == 'dnat'):

        cloud_query = 'https://'+kwarg['service']+'.'+kwarg['region'] + \
            '.hc.sbercloud.ru/v2/' + \
            kwarg['project']+'/'+kwarg['s_type']+'_rules'

        paginated = False
    elif kwarg['service'] == 'elb' and kwarg['s_type'] == 'lb':

        cloud_query = 'https://'+kwarg['service']+'.'+kwarg['region'] + \
            '.hc.sbercloud.ru/v2/'+kwarg['project']+'/elb/loadbalancers'

        paginated = False
    elif kwarg['service'] == 'elb' and kwarg['s_type'] in ['pools', 'listeners', 'poolmembers']:
        if kwarg['s_type'] == 'poolmembers':

            cloud_query = 'https://'+kwarg['service']+'.'+kwarg['region'] + \
                '.hc.sbercloud.ru/v2/'+kwarg['project'] + \
                '/elb/pools/'+kwarg['item']+'/members'

        elif kwarg['s_type'] == 'pools' and kwarg['item'] == None:

            cloud_query = 'https://' + \
                kwarg['service']+'.'+kwarg['region'] + \
                '.hc.sbercloud.ru/v2/'+kwarg['project']+'/elb/pools'

        else:

            cloud_query = 'https://'+kwarg['service']+'.'+kwarg['region'] + \
                '.hc.sbercloud.ru/v2/'+kwarg['project'] + \
                '/elb/'+kwarg['s_type']+'/'+kwarg['item']

        paginated = False
    elif kwarg['service'] == 'elb' and kwarg['s_type'] == 'l7policies':
        if kwarg['item'] != None:

            cloud_query = 'https://'+kwarg['service']+'.'+kwarg['region'] + \
                '.hc.sbercloud.ru/v2/' + \
                kwarg['project']+'/elb/l7policies?'+kwarg['item']

        else:

            cloud_query = 'https://'+kwarg['service']+'.'+kwarg['region'] + \
                '.hc.sbercloud.ru/v2/'+kwarg['project']+'/elb/l7policies'

        paginated = False
    elif kwarg['service'] == 'cce':
        if kwarg['s_type'] == 'clusters':

            cloud_query = 'https://'+kwarg['service']+'.'+kwarg['region'] + \
                '.hc.sbercloud.ru/api/v3/projects/' + \
                kwarg['project']+'/clusters'

        paginated = False
    elif kwarg['service'] == 'dms':

        cloud_query = 'https://'+kwarg['service']+'.'+kwarg['region'] + \
            '.hc.sbercloud.ru/v1.0/'+kwarg['project']+'/instances'

        paginated = False

    if cloud_query != None:
        r = signer.HttpRequest("GET", cloud_query)
        if kwarg['project'] != None:
            r.headers = {"X-Project-Id": kwarg['project']}
        if kwarg['service'] == 'cce':
            r.headers = {"Content-Type": "application/json;charset=utf-8"}
        sig.Sign(r)
        resp = requests.request(
            r.method, r.scheme + "://" + r.host + r.uri, headers=r.headers, data=r.body)

        jsondata = json.loads(resp.text)
        if kwarg['service'] == 'ecs' and kwarg['s_type'] == None:
            jsondata_ecs = jsondata['servers']
        if paginated == True:
            pages = (jsondata['count'] // 50) + (jsondata['count'] % 50 > 0)
            if pages > 1:
                page = 2
                while page <= pages:

                    cloud_query = 'https://'+kwarg['service']+'.'+kwarg['region'] + \
                        '.hc.sbercloud.ru/v1/' + \
                        kwarg['project'] + \
                        '/cloudservers/detail?limit=50&offset='+page

                    page += 1
                    r = signer.HttpRequest("GET", cloud_query)
                    r.headers = {"X-Project-Id": kwarg['project']}
                    sig.Sign(r)
                    resp = requests.request(
                        r.method, r.scheme + "://" + r.host + r.uri, headers=r.headers, data=r.body)
                    temp = json.loads(resp.text)
                    jsondata_ecs += temp['servers']
                jsondata = jsondata_ecs
            else:
                jsondata = jsondata_ecs
        return jsondata
