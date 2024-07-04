import argparse
import time

from irobot_edu_sdk.backend.bluetooth import Bluetooth
from irobot_edu_sdk.robots import event, Create3

from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from myCobot_client.myCobot_client import call_cobot_function

COBOT_IP = "192.168.0.134"
COBOT_PORT = 12355

DETECTION_DISTANCE_THRESHOLD = 40
ROTATION_SPEED = 1
DETECTION_DISTANCE_SPINNING = 10
FINAL_DISTANCE = 5

FOLDED_POSITION = [5, -90, 100, -90, 0, -45]
MIDDLE_POSITION = [5, -70, -10, 0, 0, -45]
LIFT_POSITION = [5, -90, 0, 7, 0, -45]


def lift_cup():
    call_cobot_function(COBOT_IP, COBOT_PORT, "send_angles", MIDDLE_POSITION, 50)
    time.sleep(2)
    call_cobot_function(COBOT_IP, COBOT_PORT, "send_angles", LIFT_POSITION, 50)
    time.sleep(1)
    call_cobot_function(COBOT_IP, COBOT_PORT, "set_gripper_value", 0, 50)
    time.sleep(1)
    call_cobot_function(COBOT_IP, COBOT_PORT, "send_angles", FOLDED_POSITION, 50)
    time.sleep(2)


robot = Create3(Bluetooth())

@event(robot.when_touched, [False, True])
async def move_and_go_back(robot):
    await robot.reset_navigation()
    await robot.move(30)
    await robot.set_wheel_speeds(20, -20)
    await robot.wait(0.5)
    await robot.set_wheel_speeds(0, 0)
    await robot.wait(0.1)
    await robot.move(20)
    await robot.navigate_to(0, 0, 90)

@event(robot.when_touched, [True, False])
async def locate_item(robot):
    time.sleep(2)
    call_cobot_function(COBOT_IP, COBOT_PORT, "send_angles", FOLDED_POSITION, 50)
    call_cobot_function(COBOT_IP, COBOT_PORT, "set_gripper_value", 100, 50)
    time.sleep(1)

    # Spinning until the robot detects an obstacle
    for i in range(2):
        await robot.set_wheel_speeds(ROTATION_SPEED, -ROTATION_SPEED)
        call_cobot_function(COBOT_IP, COBOT_PORT, "wait_for_obstacle", DETECTION_DISTANCE_THRESHOLD, 1, custom=True) # 1 = the sensor to wait for
        await robot.set_wheel_speeds(0, 0)
        distances = call_cobot_function(COBOT_IP, COBOT_PORT, "get_ultrasonic_sensors", custom=True)
        await robot.move(distances[1] / 2)
    
    await robot.set_wheel_speeds(ROTATION_SPEED, -ROTATION_SPEED)
    call_cobot_function(COBOT_IP, COBOT_PORT, "wait_for_obstacle", DETECTION_DISTANCE_THRESHOLD, 1, custom=True) # 1 = the sensor to wait for
    await robot.set_wheel_speeds(0, 0)

    # Spin to the right until left sensor can see the item, then stop
    await robot.set_wheel_speeds(-ROTATION_SPEED, ROTATION_SPEED)
    call_cobot_function(COBOT_IP, COBOT_PORT, "wait_for_obstacle", DETECTION_DISTANCE_SPINNING, 0, custom=True) # 0 = the sensor to wait for
    await robot.set_wheel_speeds(0, 0)

    distance = call_cobot_function(COBOT_IP, COBOT_PORT, "get_ultrasonic_sensors", custom=True)[0]
    await robot.move(distance - FINAL_DISTANCE)

    time.sleep(1)
    lift_cup()



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='mycobot server')
    parser.add_argument('--host', type=str, help='host ip', default=COBOT_IP)
    parser.add_argument('--port', type=int, help='port number', default=COBOT_PORT)
    args = parser.parse_args()

    robot.play()
