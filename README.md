# pia-wg
A WireGuard configuration utility for Private Internet Access

This is a Python utility that generates WireGuard configuration files for the Private Internet Access VPN service. This allows you to take advantage of the WireGuard protocol without relying on PIA's proprietary client.

This was created by reverse engineering the [manual-connections](https://github.com/pia-foss/manual-connections) script released by PIA. At this stage, the tool is a quick and dirty attempt to get things working. It could break at any moment if PIA makes changes to their API.

pia-wg *should* run on both Windows and Linux.

## Windows
* Install the latest version of [Python 3](https://www.python.org/downloads/windows/)
  * Select "Add Python to environment variables"
* Install [WireGuard](https://www.wireguard.com/install/)

Open a command prompt and navigate to the directory where you placed the pia-wg utility. The following commands will create a virtual Python environment, install the dependencies, and run the tool.

```
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
generate-config.py
```

Follow the prompts. When finished, you can exit the virtual environment with the `deactivate` command.

The script should generate a `.conf` file that can be imported into the WireGuard utility.

## Linux
todo
