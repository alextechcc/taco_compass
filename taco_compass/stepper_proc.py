#!/usr/bin/env python3

import time
import RPi.GPIO as GPIO
import atexit
from collections import namedtuple
from multiprocessing import Process

class Stepper_Process(Process):
    stepper_pins = namedtuple('stepper_pins', ['enable', 'step', 'dir', 'sens'])
    def __init__(self, target_angle, enable_pin, step_pin, dir_pin, sens_pin, steps_per_rev):
        super().__init__()
        self.daemon = True
        self.target_angle = target_angle
        self.pins = Stepper_Process.stepper_pins(enable_pin, step_pin, dir_pin, sens_pin)
        self.pos_angle = 0
        self.steps_per_rev = steps_per_rev
        self.step_angle = 360 / self.steps_per_rev
        self.rate = 0.005
        self.idle_ticks = 10
        self.idle_counter = 0
        self.init_gpio()
        self.CAL_RETRY_COUNT = 4
        print('Steps per rev: {}, Step angle: {}'.format(self.steps_per_rev, self.step_angle))
        self.calibrate()
        atexit.register(self.cleanup)

    def run(self):
        while True:
            if abs(self.target_angle.value - self.pos_angle) > self.step_angle * 1.5:
                GPIO.output(self.pins.enable, False)
                direction = self.get_target_direction()
                self.step(direction)
                self.idle_counter = 0
            elif self.idle_counter < self.idle_ticks:
                self.idle_counter += 1
                time.sleep(self.rate * 2)
            else:
                GPIO.output(self.pins.enable, True)
                time.sleep(self.rate * 2)

    def sens_stable(self, samples=5):
        on_count = 0
        for i in range(samples):
            if GPIO.input(self.pins.sens):
                on_count += 1
            time.sleep(0.001)
        return on_count > 0

    def calibrate(self):
        GPIO.output(self.pins.enable, False)
        # If already under sensor, move away first
        if self.sens_stable():
            for i in range(20):
                self.step(False)
        while not self.sens_stable():
            self.step(True)

        GPIO.output(self.pins.enable, True)
        self.pos_angle = 0
        print('Motor Calibrated')


    def get_target_direction(self):
        # If we're more than 180 degrees off from the target, go the opposite way to get to it
        invert = abs(self.target_angle.value - self.pos_angle) > 180
        direction = self.target_angle.value - self.pos_angle > 1
        return direction != invert

    def step(self, clockwise):
        GPIO.output(self.pins.dir, clockwise)
        time.sleep(self.rate)
        GPIO.output(self.pins.step, True)
        time.sleep(self.rate)
        GPIO.output(self.pins.step, False)
        if clockwise:
            self.pos_angle = (self.pos_angle + self.step_angle) % 360
        else:
            self.pos_angle = (self.pos_angle - self.step_angle) % 360

    def init_gpio(self):
        GPIO.setwarnings(False)
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.pins.enable, GPIO.OUT)
        GPIO.setup(self.pins.step, GPIO.OUT)
        GPIO.setup(self.pins.dir, GPIO.OUT)
        GPIO.setup(self.pins.sens, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        self.disable_motors()

    def cleanup(self):
        self.disable_motors()
        #GPIO.cleanup()

    def disable_motors(self):
        GPIO.output(self.pins.step, False)
        GPIO.output(self.pins.dir, False)
        GPIO.output(self.pins.enable, True)
