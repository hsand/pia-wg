import requests
import json
from requests_toolbelt.adapters import host_header_ssl
import urllib3
import subprocess
import urllib.parse

# PIA uses the CN attribute for certificates they issue themselves.
# This will be deprecated by urllib3 at some point in the future, and generates a warning (that we ignore).
urllib3.disable_warnings(urllib3.exceptions.SubjectAltNameWarning)


class piawg:
    def __init__(self):
        self.server_list = {}
        self.get_server_list()
        self.region = None
        self.token = None
        self.publickey = None
        self.privatekey = None
        self.connection = None

    def get_server_list(self):
        r = requests.get('https://serverlist.piaservers.net/vpninfo/servers/v4')
        # Only process first line of response, there's some base64 data at the end we're ignoring
        data = json.loads(r.text.splitlines()[0])
        for server in data['regions']:
            self.server_list[server['name']] = server

    def set_region(self, region_name):
        self.region = region_name

    def get_token(self, username, password):
        # Get common name and IP address for metadata endpoint in region
        meta_cn = self.server_list[self.region]['servers']['meta'][0]['cn']
        meta_ip = self.server_list[self.region]['servers']['meta'][0]['ip']

        # Some tricks to verify PIA certificate, even though we're sending requests to an IP and not a proper domain
        # https://toolbelt.readthedocs.io/en/latest/adapters.html#requests_toolbelt.adapters.host_header_ssl.HostHeaderSSLAdapter
        s = requests.Session()
        s.mount('https://', host_header_ssl.HostHeaderSSLAdapter())
        s.verify = 'ca.rsa.4096.crt'

        r = s.get("https://{}/authv3/generateToken".format(meta_ip), headers={"Host": meta_cn},
                  auth=(username, password))
        data = r.json()
        if r.status_code == 200 and data['status'] == 'OK':
            self.token = data['token']
            return True
        else:
            return False

    def generate_keys(self):
        self.privatekey = subprocess.run(['wg', 'genkey'], stdout=subprocess.PIPE, encoding="utf-8").stdout.strip()
        self.publickey = subprocess.run(['wg', 'pubkey'], input=self.privatekey, stdout=subprocess.PIPE,
                                        encoding="utf-8").stdout.strip()

    def addkey(self):
        # Get common name and IP address for wireguard endpoint in region
        cn = self.server_list[self.region]['servers']['wg'][0]['cn']
        ip = self.server_list[self.region]['servers']['wg'][0]['ip']

        s = requests.Session()
        s.mount('https://', host_header_ssl.HostHeaderSSLAdapter())
        s.verify = 'ca.rsa.4096.crt'

        r = s.get("https://{}:1337/addKey?pt={}&pubkey={}".format(ip, urllib.parse.quote(self.token),
                                                                  urllib.parse.quote(self.publickey)), headers={"Host": cn})
        if r.status_code == 200 and r.json()['status'] == 'OK':
            self.connection = r.json()
            return True, r.content
        else:
            return False, r.content
