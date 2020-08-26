# protonvpn-tray-status

> Unofficial and In-Development.

Uses the ProtonVPN CLI to pull and display basic connection status in the system tray. Whilst most functionality is present, it is better suited as a supplement to the CLI for ease of monitoring and control. It is not yet a fully fledged client.

## Dependencies

Requires the ProtonVPN CLI package to be installed and configured:

`sudo pip3 install protonvpn-cli`

`sudo protonvpn init`

Requires gir1.2-appindicator3 and gir1.2-gtk-3.0 :

`sudo apt install gir1.2-appindicator3 gir1.2-gtk-3.0`

## Install and Start

To install on Linux, clone this repository into the `/opt/` directory. To launch on boot, add the following to your startup app list:

`nohup python3 /opt/protonvpn-tray-status/tray.py &`

To display usage statistics in the tray, add the `-u` flag to the command:

`nohup python3 /opt/protonvpn-tray-status/tray.py -u &`

### Authentication Note

The tray requires super user privileges to manage connections. Update the sudo-ers list for password-less action. Follow the steps here:

https://github.com/ProtonVPN/linux-gui#visudo

Alternatively, pass the `-p` flag and use PolyKit:

- `sudo apt install libpolkit-agent-1-0`
- `nohup python3 /opt/protonvpn-tray-status/tray.py -p &`

## Usage

The ProtonVPN icon will be red when disconnected, and green when and active OpenVPN connection is detected. Note, in the event of a network error, the icon will remain green as the OpenVPN session is still technically established.

If there is an authentication error, a padlock and key icon (🔐) will be displayed in the tray to prompt you to verify your credentials or ensure not too many connections have been made on your account.

If there is a network error when trying to connect, reconnect or disconnect, a link (🔗) icon will be displayed in the tray, prompting you to check your internet connection, or verify your ISP has not blocked the ProtonVPN API.

### Note on Authentication Errors

If a connection is dropped uncleanly, i.e. via network loss, or if you try and make a number of repeated connection attempts, ProtonVPN sometimes fails to properly track the number of active connections on your account. This is reported to the ProtonVPN CLI as an authentication error. If this is the case for you when trying to connect, and you are certain you have used the correct OpenVPN Client Credentials in `protonvpn init`, then please wait a little while before trying to reconnect (or bug ProtonVPN to make things better).

### Status

- [x] Add basic connection functionality.
- [x] Add basic reporting and monitoring.
- [ ] Detect un-initialised ProtonVPN CLI.
- [ ] Add support for fastest of country.
- [ ] Add support for random server.
- [ ] Add support for specific server.
