import json
import urllib2


def getProxy(type='proxy_icekredit'):
    proxies = {
        "proxy_icekredit": "http://proxy.icekredit.com/api/v2/proxy/adsl"
    }
    addr = proxies[type]
    req = urllib2.Request(addr)
    response = urllib2.urlopen(req, timeout=5).read()
    items = json.loads(response)
    ip_list = items["data"]["proxy_list"]
    return ip_list
