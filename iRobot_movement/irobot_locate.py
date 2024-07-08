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
HOME_DISTANCE_THRESHOLD = 20
ROTATION_SPEED = 1
DETECTION_DISTANCE_SPINNING = 10
FINAL_DISTANCE = 5

FOLDED_POSITION = [5, -90, 100, -90, 0, -45]
MIDDLE_POSITION = [5, -70, -10, 0, 0, -45]
LIFT_POSITION = [5, -90, 0, 7, 0, -45]
INSERT_POSITION = [5, -90, 50, -35, 0, -45]
INSERT_MIDDLE_POSITION = [5, -60, 30, -45, 0, -45]

#Initalize irobot, needs to be before all functions including robot
robot = Create3(Bluetooth())

def lift_cup():
    call_cobot_function(COBOT_IP, COBOT_PORT, "send_angles", MIDDLE_POSITION, 50)
    time.sleep(1.7)
    call_cobot_function(COBOT_IP, COBOT_PORT, "send_angles", LIFT_POSITION, 50)
    time.sleep(0.5)
    call_cobot_function(COBOT_IP, COBOT_PORT, "set_gripper_value", 0, 50)
    time.sleep(1)
    call_cobot_function(COBOT_IP, COBOT_PORT, "send_angles", FOLDED_POSITION, 50)
    time.sleep(1.5)

def drop_cup():
    call_cobot_function(COBOT_IP, COBOT_PORT, "send_angles", MIDDLE_POSITION, 50)
    time.sleep(1.7)
    call_cobot_function(COBOT_IP, COBOT_PORT, "send_angles", LIFT_POSITION, 50)
    time.sleep(0.5)
    call_cobot_function(COBOT_IP, COBOT_PORT, "set_gripper_value", 100, 50)
    time.sleep(1)
    call_cobot_function(COBOT_IP, COBOT_PORT, "send_angles", FOLDED_POSITION, 50)
    time.sleep(1.5)


def insert_cup():
    call_cobot_function(COBOT_IP, COBOT_PORT, "send_angles", INSERT_MIDDLE_POSITION, 50)
    time.sleep(1.7)
    call_cobot_function(COBOT_IP, COBOT_PORT, "send_angles", INSERT_POSITION, 50)
    time.sleep(0.5)
    call_cobot_function(COBOT_IP, COBOT_PORT, "set_gripper_value", 100, 50)
    time.sleep(1)
    call_cobot_function(COBOT_IP, COBOT_PORT, "send_angles", FOLDED_POSITION, 50)
    time.sleep(1.5)


async def locate_home(robot):
    await robot.wait(1)

    # Spinning until the robot detects an obstacle
    for i in range(2):
        distances = call_cobot_function(COBOT_IP, COBOT_PORT, "get_ultrasonic_sensors", custom=True)
        if distances[1] > HOME_DISTANCE_THRESHOLD:
            await robot.set_wheel_speeds(ROTATION_SPEED, -ROTATION_SPEED)
            # Blocking until an object within DETECTION_DISTANCE_THRESHOLD was found, 1 = the middle sensor
            while call_cobot_function(COBOT_IP, COBOT_PORT, "wait_for_obstacle", HOME_DISTANCE_THRESHOLD , 1, custom=True) == "Timeout":
                pass
            await robot.set_wheel_speeds(0, 0)
            distances = call_cobot_function(COBOT_IP, COBOT_PORT, "get_ultrasonic_sensors", custom=True)
        await robot.move(distances[1] / 2)
    
    # Spin to the left until middle sensor detects the object.
    distances = call_cobot_function(COBOT_IP, COBOT_PORT, "get_ultrasonic_sensors", custom=True)
    if distances[1] > DETECTION_DISTANCE_SPINNING:
        await robot.set_wheel_speeds(ROTATION_SPEED, -ROTATION_SPEED)
        while call_cobot_function(COBOT_IP, COBOT_PORT, "wait_for_obstacle", DETECTION_DISTANCE_SPINNING, 1, custom=True) == "Timeout":
            print("No object was found, continuing search")
        await robot.set_wheel_speeds(0, 0)

    # Spin to the right until left sensor can see the item, then stops
    await robot.set_wheel_speeds(-ROTATION_SPEED, ROTATION_SPEED)
    call_cobot_function(COBOT_IP, COBOT_PORT, "wait_for_obstacle", DETECTION_DISTANCE_SPINNING, 0, custom=True) # 0 = the sensor to wait for
    await robot.set_wheel_speeds(0, 0)

    distance = call_cobot_function(COBOT_IP, COBOT_PORT, "get_ultrasonic_sensors", custom=True)[0]
    await robot.move(distance - FINAL_DISTANCE)


async def locate_closest_item(robot):
    min_distance = DETECTION_DISTANCE_THRESHOLD
    angle = (await robot.get_position()).heading
    start_angle = angle
    min_angle = angle

    await robot.set_wheel_speeds(ROTATION_SPEED, -ROTATION_SPEED)
    while (start_angle - angle) % 360 < 90:
        distance = call_cobot_function(COBOT_IP, COBOT_PORT, "wait_for_obstacle", min_distance - 0.5, 1, custom=True)
        if distance == "Timeout":
            angle = (await robot.get_position()).heading
            continue
        angle = (await robot.get_position()).heading
        if (start_angle - angle) % 360 < 90:
            min_distance = distance[1]
            min_angle = angle
            print(f"updated to distance {distance} and angle {angle}")
    
    await robot.set_wheel_speeds(0, 0)
    print(min_angle, min_distance)
    print(await robot.get_position())
    current_angle = (await robot.get_position()).heading
    print(current_angle, min_angle)
    if start_angle == min_angle:
        return False

    await robot.turn_left((min_angle - current_angle) % 360)

    #  Driving to obeject
    distances = call_cobot_function(COBOT_IP, COBOT_PORT, "get_ultrasonic_sensors", custom=True)
    await robot.move(distances[1] / 2)
    loops = 1
    while distances[1] > DETECTION_DISTANCE_SPINNING * 2:
        distances = call_cobot_function(COBOT_IP, COBOT_PORT, "get_ultrasonic_sensors", custom=True)
        detection_distance = (DETECTION_DISTANCE_THRESHOLD / (2 ** loops)) + 10
        if distances[1] > detection_distance:
            await robot.set_wheel_speeds(ROTATION_SPEED, -ROTATION_SPEED)
            # Blocking until an object within DETECTION_DISTANCE_THRESHOLD was found, 1 = the middle sensor
            while call_cobot_function(COBOT_IP, COBOT_PORT, "wait_for_obstacle", detection_distance, 1, custom=True) == "Timeout":
                pass
            await robot.set_wheel_speeds(0, 0)
            distances = call_cobot_function(COBOT_IP, COBOT_PORT, "get_ultrasonic_sensors", custom=True)
        await robot.move(distances[1] / 2)
    
    # Spin to the left until middle sensor detects the object.
    distances = call_cobot_function(COBOT_IP, COBOT_PORT, "get_ultrasonic_sensors", custom=True)
    if distances[1] > DETECTION_DISTANCE_SPINNING:
        await robot.set_wheel_speeds(ROTATION_SPEED, -ROTATION_SPEED)
        while call_cobot_function(COBOT_IP, COBOT_PORT, "wait_for_obstacle", DETECTION_DISTANCE_SPINNING, 1, custom=True) == "Timeout":
            print("No object was found, continuing search")
        await robot.set_wheel_speeds(0, 0)

    # Spin to the right until left sensor can see the item, then stops
    await robot.set_wheel_speeds(-ROTATION_SPEED, ROTATION_SPEED)
    call_cobot_function(COBOT_IP, COBOT_PORT, "wait_for_obstacle", DETECTION_DISTANCE_SPINNING, 0, custom=True) # 0 = the sensor to wait for
    await robot.set_wheel_speeds(0, 0)

    distance = call_cobot_function(COBOT_IP, COBOT_PORT, "get_ultrasonic_sensors", custom=True)[0]
    await robot.move(distance - FINAL_DISTANCE)
    return True

async def retrieve_object(robot, insert=True):
    call_cobot_function(COBOT_IP, COBOT_PORT, "send_angles", FOLDED_POSITION, 50)
    call_cobot_function(COBOT_IP, COBOT_PORT, "set_gripper_value", 100, 50)
    await robot.wait(1)
    if not await locate_closest_item(robot):
        return False
    lift_cup()
    if insert:
        # calibrate with respect to the cup
        await robot.navigate_to(10, 10, 285)
        await locate_home(robot)
        insert_cup()
    else:
        await robot.navigate_to(0, 0, 270)
        drop_cup()
    await robot.turn_right(((await robot.get_position()).heading - 90) % 360)
    return True


@event(robot.when_touched, [True, False])
async def test(robot):
    await locate_closest_item(robot)

@event(robot.when_touched, [False, True])
async def get_items(robot):
    await robot.reset_navigation()
    to_insert = False
    while (await retrieve_object(robot, insert=to_insert)):
        to_insert = True
        await robot.wait(1)
    await robot.set_lights_on_rgb(0, 255, 0)
    # await retrieve_object(robot, insert=False)
    # await robot.wait(1)
    # await retrieve_object(robot)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='mycobot server')
    parser.add_argument('--host', type=str, help='host ip', default=COBOT_IP)
    parser.add_argument('--port', type=int, help='port number', default=COBOT_PORT)
    args = parser.parse_args()

    robot.play()
