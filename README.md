# protonvpn-tray-status

Uses the ProtonVPN CLI to pull and display basic connection status in the system tray. Checks every 10 seconds for an acitive connection.

To install on Linux, clone this repository into the `/opt/` directory. To launch on boot, add the following to your startup app list:

`nohup python3 /opt/protonvpn-tray-status/tray.py &`

To display usage statistics in the tray, add the `-u` flag to the command:

`nohup python3 /opt/protonvpn-tray-status/tray.py -u &`

### Dependencies

Requires the ProtonVPN CLI package to be installed and configured:

`sudo pip3 install protonvpn-cli`

Requires gir1.2-appindicator3 and gir1.2-gtk-3.0 :

`sudo apt install gir1.2-appindicator3 gir1.2-gtk-3.0`

### Authentication Note

Requires super user privileges to perform a reconnect. Update the sudo-ers list for password-less action. Follow the steps here:

https://github.com/ProtonVPN/linux-gui#visudo

Alternatively, pass the `-p` flag to use PolyKit:

- `sudo apt install libpolkit-agent-1-0`
- `nohup python3 /opt/protonvpn-tray-status/tray.py -p &`
