from base64 import b64encode
import httplib
import logging
import platform
import socket
import struct
import sys
import time
import urllib
from urlparse import urlparse
import xmltodict

_author__ = 'Robert Nelson'
__copyright__ = "Copyright (C) 2015 Robert Nelson"
__license__ = "BSD"

__all__ = ['IsySystem']


logger = logging.getLogger(__package__)


def discover():
    def external_ip():
        ip = None
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sock.connect(('8.8.8.8', 0))
            ip = sock.getsockname()[0]
        except:
            pass
        return ip

    def isy_ssdp(ddata):
        multicast_group = '239.255.255.250'
        multicast_port = 1900
        server_address = ('', multicast_port)

        # Create the socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        if platform.system() == 'Windows':
            interface_address = external_ip()
        else:
            interface_address = str(socket.INADDR_ANY)
        mreq = struct.pack('4s4s', socket.inet_aton(multicast_group), socket.inet_aton(interface_address))
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
        sock.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 3)
        sock.settimeout(ddata.timeout)
        sock.bind(server_address)

        probe = "M-SEARCH * HTTP/1.1\r\nHOST:239.255.255.250:1900\r\n" \
            "MAN:\"ssdp.discover\"\r\nMX:1\r\n"  \
            "ST:urn:udi-com:device:X_Insteon_Lighting_Device:1\r\n\r\n"

        sock.sendto(probe.encode('utf-8'), (multicast_group, multicast_port))

        start_time = time.clock()
        while len(ddata.upnp_urls) < ddata.count:
            current_time = time.clock()

            if (current_time - start_time) > ddata.timeout:
                break

            try:
                sock.settimeout(ddata.timeout - (current_time - start_time))
                data, address = sock.recvfrom(1024)
            except socket.timeout:
                raise UpnpLimitExpired("Timed Out")

            if sys.hexversion >= 0x3000000:
                data = str(data, encoding='utf8')

            if ddata.debug:
                print('received %s bytes from %s' % (len(data), address))
                print(data)
                print("ddata.upnp_urls = ", ddata.upnp_urls)

            # only ISY devices
            # if should I look for
            # SERVER:UCoS, UPnP/1.0, UDI/1.0
            if not "X_Insteon_Lighting_" in data:
                continue

            upnp_packet = data.splitlines()

            if "M-SEARCH " in upnp_packet[0]:
                continue

            # extract LOCATION
            for l in upnp_packet:
                a = l.split(':', 1)
                if len(a) == 2:
                    if str(a[0]).upper() == "LOCATION":
                        ddata.upnp_urls.append(str(a[1]).strip())
                        # uniq the list
                        ddata.upnp_urls = list(set(ddata.upnp_urls))

        #print "returning ", ddata.upnp_urls

    #isy_upnp(ddata)
    try:
        isy_ssdp()
    except:
        pass
    # except Exception:
        # print("Unexpected error:", sys.exc_info()[0])

    result = {}
#    result_tags = ["UDN", "URLBase", "SCPDURL",
#                "controlURL", "eventSubURL"]

    for s in ddata.upnp_urls:
        req = URL.Request(s)
        resp = URL.urlopen(req)

        pagedata = resp.read().decode('utf-8')
        resp.close()

        # does this even work ??
        # ET.register_namespace("isy", 'urn:schemas-upnp-org:device-1-0')
        #print "_namespace_map = {0}".format(ET._namespace_map)

        # this is a hack to deal with namespace:
        pa = re.sub(r" xmlns=\"urn:schemas-upnp-org:device-1-0\"", "", pagedata)
        # grok the XML from the Upnp discovered server
        xmlres = ET.fromstring(pa)

        isy_res = dict()

        xelm = xmlres.find("URLBase")
        if hasattr(xelm, 'text'):
            isy_res["URLBase"] = xelm.text

        xelm = xmlres.find("device/friendlyName")
        if hasattr(xelm, 'text'):
            isy_res["friendlyName"] = xelm.text

        xelm = xmlres.find("device/UDN")
        if hasattr(xelm, 'text'):
            isy_res["UDN"] = xelm.text

        for elm in xmlres.iter("service"):
            serv = xelm.find('serviceType')
            if hasattr(serv, 'text') and serv.text == "urn:udi-com:service:X_Insteon_Lighting_Service:1":

                serv = elm.find('SCPDURL')
                if hasattr(serv, 'text'):
                    isy_res["SCPDURL"] = serv.text

                serv = elm.find('controlURL')
                if hasattr(serv, 'text'):
                    isy_res["controlURL"] = serv.text

                serv = elm.find('eventSubURL')
                if hasattr(serv, 'text'):
                    isy_res["eventSubURL"] = serv.text

        result[isy_res["UDN"]] = isy_res

    return result

class IsySystem(object):
    def __init__(self, **kwargs):
        self.url = kwargs.get("url", None)
        self.user = kwargs.get("user", None)
        self.password = kwargs.get("password", None)

    def request(self, path):
        portal_url = urlparse(self.url)
        conn = httplib.HTTPSConnection(portal_url.netloc)
        headers = {'Authorization': 'Basic ' + b64encode(self.user + ':' + self.password)}
        conn.request('GET', portal_url.path + '/rest' + path, headers=headers)
        resp = conn.getresponse()
        result = xmltodict.parse(resp.read())
        conn.close()

        if resp.status == 200:
            return {'result': result}
        else:
            return {'status': resp.status, 'message': resp.message}

    def get_nodes(self):
        result = self.request('/nodes/devices')
        return {'result': result['result']['nodes']['node']}

    def execute_node_command(self, address, command, args):
        args = [urllib.quote(str(item)) for item in args]

        return self.request('/nodes/' + urllib.quote(address) + '/cmd/' + command + '/' + '/'.join(args))

    def get_node_property(self, address, prop):
        return self.request('/nodes/' + urllib.quote(address) + '/' + prop)

    def set_node_property(self, address, prop, value):
        if prop == 'ST':
            if value == 0:
                result = self.execute_node_command(address, 'DOF', [])
            else:
                result = self.execute_node_command(address, 'DON', [value])
        else:
            result = self.request('/nodes/' + urllib.quote(address) + '/set/' + prop + '/' + str(value))
        return result
