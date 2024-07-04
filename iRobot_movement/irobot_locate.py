import argparse
import time

from irobot_edu_sdk.backend.bluetooth import Bluetooth
from irobot_edu_sdk.robots import event, Create3

from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from myCobot_client.myCobot_client import call_cobot_function

COBOT_IP = "192.168.0.134"
COBOT_PORT = 12355

DETECTION_DISTANCE_THRESHOLD = 60
ROTATION_SPEED = 1
DETECTION_DISTANCE_SPINNING = 10
FINAL_DISTANCE = 5

FOLDED_POSITION = [5, -90, 100, -90, 0, -45]
MIDDLE_POSITION = [5, -70, -10, 0, 0, -45]
LIFT_POSITION = [5, -90, 0, 7, 0, -45]

#Initalize irobot, needs to be before all functions inlucding robot
robot = Create3(Bluetooth())

def lift_cup():
    call_cobot_function(COBOT_IP, COBOT_PORT, "send_angles", MIDDLE_POSITION, 50)
    time.sleep(2)
    call_cobot_function(COBOT_IP, COBOT_PORT, "send_angles", LIFT_POSITION, 50)
    time.sleep(1)
    call_cobot_function(COBOT_IP, COBOT_PORT, "set_gripper_value", 0, 50)
    time.sleep(1)
    call_cobot_function(COBOT_IP, COBOT_PORT, "send_angles", FOLDED_POSITION, 50)
    time.sleep(2)

def drop_cup():
    call_cobot_function(COBOT_IP, COBOT_PORT, "send_angles", MIDDLE_POSITION, 50)
    time.sleep(2)
    call_cobot_function(COBOT_IP, COBOT_PORT, "send_angles", LIFT_POSITION, 50)
    time.sleep(1)
    call_cobot_function(COBOT_IP, COBOT_PORT, "set_gripper_value", 100, 50)
    time.sleep(1)
    call_cobot_function(COBOT_IP, COBOT_PORT, "send_angles", FOLDED_POSITION, 50)
    time.sleep(2)


async def locate_item(robot):
    call_cobot_function(COBOT_IP, COBOT_PORT, "send_angles", FOLDED_POSITION, 50)
    call_cobot_function(COBOT_IP, COBOT_PORT, "set_gripper_value", 100, 50)
    await robot.wait(1)

    # Spinning until the robot detects an obstacle
    for i in range(2):
        await robot.set_wheel_speeds(ROTATION_SPEED, -ROTATION_SPEED)
        # Blocking until an object within DETECTION_DISTANCE_THRESHOLD was found, 1 = the middle sensor
        if call_cobot_function(COBOT_IP, COBOT_PORT, "wait_for_obstacle", DETECTION_DISTANCE_THRESHOLD, 1, custom=True) == "timeout":
            print("No object was founded, stopping search")
            return

        await robot.set_wheel_speeds(0, 0)
        distances = call_cobot_function(COBOT_IP, COBOT_PORT, "get_ultrasonic_sensors", custom=True)
        await robot.move(distances[1] / 2)
    
    # Spin to the left until middle sensor detects the object.
    await robot.set_wheel_speeds(ROTATION_SPEED, -ROTATION_SPEED)
    if call_cobot_function(COBOT_IP, COBOT_PORT, "wait_for_obstacle", DETECTION_DISTANCE_SPINNING, 1, custom=True) == "timeout":
        print("No object was founded, stopping search")
        return
    await robot.set_wheel_speeds(0, 0)

    # Spin to the right until left sensor can see the item, then stops
    await robot.set_wheel_speeds(-ROTATION_SPEED, ROTATION_SPEED)
    call_cobot_function(COBOT_IP, COBOT_PORT, "wait_for_obstacle", DETECTION_DISTANCE_SPINNING, 0, custom=True) # 0 = the sensor to wait for
    await robot.set_wheel_speeds(0, 0)

    distance = call_cobot_function(COBOT_IP, COBOT_PORT, "get_ultrasonic_sensors", custom=True)[0]
    await robot.move(distance - FINAL_DISTANCE)
    time.sleep(1)

async def get_object(robot):
    await robot.wait(1)
    await locate_item(robot)
    lift_cup()
    await robot.navigate_to(0, 0, 270)
    drop_cup()
    await robot.turn_right(180)


@event(robot.when_touched, [False, True])
async def get_items(robot):
    await robot.reset_navigation()
    await get_object(robot)
    await robot.wait(1)
    await get_object(robot)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='mycobot server')
    parser.add_argument('--host', type=str, help='host ip', default=COBOT_IP)
    parser.add_argument('--port', type=int, help='port number', default=COBOT_PORT)
    args = parser.parse_args()

    robot.play()
