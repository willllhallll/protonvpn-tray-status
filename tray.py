#!/usr/bin/python
import subprocess
import os
from gi.repository import Gtk as gtk, AppIndicator3 as appindicator
from threading import Event, Thread

current_path = os.path.dirname(os.path.realpath(__file__))
green_icon = os.path.join(current_path, 'icons', 'green.png')
red_icon = os.path.join(current_path, 'icons', 'red.png')

def call_repeatedly(interval, func):
    stopped = Event()
    def loop():
        while not stopped.wait(interval):
            func()
    Thread(target=loop).start()    
    return stopped.set

class Indicator():
    def __init__(self):
        self.trayindicator = appindicator.Indicator.new("protonvpn-tray", red_icon, appindicator.IndicatorCategory.APPLICATION_STATUS)
        self.trayindicator.set_status(appindicator.IndicatorStatus.ACTIVE)
        self.trayindicator.set_menu(self.menu())
        self.cancel_interval = call_repeatedly(5, self.report_connection)
        self.report_connection()

    def menu(self):
        menu = gtk.Menu()

        exittray = gtk.MenuItem('Exit')
        exittray.connect('activate', self.stop)
        menu.append(exittray)

        menu.show_all()
        return menu 

    def report_connection(self):
        output = subprocess.check_output("protonvpn status", shell=True)
        connected_string_index = output.find(b'Connected')

        if connected_string_index != -1:
            self.trayindicator.set_icon(green_icon)
        else:
            self.trayindicator.set_icon(red_icon)

    def stop(self, source):
        self.cancel_interval()
        gtk.main_quit()

Indicator()
gtk.main()