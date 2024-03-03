# pia-wg
A WireGuard configuration utility for Private Internet Access

This is a Python utility that generates WireGuard configuration files for the Private Internet Access VPN service. This allows you to take advantage of the WireGuard protocol without relying on PIA's proprietary client.

This was created by reverse engineering the [manual-connections](https://github.com/pia-foss/manual-connections) script released by PIA. At this stage, the tool is a quick and dirty attempt to get things working. It could break at any moment if PIA makes changes to their API.

pia-wg runs on both Windows and Linux.

## Windows
* Install the latest version of [Python 3](https://www.python.org/downloads/windows/)
  * Select "Add Python to environment variables"
* Install [WireGuard](https://www.wireguard.com/install/)

Open a command prompt and navigate to the directory where you placed the pia-wg utility. The following commands will create a virtual Python environment, install the dependencies, and run the tool.

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
python generate-config.py
```

Follow the prompts. When finished, you can exit the virtual environment with the `deactivate` command.

The script should generate a `.conf` file that can be imported into the WireGuard utility.

## Linux (Debian/Ubuntu)
Install dependencies, clone pia-wg project, and create a virual Python environment:
```
sudo apt install git python3-venv wireguard openresolv
git clone https://github.com/hsand/pia-wg.git
cd pia-wg
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

Run the tool, and follow the prompts
```
python generate-config.py
```

Copy the `.conf` file to `/etc/wireguard/`, and start the interface
```
sudo cp PIA-Iceland-1605054556.conf /etc/wireguard/wg0.conf
sudo wg-quick up wg0
```

You can shut down the interface with `sudo wg-quick down wg0`

## RouterOS

If you want to send the Wireguard config to a Mikrotik router, use configure-ros.py:
```
$ ./configure-ros.py -i wg-pia-il -f PIA-Iceland-1605054556.conf
- loading config from ./config.yaml
- added new /interface/wireguard
- added new /ip/address
- added new /interface/wireguard/peers
- added new /ip/dns/static
```
You'll then have an interface named wg-pia-il, and it's up to you to configure what traffic routes through it.  A static dns entry for the PIA gateway IP is added as 'gw-wg-pia-il' to help you identify it.

If an interface of the supplied name already exists, its settings will be updated.  To remove interfaces, use the `-d` option:
```
$ ./configure-ros.py -i wg-pia-il -d
- loading config from config.yaml
- removed entry in /interface/wireguard/peers
- removed entry in /ip/address
- removed entry in /interface/wireguard
- removed entry in /ip/dns/static
```

## Check everything is working
Visit https://dnsleaktest.com/ to see your new IP and check for DNS leaks.

## Options

The following options are supported:

```
$ ./generate-config.py -h
usage: generate-config.py [-h] [-r] [--sort-latency] [-f CONFIG]

Generate PIA wireguard config

optional arguments:
  -h, --help            show this help message and exit
  -r , --region         Allowed values are AU Adelaide, AU Brisbane, AU
                        Melbourne, AU Perth, AU Sydney, Albania, Algeria,
                        Andorra, Argentina, Armenia, Australia Streaming
                        Optimized, Austria, Bahamas, Bangladesh, Belgium,
                        Bolivia, Bosnia and Herzegovina, Brazil, Bulgaria, CA
                        Montreal, CA Ontario, CA Ontario Streaming Optimized,
                        CA Toronto, CA Vancouver, Cambodia, Chile, China,
                        Colombia, Costa Rica, Croatia, Cyprus, Czech Republic,
                        DE Berlin, DE Frankfurt, DE Germany Streaming
                        Optimized, DK Copenhagen, DK Streaming Optimized, ES
                        Madrid, ES Valencia, Ecuador, Egypt, Estonia, FI
                        Helsinki, FI Streaming Optimized, France, Georgia,
                        Greece, Greenland, Guatemala, Hong Kong, Hungary, IT
                        Milano, IT Streaming Optimized, Iceland, India,
                        Indonesia, Ireland, Isle of Man, Israel, JP Streaming
                        Optimized, JP Tokyo, Kazakhstan, Latvia,
                        Liechtenstein, Lithuania, Luxembourg, Macao, Malaysia,
                        Malta, Mexico, Moldova, Monaco, Mongolia, Montenegro,
                        Morocco, NL Netherlands Streaming Optimized, Nepal,
                        Netherlands, New Zealand, Nigeria, North Macedonia,
                        Norway, Panama, Peru, Philippines, Poland, Portugal,
                        Qatar, Romania, SE Stockholm, SE Streaming Optimized,
                        Saudi Arabia, Serbia, Singapore, Slovakia, Slovenia,
                        South Africa, South Korea, Sri Lanka, Switzerland,
                        Taiwan, Turkey, UK London, UK Manchester, UK
                        Southampton, UK Streaming Optimized, US Alabama, US
                        Alaska, US Arkansas, US Atlanta, US Baltimore, US
                        California, US Chicago, US Connecticut, US Denver, US
                        East, US East Streaming Optimized, US Florida, US
                        Honolulu, US Houston, US Idaho, US Indiana, US Iowa,
                        US Kansas, US Kentucky, US Las Vegas, US Louisiana, US
                        Maine, US Massachusetts, US Michigan, US Minnesota, US
                        Mississippi, US Missouri, US Montana, US Nebraska, US
                        New Hampshire, US New Mexico, US New York, US North
                        Carolina, US North Dakota, US Ohio, US Oklahoma, US
                        Oregon, US Pennsylvania, US Rhode Island, US Salt Lake
                        City, US Seattle, US Silicon Valley, US South
                        Carolina, US South Dakota, US Tennessee, US Texas, US
                        Vermont, US Virginia, US Washington DC, US West, US
                        West Streaming Optimized, US West Virginia, US
                        Wilmington, US Wisconsin, US Wyoming, Ukraine, United
                        Arab Emirates, Uruguay, Venezuela, Vietnam
  --sort-latency        Display lowest latency regions first (requires root)
  -f CONFIG, --config CONFIG
                        Name of the generated config file

$ ./configure-ros.py -h
usage: configure-ros.py [-h] [-d] -i INTERFACE -f CONFIG

Configure RouterOS with wireguard config

optional arguments:
  -h, --help            show this help message and exit
  -d, --delete
  -i INTERFACE, --interface INTERFACE
  -f CONFIG, --config CONFIG
```

## Config file

You can store your username, password, and region in a `config.yaml` file in the same directory as the script:
```
pia:
    username: pXXXXXXX
    password: 1234567890abcde
    region: "AU Melbourne"
router:
    ip: 192.168.0.1
    username: admin
    password: password
```
