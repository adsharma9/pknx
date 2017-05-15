"""KNX timeupdater module

This implements a method to send date and time update packets to the KNX bus
"""

import threading
from time import sleep
import datetime

from knxip.core import parse_group_address
from knxip.ip import KNXIPTunnel
from knxip.conversion import *
from time import sleep


class KNXDateTimeUpdater():

    def __init__(self, knxiptunnel,
                 dateaddr=None,
                 timeaddr=None,
                 datetimeaddr=None,
                 daynightaddr=None,
                 lat=45,
                 long=0,
                 updateinterval=60):

        self.tunnel = knxiptunnel
        self.dateaddr = dateaddr

        if timeaddr is not None:
            self.timeaddr = parse_group_address(timeaddr)
        else:
            self.timeaddr = None

        if dateaddr is not None:
            self.dateaddr = parse_group_address(dateaddr)
        else:
            self.dateaddr = None

        if datetimeaddr is not None:
            self.datetimeaddr = parse_group_address(datetimeaddr)
        else:
            self.datetimeaddr = None

        if daynightaddr is not None:
            self.daynightaddr = parse_group_address(daynightaddr)
        else:
            self.daynightaddr = None

        self.updateinterval = updateinterval
        self.lat = lat
        self.long = long
        self.updater_running = False

    def send_updates(self):
        d = datetime.now()
        if self.timeaddr:
            self.tunnel.group_write(self.timeaddr,
                                    time_to_knx(d))

        if self.dateaddr:
            self.tunnel.group_write(self.dateaddr,
                                    date_to_knx(d))

        if self.datetimeaddr:
            self.tunnel.group_write(self.datetimeaddr,
                                    datetime_to_knx(d))

        if self.daynightaddr:
            from pysolar.solar import get_altitude
            alt = get_altitude(lat, long, d)
            if alt > 0:
                self.tunnel.group_write(self.daynightaddr, 1)
            else:
                self.tunnel.group_write(self.daynightaddr, 0)

    def updater_loop(self):
        self.updater_running = True
        while (self.updater_running):
            self.send_updates()
            sleep(self.updateinterval)

    def run_updater_in_background(self):
        thread = threading.Thread(target=self.updater_loop())
        thread.daemon = True
        thread.start()
