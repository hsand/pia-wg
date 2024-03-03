#!/usr/bin/env python

from pick import pick
from getpass import getpass
from datetime import datetime
from icmplib import multiping
from pprint import pprint
from routeros import login
import argparse, collections, os, re, sys, yaml, wgconfig

# comment to debug
sys.tracebacklimit = 0

def add_or_update(ros, section, key, value, **params):
    existing = ros.query(section + "/print").equal(**{key: value})
    ret = []
    if existing:
        ret = ros(section + "/set", **{".id": existing[0]['.id']}, **params)
        if len(ret)==0 or ".id" in ret[0]:
            print("- updated existing " + section)
    else:
        ret = ros(section + "/add", **{key: value}, **params)
        if len(ret)==0 or "ret" in ret[0]:
            print("- added new " + section)
    if len(ret) and not (".id" in ret[0] or "ret" in ret[0]):
        raise Exception("ROS {} update failed".format(section))

def remove(ros, section, key, value):
    existing = ros.query(section + "/print").equal(**{key: value})
    if existing:
        ret = ros(section + "/remove", **{".id": existing[0]['.id']})
        if len(ret)==0 or ".id" in ret[0]:
            print("- removed entry in " + section)
        else:
            raise Exception("ROS {} remove failed".format(section))
    else:
        print("- entry not found in " + section)

def add_gw_dns(ros, ifname):
    existing = ros.query("/ip/address/print").equal(interface=ifname)
    if existing:
        network = existing[0]["network"]
        gw = re.sub("\.0$", ".1", network)
        add_or_update(ros, "/ip/dns/static", "name", "gw-" + ifname,
                      **{"address": gw})
    else:
        print("- " + ifname + " address not found")

def delete_interface(ros, ifname):
    remove(ros, "/interface/wireguard/peers", "interface", ifname)
    remove(ros, "/ip/address", "interface", ifname)
    remove(ros, "/interface/wireguard", "name", ifname)
    remove(ros, "/ip/dns/static", "name", "gw-" + ifname)
    
def configure_routeros(ros, ifname, wgconf):
    interface = wgconf.get_interface()
    peers     = wgconf.get_peers(keys_only=False)

    # make sure we have everything we need
    for k in ['Address', 'PrivateKey']:
        if interface.get(k) == None:
            raise Exception("Missing interface parameter: '{}'".format(k))

    assert len(peers) == 1, "1 peer expected"

    for p in peers:
        peer = peers[p]

    for k in ['Endpoint', 'PublicKey']:
        if peer.get(k) == None:
            raise Exception("Missing peer parameter: '{}'".format(k))

    # add/update interface
    add_or_update(ros, "/interface/wireguard", "name", ifname,
                  **{"private-key": interface["PrivateKey"]})

    # add/update interface address
    add_or_update(ros, "/ip/address", "interface", ifname,
                  address="{}/17".format(interface["Address"]))

    # add/update peer
    ip, port = peer['Endpoint'].split(':')
    add_or_update(ros, "/interface/wireguard/peers", "interface", ifname,
                  **{
                      "endpoint-address": ip,
                      "endpoint-port": port,
                      "public-key": peer['PublicKey'],
                      "allowed-address": "0.0.0.0/0",
                      "persistent-keepalive": "25s",
                  })

    # add a static dns entry for the gateway ip
    add_gw_dns(ros, ifname)

def main():
    # Parse arguments
    parser = argparse.ArgumentParser(
        description='Configure RouterOS with wireguard config'
    )
    parser.add_argument('-d', '--delete', action='store_true')
    parser.add_argument('-i', '--interface', required=True)
    parser.add_argument('-f', '--config',
                        required=not ('-d' in sys.argv or
                                      '--delete' in sys.argv))
    args = parser.parse_args()

    # Load config
    config = None
    file = os.path.join(os.path.dirname(__file__), 'config.yaml')
    file = os.path.normpath(file)
    if os.path.exists(file):
        print("- loading config from {}".format(file))
        with open(file, 'r') as f:
            config = yaml.safe_load(f)

    # Get credentials
    try:
        ip       = config['router']['ip']
        username = config['router']['username']
        password = config['router']['password']
    except:
        ip, username, password = None, None, None

    # Login
    while True:
        if None in (ip, username, password):
            ip       = input("\nEnter router IP: ")
            username = input("\nEnter username: ")
            password = getpass()
        routeros = login(username, password, ip)
        try:
            routeros('/interface/print')
            break
        except:
            print("Error logging in, please try again...")
            username = None

    if args.delete:
        # Delete the interface
        delete_interface(routeros, args.interface)
        
    else:
        # Read wg config
        wgconf = wgconfig.WGConfig(
            os.path.join(os.path.dirname(__file__), args.config)
        )
        wgconf.read_file()

        # Make change to router
        configure_routeros(routeros, args.interface, wgconf)

    routeros.close()

if __name__ == '__main__':
    main()
