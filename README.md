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
python3 generate-config.py
```

Copy the `.conf` file to `/etc/wireguard/`, and start the interface
```
sudo cp PIA-Iceland-1605054556.conf /etc/wireguard/wg0.conf
sudo wg-quick up wg0
```

You can shut down the interface with `sudo wg-quick down wg0`

## Check everything is working
Visit https://dnsleaktest.com/ to see your new IP and check for DNS leaks.

## Options

The following options are supported:

```
$ python generate-config.py -h
usage: generate-config.py [-h] [-r <region>] [--sort-latency]

Generate PIA wireguard config

optional arguments:
  -h, --help      show this help message and exit
  -r , --region   Allowed values are AU Melbourne, AU Perth, AU Sydney,
                  Albania, Algeria, Andorra, Argentina, Armenia, Austria,
                  Bahamas, Bangladesh, Belgium, Bosnia and Herzegovina,
                  Brazil, CA Montreal, CA Ontario, CA Toronto, CA Vancouver,
                  Cambodia, Chile, China, Colombia, Costa Rica, Croatia,
                  Cyprus, Czech Republic, DE Berlin, DE Frankfurt, DK
                  Copenhagen, DK Streaming Optimized, ES Madrid, ES Valencia,
                  Egypt, Estonia, FI Helsinki, FI Streaming Optimized, France,
                  Georgia, Greece, Greenland, Hong Kong, Hungary, IT Milano,
                  IT Streaming Optimized, Iceland, India, Indonesia, Ireland,
                  Isle of Man, Israel, JP Streaming Optimized, JP Tokyo,
                  Kazakhstan, Latvia, Liechtenstein, Lithuania, Luxembourg,
                  Macao, Malaysia, Malta, Mexico, Moldova, Monaco, Mongolia,
                  Montenegro, Morocco, Netherlands, New Zealand, Nigeria,
                  Norway, Panama, Philippines, Poland, Portugal, Qatar,
                  Romania, SE Stockholm, SE Streaming Optimized, Saudi Arabia,
                  Serbia, Singapore, Slovakia, Slovenia, South Africa, Sri
                  Lanka, Switzerland, Taiwan, Turkey, UK London, UK
                  Manchester, UK Southampton, UK Streaming Optimized, US
                  Atlanta, US Baltimore, US California, US Chicago, US Denver,
                  US East, US East Streaming Optimized, US Florida, US
                  Honolulu, US Houston, US Las Vegas, US New York, US Salt
                  Lake City, US Seattle, US Silicon Valley, US Texas, US
                  Washington DC, US West, US West Streaming Optimized, US
                  Wilmington, Ukraine, United Arab Emirates, Venezuela,
                  Vietnam
  --sort-latency  Display lowest latency regions first (requires root)
```

## Config file

You can store your username, password, and region in a `config.yaml` file in the same directory as the script:
```
pia:
    username: pXXXXXXX
    password: 1234567890abcde
    region: "AU Melbourne"
```
