#!/usr/bin/env python

from piawg import piawg
from pick import pick
from getpass import getpass
from datetime import datetime
from icmplib import multiping
from pprint import pprint
from wgconfig import WGConfig
import argparse, collections, os, sys, yaml

# comment to debug
sys.tracebacklimit = 0

def main():
    pia = piawg()
    regions = sorted([x for x in pia.server_list if 'wg' in pia.server_list[x]['servers']])

    # Parse arguments
    parser = argparse.ArgumentParser(description='Generate PIA wireguard config')
    parser.add_argument('-r', '--region', dest='region', choices=["auto"]+regions, help='Allowed values are '+', '.join(regions), metavar='')
    parser.add_argument('--sort-latency', action='store_true', help='Display lowest latency regions first (requires root)')
    parser.add_argument('-f', '--config', help='Name of the generated config file')
    args = parser.parse_args()

    # Load config
    config = None
    file = os.path.join(os.path.dirname(__file__), 'config.yaml')
    file = os.path.normpath(file)
    if os.path.exists(file):
        print("Loading config from {}".format(file))
        with open(file, 'r') as f:
            config = yaml.safe_load(f)

    # Select region
    try:
        region = config['pia']['region']
    except:
        region = args.region
    if region in (None, "auto"):
        title = 'Please choose a region: '
        # sort by latency
        if args.sort_latency or region == "auto":
            print("Measuring latency to regions...")
            wg_latencies = ping_latencies([pia.server_list[x]['servers']['wg'][0]['ip'] for x in regions])
            region_latencies = {x: wg_latencies[pia.server_list[x]['servers']['wg'][0]['ip']] for x in regions};
            closest_regions = sorted(region_latencies.keys(), key=lambda k: region_latencies[k])
            if region == "auto":
                region = closest_regions[0]
            else:
                region, index = pick(closest_regions, title, options_map_func=lambda x: "{} ({} ms)".format(x,region_latencies[x]))
        else:
            region, index = pick(regions, title)
    print("Selected '{}'".format(region))
    pia.set_region(region)

    # Generate public and private key pair
    pia.generate_keys()

    # Get credentials
    try:
        username = config['pia']['username']
        password = config['pia']['password']
    except:
        username, password = None, None

    # Get token
    while True:
        if None in (username, password):
            username = input("\nEnter PIA username: ")
            password = getpass()
        if pia.get_token(username, password):
            print("Login successful!")
            break
        else:
            print("Error logging in, please try again...")
            username = None

    # Add key
    status, response = pia.addkey()
    if status:
        print("Added key to server!")
    else:
        print("Error adding key to server")
        print(response)

    # Build config
    if args.config:
        config_file = args.config
    else:
        timestamp = int(datetime.now().timestamp())
        location = pia.region.replace(' ', '-')
        config_file = 'PIA-{}-{}.conf'.format(location, timestamp)
    print("Saving configuration file {}".format(config_file))
    if config_file[0] != '/':
        config_file = os.path.join(os.path.dirname(__file__), config_file)
        config_file = os.path.normpath(config_file)
    wgc = WGConfig(config_file)
    wgc.add_attr(None, 'Address', pia.connection['peer_ip'])
    wgc.add_attr(None, 'PrivateKey', pia.privatekey)
    for dns_server in pia.connection['dns_servers'][0:2]:
        wgc.add_attr(None, 'DNS', dns_server)
    peer = pia.connection['server_key']
    wgc.add_peer(peer, '# ' + pia.region)
    wgc.add_attr(peer, 'Endpoint', pia.connection['server_ip'] + ':1337')
    wgc.add_attr(peer, 'AllowedIPs', '0.0.0.0/0')
    wgc.add_attr(peer, 'PersistentKeepalive', '25')
    wgc.write_file()

def ping_latencies(hosts):
    if os.getuid() != 0:
        raise Exception("measuring latencies requires root")
    # trying to ping everything at once seems to result in inaccurate timing
    # the default concurrent_tasks=50 seems to work well
    results = multiping(addresses=hosts, count=3, timeout=0.5)
    # workaround: lossy pings have their rtt set to 0.0 by icmplib
    return { x.address:(500, x.avg_rtt)[x.avg_rtt > 0] for x in results }

if __name__ == '__main__':
    main()
