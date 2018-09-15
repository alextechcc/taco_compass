#!/usr/bin/env python3

import time
from multiprocessing import Value
from utils import read_restaurants, get_delta
from stepper_proc import Stepper_Process
from imu_proc import IMU_Process
from gps_proc import GPS_Process
import math
import sys
import pickle
import socket

def main():
    if len(sys.argv) > 1:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((sys.argv[1], 15975))

    restaurants = read_restaurants()

    yaw = Value('d')
    imu_proc = IMU_Process(yaw)
    imu_proc.start()

    # Stepper is Red Blue White Yellow from top to bottom (towards knob) Dir = LOW means clockwise
    target_angle = Value('d')
    stepper_proc = Stepper_Process(target_angle, 15, 18, 23, 25, 200)
    stepper_proc.start()

    lat, lon = Value('d'), Value('d')
    gps_proc = GPS_Process(lat, lon)
    gps_proc.start()
    
    print_state = False
    while True:
        bearing = yaw.value
        delta, closest, dist = get_delta(bearing, restaurants, (lat.value, lon.value))
        target_angle.value = delta

        if math.floor(time.time() % 2) != print_state:
            data = (closest.name, dist, bearing, delta, closest.lat, closest.lon, lat.value, lon.value)

            if len(sys.argv) > 1:
                s.send(pickle.dumps(data))
            else:
                print('Closest: {}, Dist: {:.2f}\n\tBearing: {:.0f}, Delta: {:.0f}\n\tClosest: {},{}\n\tLoc: {},{}'
                                        .format(*data))

            print_state = not print_state
        time.sleep(0.005)

if __name__ == '__main__':
    main()
