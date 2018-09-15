#!/usr/bin/env python3

import RTIMU
from multiprocessing import Process
from math import degrees
from collections import namedtuple
import time
import json

class IMU_Process(Process):
    def __init__(self, current_yaw):
        super().__init__()
        self.daemon = True
        self.current_yaw = current_yaw

    def run(self):
        settings = RTIMU.Settings('RTIMULib')
        imu = RTIMU.RTIMU(settings)
        imu.IMUInit()
        poll_interval = float(imu.IMUGetPollInterval()) / 1000
        imu.setSlerpPower(0.02)
        imu.setGyroEnable(True)
        imu.setAccelEnable(True)
        imu.setCompassEnable(True)
        while True:
            if imu.IMURead():
                data = imu.getIMUData()
                self.current_yaw.value = (degrees(data['fusionPose'][2]) + 10) % 360
            time.sleep(poll_interval)
