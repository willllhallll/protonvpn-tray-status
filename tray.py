#!/usr/bin/python
import os
import sys
import time
import datetime
import requests
import subprocess

import gi
gi.require_version('Gtk', '3.0')
gi.require_version('AppIndicator3', '0.1')
from gi.repository import Gtk as gtk, AppIndicator3 as appindicator, GObject as gobject
from threading import Event, Thread

from protonvpn_cli.utils import (
    is_connected,
    get_config_value,
    get_servers,
    get_server_value,
    get_transferred_data,
    get_country_name
)

'''
Set the local paths for the tray icons.
'''
current_path = os.path.dirname(os.path.realpath(__file__))
GREEN_ICON = os.path.join(current_path, 'icons', 'green.png')
RED_ICON = os.path.join(current_path, 'icons', 'red.png')
AMBER_ICON = os.path.join(current_path, 'icons', 'amber.png')

class Indicator():
    def __init__(self):

        self.gtk = gtk
        self.gobject = gobject

        self.trayindicator = appindicator.Indicator.new("protonvpn-tray", RED_ICON, appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.trayindicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.trayindicator.set_menu(self.set_menu())
        self.trayindicator.set_label("", "")

        self.connected = False
        self.current_server = "-"
        self.auth_error = False
        self.network_error = False

        self.main_loop = self.gobject.timeout_add_seconds(1, self.main)
        self.network_loop = self.gobject.timeout_add_seconds(8, self.try_network)
        
        self.main()
        self.try_network()

        self.gtk.main()

    '''
    Call all the reporters. 
    `True` is returned to allow for scheduling of the next call.
    '''
    def main(self):

        self.report_is_connected()
        self.report_time_connected()
        self.report_location_connected()
        self.report_kill_switch()
        self.report_dns_leak_protection()
        self.report_data_transfer()
        self.report_tray_info()

        return True

    '''
    Define the menu structure. There are three sections:
    - Connection Info
    - Config info
    - Exit
    '''
    def set_menu(self):

        self.menu = self.gtk.Menu()

        self.time_connected = self.gtk.MenuItem(label='')
        self.menu.append(self.time_connected)

        self.location_connected = self.gtk.MenuItem(label='')
        self.menu.append(self.location_connected)

        self.data_transfer = self.gtk.MenuItem(label='')
        self.menu.append(self.data_transfer)
        
        self.separator_1 = self.gtk.SeparatorMenuItem()
        self.menu.append(self.separator_1)
        self.separator_1.show()

        self.reconnect = self.gtk.MenuItem(label='')
        self.reconnect.connect('activate', self.try_reconnect)
        self.menu.append(self.reconnect)

        self.disconnect = self.gtk.MenuItem(label='Disconnect')
        self.disconnect.connect('activate', self.try_disconnect)
        self.menu.append(self.disconnect)

        self.separator_2 = self.gtk.SeparatorMenuItem()
        self.menu.append(self.separator_2)
        self.separator_2.show()

        self.fast_connect = self.gtk.MenuItem(label='➜ Fastest')
        self.fast_connect.connect('activate', self.try_connect, ["--fastest"])
        self.menu.append(self.fast_connect)

        self.random_connect = self.gtk.MenuItem(label='➜ Random')
        self.random_connect.connect('activate', self.try_connect, ["--random"])
        self.menu.append(self.random_connect)

        self.build_menu_profiles()  

        self.separator_3 = self.gtk.SeparatorMenuItem()
        self.menu.append(self.separator_3)
        self.separator_3.show()

        self.kill_switch = self.gtk.MenuItem(label='')
        self.menu.append(self.kill_switch)

        self.dns_leak_protection = self.gtk.MenuItem(label='')
        self.menu.append(self.dns_leak_protection)

        self.separator_4= self.gtk.SeparatorMenuItem()
        self.menu.append(self.separator_4)
        self.separator_4.show()

        self.exittray = self.gtk.MenuItem('Exit')
        self.exittray.connect('activate', self.stop)
        self.menu.append(self.exittray)

        self.menu.show_all()
        return self.menu

    '''
    If the user has specified profiles, construct the menu entries accordingly.
    '''
    def build_menu_profiles(self):

        if "--profiles" in sys.argv:
            self.separator_profile = self.gtk.SeparatorMenuItem()
            self.menu.append(self.separator_profile)
            self.separator_profile.show()

            profile_flag_index = sys.argv.index("--profiles")
            next_flag_index = len(sys.argv)

            for i in range(profile_flag_index + 1, len(sys.argv)):
                if "--" in sys.argv[i]:
                    next_flag_index = i

            for profile in sys.argv[profile_flag_index + 1:next_flag_index]:
                if "#" in profile:
                    direct_server = self.gtk.MenuItem(label="➜ "+ profile)
                    direct_server.connect('activate', self.try_connect, [profile])
                    self.menu.append(direct_server)
                else:
                    country_server = self.gtk.MenuItem(label="➜ " + get_country_name(profile))
                    country_server .connect('activate', self.try_connect, ["--cc", profile])
                    self.menu.append(country_server)

    '''
    Verifies if currently connected to a server.
    Sets the colour of the tray indicator icon to reflect the connetion status. 
    '''
    def report_is_connected(self):

        self.reconnect.get_child().set_text("Reconnect to {}".format(self.current_server))

        if is_connected():

            if self.network_error:
                self.trayindicator.set_icon(AMBER_ICON)
            else:
                self.trayindicator.set_icon(GREEN_ICON)

            if not self.connected:
                self.connected = True
                self.auth_error = False
                self.network_error = False
        else:

            if self.connected:
                self.connected = False

            self.trayindicator.set_icon(RED_ICON)      

    '''
    Reports the current time elapsed since the connection was established.
    Sources the epoch time from the ProtonVPI-CLI config via a utility function.
    '''
    def report_time_connected(self):

        connection_time = "-"

        if self.connected and not self.auth_error and not self.network_error:
            try:
                connected_time = get_config_value("metadata", "connected_time")
                connection_time = time.time() - int(connected_time)
                connection_time = str(datetime.timedelta(seconds=(time.time() - int(connected_time)))).split(".")[0]
            except (BaseException):
                print("Error Reporting Time Connected")

        self.time_connected.get_child().set_text("{}".format(connection_time))

    '''
    Reports the location of the currently connected server.
    Sources the connected server from the ProtonVPN-CLI config, and the server info from the 
    local ProtonVPN-CLI server JSON file.
    Sets the `current_server` property of the indicator instance.
    '''
    def report_location_connected(self):

        location_string = "-"
        connected_server = "-"

        try:
            servers = get_servers()
            connected_server = get_config_value("metadata", "connected_server")

            if self.connected and not self.auth_error and not self.network_error:
                country_code = get_server_value(connected_server, "EntryCountry", servers)
                country_string = get_country_name(country_code)
                city = get_server_value(connected_server, "City", servers)
                location_string = "{city}, {country}".format(country=country_string, city=city)

        except (BaseException):
            print("Error Reporting Connected Server")

        self.current_server = connected_server
        
        self.location_connected.get_child().set_text(location_string)

    '''
    Reports the Kill Switch status, sourced from the ProtonVPN-CLI config.
    '''
    def report_kill_switch(self):

        kill_switch_status = "-"

        try:
            kill_switch_flag = get_config_value("USER", "killswitch")

            if kill_switch_flag == "1":
                kill_switch_status = "On (WAN & LAN)"
            elif kill_switch_flag == "2":
                kill_switch_status = "On (WAN)"
            else:
                kill_switch_status = "Off"

        except (BaseException):
            print("Error Reporting Kill Switch Status")

        self.kill_switch.get_child().set_text("Kill Switch: {}".format(kill_switch_status))

    '''
    Reports the DNS Leak Protection status, sourced from the ProtonVPN-CLI config.
    '''
    def report_dns_leak_protection(self):

        dns_leak_protection_status = "-"

        try:
            dns_leak_protection_flag = get_config_value("USER", "dns_leak_protection")
            dns_leak_protection_status = "On" if dns_leak_protection_flag == "1" else "Off"
        except (BaseException):
            print("Error Reporting DNS Leak Protection Status")

        self.dns_leak_protection.get_child().set_text("DNS Leak Protection: {}".format(dns_leak_protection_status))

    '''
    Reports the amount of data transferred by the client.
    '''
    def report_data_transfer(self):
        
        usage_string = "-"

        if self.connected and not self.auth_error and not self.network_error:
            sent_amount, received_amount = get_transferred_data()
            usage_string = "{0} 🠕🠗 {1}".format(sent_amount, received_amount)

        self.data_transfer.get_child().set_text(usage_string)
    
    '''
    Update the tray label with the currently connected server.
    If there is an authentication or network error, report this instead.
    '''
    def report_tray_info(self):

        info_string = ""

        if self.connected and not self.auth_error and not self.network_error:
            info_string = self.current_server

        info_string = "🔐" if self.auth_error else info_string
        info_string = "🔗" if self.network_error else info_string
  
        self.trayindicator.set_label(info_string, "")

    '''
    Attempts to connect to a VPN server, specifying flags for the connection command. 
    '''
    def try_connect(self, _, flags):

        command_array = [self.sudo_type, "protonvpn", "connect"] + flags

        process = subprocess.Popen(command_array, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        try:
            response = process.communicate(timeout=30)
            outs = response[0].decode().lower()

            if "authentication failed" in outs:
                self.auth_error = True
                print("Error Whilst Attempting Quick Connect: Authentication.")

        except subprocess.TimeoutExpired:
            print("Error Whilst Attempting Quick Connect: Timeout.")

    '''
    Attempts to reconnect to the last VPN server
    '''
    def try_reconnect(self, _):

        process = subprocess.Popen([self.sudo_type, "protonvpn", "reconnect"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        try:
            response = process.communicate(timeout=30)
            outs = response[0].decode().lower()

            if "authentication failed" in outs:
                self.auth_error = True
                print("Error Whilst Attempting Reconnection: Authentication.")

        except subprocess.TimeoutExpired:
            print("Error Whilst Attempting Reconnection: Timeout.")

    '''
    Attempts to disconnect from the VPN server
    '''
    def try_disconnect(self, _):

        process = subprocess.Popen([self.sudo_type, "protonvpn", "disconnect"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        try:
            process.communicate(timeout=30)
        except subprocess.TimeoutExpired:
            print("Error Whist Attempting Disconnect: Timeout.")

    '''
    Attempts to ping the ProtonVPN API Endpoint. 
    '''
    def try_network(self):
        
        process = subprocess.Popen(["ping", "-c", "1", "api.protonvpn.ch"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)

        try:
            process.communicate(timeout=7)
            if process.returncode == 0:
                self.network_error = False
            else:
                self.network_error = True
                print("Error: No network")
            
        except subprocess.TimeoutExpired:
            self.network_error = True
            print("Error: No network")
        
        return True

    '''
    Returns the user specified sudo type.
    '''
    @property
    def sudo_type(self):

        if "--polykit" in sys.argv:
            return "pkexec"

        return "sudo"

    '''
    Quits the tray.
    '''
    def stop(self, _):
        self.gobject.source_remove(self.main_loop)
        self.gtk.main_quit()

Indicator()