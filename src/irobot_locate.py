import argparse
import time

from irobot_edu_sdk.backend.bluetooth import Bluetooth
from irobot_edu_sdk.robots import event, Create3


from myCobot_client import call_cobot_function
from server_commands import ServerCommands

COBOT_IP = "192.168.0.134"
COBOT_PORT = 12355

DETECTION_DISTANCE_THRESHOLD = 60
HOME_DISTANCE_THRESHOLD = 20
ROTATION_SPEED = 1
SCAN_ROTATION_SPEED = 5
DETECTION_DISTANCE_SPINNING = 10
FINAL_DISTANCE = 5

FOLDED_POSITION = [5, -90, 100, -90, 0, -45]
MIDDLE_POSITION = [5, -70, -10, 0, 0, -45]
LIFT_POSITION = [5, -90, 0, 7, 0, -45]
INSERT_POSITION = [5, -90, 50, -35, 0, -45]
INSERT_MIDDLE_POSITION = [5, -60, 30, -45, 0, -45]
SIDE_MIDDLE_POSITION_1 = [-50, -80, 20, -5, 90, -90]
SIDE_MIDDLE_POSITION_2 = [-50, -130, 20, 0, 90, -110]
SIDE_GRAB_POSITION = [-35, -130, 20, 0, 90, -110]

#Initalize irobot, needs to be before all functions including robot
robot = Create3(Bluetooth())

def lift_cup():
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SEND_ANGLES, MIDDLE_POSITION, 50)
    time.sleep(1.7)
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SEND_ANGLES, LIFT_POSITION, 50)
    time.sleep(0.5)
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SET_GRIPPER_VALUE, 0, 50)
    time.sleep(1)
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SEND_ANGLES, FOLDED_POSITION, 50)
    time.sleep(1.5)

def drop_cup():
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SEND_ANGLES, MIDDLE_POSITION, 50)
    time.sleep(1.7)
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SEND_ANGLES, LIFT_POSITION, 50)
    time.sleep(0.5)
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SET_GRIPPER_VALUE, 100, 50)
    time.sleep(1)
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SEND_ANGLES, FOLDED_POSITION, 50)
    time.sleep(1.5)


def insert_cup():
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SEND_ANGLES, INSERT_MIDDLE_POSITION, 50)
    time.sleep(1.7)
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SEND_ANGLES, INSERT_POSITION, 50)
    time.sleep(0.5)
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SET_GRIPPER_VALUE, 100, 50)
    time.sleep(1)
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SEND_ANGLES, FOLDED_POSITION, 50)
    time.sleep(1.5)


def lift_side_cup():
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SEND_ANGLES, SIDE_MIDDLE_POSITION_1, 50)
    time.sleep(1.7)
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SEND_ANGLES, SIDE_MIDDLE_POSITION_2, 50)
    time.sleep(0.7)
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SEND_ANGLES, SIDE_GRAB_POSITION, 50)
    time.sleep(0.6)
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SET_GRIPPER_VALUE, 0, 50)
    time.sleep(1)
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SEND_ANGLES, SIDE_MIDDLE_POSITION_2, 50)
    time.sleep(0.6)
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SEND_ANGLES, SIDE_MIDDLE_POSITION_1, 50)
    time.sleep(0.7)
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SEND_ANGLES, FOLDED_POSITION, 50)
    time.sleep(1.7)


async def locate_home(robot):
    await robot.wait(1)

    # Spinning until the robot detects an obstacle
    for i in range(2):
        distances = call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.GET_ULTRASONIC_SENSORS, custom=True)
        if distances[1] > HOME_DISTANCE_THRESHOLD:
            await robot.set_wheel_speeds(ROTATION_SPEED, -ROTATION_SPEED)
            # Blocking until an object within DETECTION_DISTANCE_THRESHOLD was found, 1 = the middle sensor
            while call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.WAIT_FOR_OBSTACLE, HOME_DISTANCE_THRESHOLD , 1, custom=True) == "Timeout":
                pass
            await robot.set_wheel_speeds(0, 0)
            distances = call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.GET_ULTRASONIC_SENSORS, custom=True)
        await robot.move(distances[1] / 2)
    
    # Spin to the right until middle sensor detects the object.
    distances = call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.GET_ULTRASONIC_SENSORS, custom=True)
    if distances[1] > DETECTION_DISTANCE_SPINNING:
        await robot.set_wheel_speeds(ROTATION_SPEED, -ROTATION_SPEED)
        while call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.WAIT_FOR_OBSTACLE, DETECTION_DISTANCE_SPINNING, 1, custom=True) == "Timeout":
            print("No object was found, continuing search")
        await robot.set_wheel_speeds(0, 0)

    # Spin to the left until right sensor can see the item, then stops
    await robot.set_wheel_speeds(-ROTATION_SPEED, ROTATION_SPEED)
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.WAIT_FOR_OBSTACLE, DETECTION_DISTANCE_SPINNING, 0, custom=True) # 0 = the sensor to wait for
    await robot.set_wheel_speeds(0, 0)

    distance = call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.GET_ULTRASONIC_SENSORS, custom=True)[0]
    await robot.move(distance - FINAL_DISTANCE)


async def locate_closest_item(robot):
    min_distance = DETECTION_DISTANCE_THRESHOLD
    angle = (await robot.get_position()).heading
    start_angle = angle
    min_angle = angle

    await robot.set_wheel_speeds(SCAN_ROTATION_SPEED, -SCAN_ROTATION_SPEED)
    while (start_angle - angle) % 360 < 90:
        distance = call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.WAIT_FOR_OBSTACLE, max(min_distance - 0.5, 0), 1, custom=True)
        if distance == "Timeout":
            angle = (await robot.get_position()).heading
            continue
        distance = distance[0]
        angle = (await robot.get_position()).heading
        if (start_angle - angle) % 360 < 90:
            min_distance = distance[1]
            min_angle = angle
    
    await robot.set_wheel_speeds(0, 0)
    current_angle = (await robot.get_position()).heading
    if start_angle == min_angle:
        return False

    await robot.turn_left((min_angle - current_angle) % 360)

    #  Driving to object
    distances = call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.GET_ULTRASONIC_SENSORS, custom=True)
    await robot.move(distances[1] / 2)
    loops = 1
    while distances[1] > DETECTION_DISTANCE_SPINNING * 2:
        distances = call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.GET_ULTRASONIC_SENSORS, custom=True)
        detection_distance = (DETECTION_DISTANCE_THRESHOLD / (2 ** loops)) + 5
        if distances[1] > detection_distance:
            await robot.set_wheel_speeds(ROTATION_SPEED, -ROTATION_SPEED)
            # Blocking until an object within DETECTION_DISTANCE_THRESHOLD was found, 1 = the middle sensor
            while call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.WAIT_FOR_OBSTACLE, detection_distance, 1, custom=True) == "Timeout":
                pass
            await robot.set_wheel_speeds(0, 0)
            distances = call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.GET_ULTRASONIC_SENSORS, custom=True)
        await robot.move(distances[1] / 2)
        loops += 1
    
    # Spin to the right until middle sensor detects the object.
    distances = call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.GET_ULTRASONIC_SENSORS, custom=True)
    if distances[1] > DETECTION_DISTANCE_SPINNING:
        await robot.set_wheel_speeds(ROTATION_SPEED, -ROTATION_SPEED)
        while call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.WAIT_FOR_OBSTACLE, DETECTION_DISTANCE_SPINNING, 1, custom=True) == "Timeout":
            print("No object was found, continuing search")
        await robot.set_wheel_speeds(0, 0)

    # Spin to the right until left sensor can see the item, then stops
    await robot.set_wheel_speeds(ROTATION_SPEED, -ROTATION_SPEED)
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.WAIT_FOR_OBSTACLE, DETECTION_DISTANCE_SPINNING, 2, custom=True) # 2 = the sensor to wait for
    await robot.set_wheel_speeds(0, 0)
    # Spin to the left until right sensor can see the item, then stops
    await robot.set_wheel_speeds(-ROTATION_SPEED, ROTATION_SPEED)
    t = call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.WAIT_FOR_OBSTACLE, DETECTION_DISTANCE_SPINNING, 0, custom=True)[1] # 0 = the sensor to wait for
    print(t)
    await robot.set_wheel_speeds(0, 0)
    distance = call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.GET_ULTRASONIC_SENSORS, custom=True)[0]
    if t < 1.4:
        await robot.move(distance - FINAL_DISTANCE + 4)
        return "side"
    else:
        await robot.move(distance - FINAL_DISTANCE)
        return "lift"


async def retrieve_object(robot, insert=True):
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SEND_ANGLES, FOLDED_POSITION, 50)
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SET_GRIPPER_VALUE, 100, 50)
    await robot.wait(1)
    closest_item = await locate_closest_item(robot)
    if not closest_item:
        return False
    if closest_item == "lift":
        lift_cup()
    else:
        lift_side_cup()
    if insert:
        # calibrate with respect to the cup
        await robot.navigate_to(5, 5, 285)
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
        await robot.wait(0.2)
    await robot.set_lights_on_rgb(0, 255, 0)



if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='mycobot server')
    parser.add_argument('--host', type=str, help='host ip', default=COBOT_IP)
    parser.add_argument('--port', type=int, help='port number', default=COBOT_PORT)
    args = parser.parse_args()

    robot.play()
