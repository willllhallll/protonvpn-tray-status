#!/usr/bin/python
import os
import time
import datetime
import subprocess

from gi.repository import Gtk as gtk, AppIndicator3 as appindicator, GObject as gobject
from threading import Event, Thread

from protonvpn_cli.utils import (
    is_connected,
    get_config_value,
    get_servers,
    get_server_value,
)

'''
Set the local paths for the tray icons.
'''
current_path = os.path.dirname(os.path.realpath(__file__))
green_icon = os.path.join(current_path, 'icons', 'green.png')
red_icon = os.path.join(current_path, 'icons', 'red.png')

class Indicator():
    def __init__(self):
        self.gtk = gtk
        self.gobject = gobject
        self.trayindicator = appindicator.Indicator.new("protonvpn-tray", red_icon, appindicator.IndicatorCategory.APPLICATION_STATUS)

        self.trayindicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.trayindicator.set_menu(self.menu())

        self.connection_error = True;

        self.gobject.timeout_add_seconds(1, self.main)

        self.main()

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

        return True

    '''
    Define the menu structure. There are three sections:
    - Connection Info
    - Config info
    - Exit
    '''
    def menu(self):
        self.menu = self.gtk.Menu()

        self.time_connected = self.gtk.MenuItem(label='')
        self.menu.append(self.time_connected)

        self.location_connected = self.gtk.MenuItem(label='')
        self.menu.append(self.location_connected)
        
        self.separator_0 = self.gtk.SeparatorMenuItem()
        self.menu.append(self.separator_0)
        self.separator_0.show()

        self.kill_switch = self.gtk.MenuItem(label='')
        self.menu.append(self.kill_switch)

        self.dns_leak_protection = self.gtk.MenuItem(label='')
        self.menu.append(self.dns_leak_protection)

        self.separator_1 = self.gtk.SeparatorMenuItem()
        self.menu.append(self.separator_1)
        self.separator_1.show()

        self.exittray = self.gtk.MenuItem('Exit')
        self.exittray.connect('activate', self.stop)
        self.menu.append(self.exittray)

        self.menu.show_all()
        return self.menu


    '''
    Verifies if currently connected to a server.
    If the connection state changes, update the UI immediately.
    Sets the colour of the tray indicator icon to reflect the connetion status. 
    '''
    def report_is_connected(self):

        if is_connected():
            
            if self.connection_error:
                self.connection_error = False
                self.main()
                
            self.trayindicator.set_icon(green_icon)

        else:
            if not self.connection_error:
                self.connection_error = True
                self.main()

            self.trayindicator.set_icon(red_icon)

    '''
    Reports the current time elapsed since the connection was established.
    Sources the epoch time from the ProtonVPI-CLI config via a utility function.
    '''
    def report_time_connected(self):

        connection_time = "-"

        if not self.connection_error:
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
    '''
    def report_location_connected(self):

        location_string = "-"
        
        if not self.connection_error:
            try:
                servers = get_servers()
                connected_server = get_config_value("metadata", "connected_server")
                country_code = get_server_value(connected_server, "EntryCountry", servers)
                city = get_server_value(connected_server, "City", servers)
                location_string = "{city}, {cc}".format(cc=country_code, city=city)
            except (BaseException):
                print("Error Reporting Connected Server")

        self.location_connected.get_child().set_text(location_string)

    '''
    Reports the Kill Switch status, sourced from the ProtonVPN-CLI config.
    '''
    def report_kill_switch(self):

        kill_switch_status = "-"

        try:
            kill_switch_flag = get_config_value("USER", "killswitch")
            kill_switch_status = "On" if kill_switch_flag == "1" else "Off"
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
    Quits the tray.
    '''
    def stop(self, source):
        self.gtk.main_quit()

Indicator()