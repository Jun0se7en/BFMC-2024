import sys
import os
import time

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.append(BASE_DIR)

from lib.control.UITCar import UITCar

if __name__ == "__main__":
    # Motor init
    Car = UITCar()
    Car.setMotorMode(0)
    Car.setSpeed_cm(40)
    print("begin:")
    time.sleep(5)
    # Car.setSpeed_cm(58)
    # Car.setAngle(20) #
    # time.sleep(5)
    # Car.setAngle(10)
    # time.sleep(5)
    # Car.setAngle(0)
    Car.setSpeed_cm(0)
    print("g")