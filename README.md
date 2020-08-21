# protonvpn-tray-status

Uses the ProtonVPN CLI to pull and display basic connection status in the system tray. Checks every 10 seconds for an acitive connection.

To install on Linux, clone this repository into the `/opt/` directory. To launch on boot, add the following to your startup app list:

`nohup python3 /opt/protonvpn-status-tray/tray.py &`

### Note

Requires the ProtonVPN CLI package to be installed and configured:

`sudo pip3 install protonvpn-cli`

Requires gir1.2-appindicator3 to work:

`sudo apt-get install gir1.2-appindicator3`
