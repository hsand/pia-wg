from piawg import piawg
from pick import pick
import os
from getpass import getpass
from datetime import datetime

pia = piawg()

# Generate public and private key pair
while True:
    if os.path.exists('privatekey') or os.path.exists('publickey'):
        value = input("Key files already exist. If you want to overwrite them type 'YES': ")
        if value == 'YES':
            pia.generate_keys()
            break
    else:
        pia.generate_keys()
        break

# Select region
title = 'Please choose a region: '
options = sorted(list(pia.server_list.keys()))
option, index = pick(options, title)
pia.set_region(option)

# Get token
while True:
    username = input("\nEnter PIA username: ")
    password = getpass()
    if pia.get_token(username, password):
        print("Login successful!")
        break
    else:
        print("Error logging in, please try again...")

# Add key
status, response = pia.addkey()
if status:
    print("Added key to server!")
else:
    print("Error adding key to server")
    print(response)

# Build config
timestamp = int(datetime.now().timestamp())
location = pia.region.replace(' ', '-')
config_file = 'PIA-{}-{}.conf'.format(location, timestamp)
print("Saving configuration file {}".format(config_file))
with open(config_file, 'w') as file:
    file.write('[Interface]\n')
    file.write('Address = {}\n'.format(pia.connection['peer_ip']))
    file.write('PrivateKey = {}\n'.format(pia.privatekey))
    file.write('DNS = {},{}\n\n'.format(pia.connection['dns_servers'][0], pia.connection['dns_servers'][1]))
    file.write('[Peer]\n')
    file.write('PublicKey = {}\n'.format(pia.connection['server_key']))
    file.write('Endpoint = {}:1337\n'.format(pia.connection['server_ip']))
    file.write('AllowedIPs = 0.0.0.0/0\n')
    file.write('PersistentKeepalive = 25\n')
