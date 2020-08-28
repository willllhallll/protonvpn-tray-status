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

### Authentication Note

The tray requires super user privileges to manage connections. Update the sudo-ers list for password-less action. Follow the steps here:

https://github.com/ProtonVPN/linux-gui#visudo

Alternatively, pass the `--polykit` flag and use PolyKit:

- `sudo apt install libpolkit-agent-1-0`
- `nohup python3 /opt/protonvpn-tray-status/tray.py --polykit &`

## Usage

The ProtonVPN icon will be red when disconnected and unprotected, amber when there the OpenVPN session is active but the internet is unreachable (e.g. Kill Switch, reconnect required, network loss) and green when active OpenVPN connection is detected.

If there is an authentication error, a padlock and key icon (🔐) will be displayed in the tray to prompt you to verify your credentials or ensure not too many connections have been made on your account.

If there is a network error when trying to connect or reconnect, a link (🔗) icon will be displayed in the tray, prompting you to check your internet connection, or verify your ISP has not blocked the ProtonVPN API.

### Note on Authentication Errors

If a connection is dropped uncleanly, i.e. via network loss, or if you try and make a number of repeated connection attempts, ProtonVPN sometimes fails to properly track the number of active connections on your account. This is reported to the ProtonVPN CLI as an authentication error. If this is the case for you when trying to connect, and you are certain you have used the correct OpenVPN Client Credentials in `protonvpn init`, then the only solution is to please wait a little while before trying to reconnect (or bug ProtonVPN to make things better). Make a brew, take a stroll, let time tick by for a minute or so.

### Connection Profiles

To add connection profiles, add the `--profiles` flag to the launch command, followed by either a country code or an exact server name. As an example, the following would give connection profiles for Swizerland, UK#13 and the United States:

`nohup python3 /opt/protonvpn-tray-status/tray.py --profiles CH UK#13 US &`

If you enter an invalid country code or server, or your ProtonVPN plan does not permit connection to that server, then the connection will simply fail.

### Status

- [x] Add basic connection functionality.
- [x] Add basic reporting and monitoring.
- [ ] Detect un-initialised ProtonVPN CLI.
- [ ] Add better input feedback for actions.
- [x] Add support for fastest of country.
- [x] Add support for random server.
- [x] Add support for specific server.
- [ ] Add server browser.
- [ ] P2P and Secure Core support.
- [ ] Update ProtonVPN CLI config from the tray.
