import argparse
from irobot_edu_sdk.backend.bluetooth import Bluetooth
from irobot_edu_sdk.robots import event, Create3

from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from myCobot_client.myCobot_client import call_cobot_function

COBOT_IP = "192.168.0.134"
COBOT_PORT = 12335 

DRIVING_SPEED = 10
DETECTION_DISTANCE_THRESHOLD = 200
ROTATION_SPEED = 1
WANTED_DISTANCE_FROM_OBSTACLE = [15, 5]
DETECTION_DISTANCE_SPINNING = 10


robot = Create3(Bluetooth())

@event(robot.when_touched, [False, True])
async def move_and_go_back():
    await robot.reset_navigation()
    await robot.move(10)
    await robot.set_wheel_speeds(ROTATION_SPEED, -ROTATION_SPEED)
    await robot.move(10)
    await robot.navigate_to(0, 0)

@event(robot.when_touched, [True, False])
async def locate_item(robot):

    # Spinning until the robot detects an obstacle
    await robot.set_wheel_speeds(ROTATION_SPEED, -ROTATION_SPEED)
    call_cobot_function(COBOT_IP, COBOT_PORT, "wait_for_obstacle", DETECTION_DISTANCE_THRESHOLD, 1, custom=True) # 1 = the sensor to wait for
    await robot.set_wheel_speeds(0, 0)

    # Read the obstacle distance and move towards it + fixing distance
    for dist in WANTED_DISTANCE_FROM_OBSTACLE:
        res = call_cobot_function(COBOT_IP, COBOT_PORT, "get_ultrasonic_sensors")
        await robot.move(res[1] - dist) # Move the robot to near the obstacle

    # Spin to the right until left sensor can see the item, then stop
    await robot.set_wheel_speeds(-ROTATION_SPEED, ROTATION_SPEED)
    call_cobot_function(COBOT_IP, COBOT_PORT, "wait_for_obstacle", DETECTION_DISTANCE_SPINNING, 0, custom=True) # 0 = the sensor to wait for
    await robot.set_wheel_speed



    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='mycobot server')
    parser.add_argument('--host', type=str, help='host ip', default=COBOT_IP)
    parser.add_argument('--port', type=int, help='port number', default=COBOT_PORT)
    args = parser.parse_args()

    robot.play()

