#!/usr/bin/env python3

import gps
from multiprocessing import Process
from collections import namedtuple

class GPS_Process(Process):
    def __init__(self, lat, lon):
        super().__init__()
        self.daemon = True
        self.lat = lat
        self.lon = lon

    def run(self):
        session = gps.gps(mode = gps.WATCH_ENABLE)
        for record in session:
            if record['class'] == 'TPV' and (record['mode'] == 2 or record['mode'] == 3):
                self.lat.value = float(record['lat'])
                self.lon.value = float(record['lon'])
