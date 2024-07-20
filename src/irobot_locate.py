import argparse
import time
from irobot_edu_sdk.backend.bluetooth import Bluetooth
from irobot_edu_sdk.robots import event, Create3
from myCobot_client import call_cobot_function
from server_commands import ServerCommands

# Constants for the cobot configuration and operation
COBOT_IP = "192.168.0.134"
COBOT_PORT = 12355
DETECTION_DISTANCE_THRESHOLD = 60
HOME_DISTANCE_THRESHOLD = 20
ROTATION_DEGREES = 90
ROTATION_SPEED = 1
SCAN_ROTATION_SPEED = 5
DETECTION_DISTANCE_SPINNING = 10
FINAL_DISTANCE = 5

# Arm positions for different actions
FOLDED_POSITION = [5, -90, 100, -90, 0, -45]
MIDDLE_POSITION = [5, -70, -10, 0, 0, -45]
LIFT_POSITION = [5, -90, 0, 7, 0, -45]
INSERT_POSITION = [2, -90, 50, -35, 0, -45]
INSERT_MIDDLE_POSITION = [2, -60, 30, -45, 0, -45]
SIDE_MIDDLE_POSITION_1 = [130, -80, 20, -5, 90, -90]
SIDE_MIDDLE_POSITION_2 = [130, -130, 20, -15, 90, -90]
SIDE_GRAB_POSITION = [155, -130, 20, -15, 90, -90]

# Initialize iRobot Create3 robot with Bluetooth
# Has to appear before the other functions.
robot = Create3(Bluetooth())

def lift_cup():
    """
    Lift the cup using the cobot arm.
    """
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SEND_ANGLES, MIDDLE_POSITION, 50)
    time.sleep(1.7)
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SEND_ANGLES, LIFT_POSITION, 50)
    time.sleep(0.5)
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SET_GRIPPER_VALUE, 0, 50)
    time.sleep(1)
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SEND_ANGLES, FOLDED_POSITION, 50)
    time.sleep(1.5)

def drop_cup():
    """
    Drop the cup using the cobot arm.
    """
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SEND_ANGLES, MIDDLE_POSITION, 50)
    time.sleep(1.7)
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SEND_ANGLES, LIFT_POSITION, 50)
    time.sleep(0.5)
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SET_GRIPPER_VALUE, 100, 50)
    time.sleep(1)
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SEND_ANGLES, FOLDED_POSITION, 50)
    time.sleep(1.5)

def insert_cup():
    """
    Insert the cup into the pile using the cobot arm.
    """
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SEND_ANGLES, INSERT_MIDDLE_POSITION, 50)
    time.sleep(0.5)
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SEND_ANGLES, INSERT_POSITION, 50)
    time.sleep(0.5)
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SET_GRIPPER_VALUE, 0, 50)
    time.sleep(1)
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SEND_ANGLES, FOLDED_POSITION, 50)
    time.sleep(1.5)


def lift_side_cup():
    """
    Lift a side cup using the cobot arm.
    """
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SEND_ANGLES, SIDE_MIDDLE_POSITION_1, 50)
    time.sleep(2)
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SEND_ANGLES, SIDE_MIDDLE_POSITION_2, 50)
    time.sleep(1)
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SEND_ANGLES, SIDE_GRAB_POSITION, 50)
    time.sleep(0.9)
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SET_GRIPPER_VALUE, 0, 50)
    time.sleep(1.3)
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SEND_ANGLES, SIDE_MIDDLE_POSITION_2, 50)
    time.sleep(0.9)
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SEND_ANGLES, SIDE_MIDDLE_POSITION_1, 50)
    time.sleep(1)
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.SEND_ANGLES, FOLDED_POSITION, 50)
    time.sleep(2)

# When close to the home pile, finds it and moving towards it, ending in the same distance.
async def locate_home(robot):
    await robot.wait(1)

    # Spinning until the robot detects an obstacle
    distances = call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.GET_ULTRASONIC_SENSORS)
    if distances[1] > HOME_DISTANCE_THRESHOLD:
        await robot.set_wheel_speeds(ROTATION_SPEED, -ROTATION_SPEED)
        # Blocking until an object within DETECTION_DISTANCE_THRESHOLD was found, 1 = the middle sensor
        while call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.WAIT_FOR_OBSTACLE, HOME_DISTANCE_THRESHOLD , 1) == "Timeout":
            pass
        await robot.set_wheel_speeds(0, 0)
        distances = call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.GET_ULTRASONIC_SENSORS)
    await robot.move(distances[1] / 2)
    
    # Spin to the right until middle sensor detects the object.
    distances = call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.GET_ULTRASONIC_SENSORS)
    if distances[1] > DETECTION_DISTANCE_SPINNING:
        await robot.set_wheel_speeds(ROTATION_SPEED, -ROTATION_SPEED)
        while call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.WAIT_FOR_OBSTACLE, DETECTION_DISTANCE_SPINNING, 1) == "Timeout":
            print("No object was found, continuing search")
        await robot.set_wheel_speeds(0, 0)

    # Spin to the left until right sensor can see the item, then stops
    await robot.set_wheel_speeds(-ROTATION_SPEED, ROTATION_SPEED)
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.WAIT_FOR_OBSTACLE, DETECTION_DISTANCE_SPINNING, 0) # 0 = the sensor to wait for
    await robot.set_wheel_speeds(0, 0)

    distance = call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.GET_ULTRASONIC_SENSORS)[0]
    await robot.move(distance - FINAL_DISTANCE)
async def locate_closest_item(robot):
    """
    Locate the closest item using the robot's sensors, and move towards it.
    This will be with corrections in front of the item - to end in a constant distance from it.
    THe function will also recognize the orientation of the cup.
    
    robot: The iRobot Create3 instance
    return: Cup orientation: "lift" for the cup's handle, "side" for the cup's side.
    If no item was found, return False.
    """
    min_distance = DETECTION_DISTANCE_THRESHOLD
    angle = (await robot.get_position()).heading
    start_angle = angle
    min_angle = angle

    # Find closest item, and turn towards it.
    await robot.set_wheel_speeds(SCAN_ROTATION_SPEED, -SCAN_ROTATION_SPEED)
    while (start_angle - angle) % 360 < ROTATION_DEGREES:
        distance = call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.WAIT_FOR_OBSTACLE, max(min_distance - 0.5, 0), 1)
        if distance == "Timeout":
            angle = (await robot.get_position()).heading
            continue
        distance = distance[0]
        angle = (await robot.get_position()).heading
        if (start_angle - angle) % 360 < ROTATION_DEGREES:
            min_distance = distance[1]
            min_angle = angle
    
    await robot.set_wheel_speeds(0, 0)
    current_angle = (await robot.get_position()).heading
    if start_angle == min_angle: # If didn't find any item:
        return False

    await robot.turn_left((min_angle - current_angle) % 360) # turn to closest item.

    # Driving to object, until the distance is less then DETECTION_DISTANCE_SPINNING * 2
    distances = call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.GET_ULTRASONIC_SENSORS)
    if distances[1] > DETECTION_DISTANCE_THRESHOLD:    # the angle correction
        await robot.set_wheel_speeds(ROTATION_SPEED, -ROTATION_SPEED)
    await robot.move(distances[1] / 2)
    loops = 1
    # each loop move half the distance from the item, then correct the angle of the irobot, until close enough to the item.
    while distances[1] > DETECTION_DISTANCE_SPINNING * 2:
        distances = call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.GET_ULTRASONIC_SENSORS)
        detection_distance = (DETECTION_DISTANCE_THRESHOLD / (2 ** loops)) + 5
        if distances[1] > detection_distance:    # the angle correction
            await robot.set_wheel_speeds(ROTATION_SPEED, -ROTATION_SPEED)
            # Blocking until an object within DETECTION_DISTANCE_THRESHOLD was found, 1 = the middle sensor
            while call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.WAIT_FOR_OBSTACLE, detection_distance, 1) == "Timeout":
                pass
            await robot.set_wheel_speeds(0, 0)
            distances = call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.GET_ULTRASONIC_SENSORS)
        await robot.move(distances[1] / 2)
        loops += 1
    
    # Spin to the right until middle sensor detects the object.
    distances = call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.GET_ULTRASONIC_SENSORS)
    if distances[1] > DETECTION_DISTANCE_SPINNING:
        await robot.set_wheel_speeds(ROTATION_SPEED, -ROTATION_SPEED)
        while call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.WAIT_FOR_OBSTACLE, DETECTION_DISTANCE_SPINNING, 1) == "Timeout":
            print("No object was found, continuing search")
        await robot.set_wheel_speeds(0, 0)

    # Spin to the right until left sensor can see the item, then stops
    await robot.set_wheel_speeds(ROTATION_SPEED, -ROTATION_SPEED)
    call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.WAIT_FOR_OBSTACLE, DETECTION_DISTANCE_SPINNING, 2) # 2 = the sensor to wait for
    await robot.set_wheel_speeds(0, 0)
    # Spin to the left until right sensor can see the item, then stops
    # Measure the time it took to decide the cup's orientation
    await robot.set_wheel_speeds(-ROTATION_SPEED, ROTATION_SPEED)
    t = call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.WAIT_FOR_OBSTACLE, DETECTION_DISTANCE_SPINNING, 0)[1] # 0 = the sensor to wait for
    await robot.set_wheel_speeds(0, 0)
    distance = call_cobot_function(COBOT_IP, COBOT_PORT, ServerCommands.GET_ULTRASONIC_SENSORS)[0]
    # move to be at constant distance, and now the pick_up_cup functions can be called.
    if t < 1.35:
        await robot.turn_right(180)
        await robot.move(-distance)
        # exit()
        # await robot.move(distance - 2)
        return "side"
    else:
        await robot.move(distance - FINAL_DISTANCE)
        return "lift"

async def retrieve_object(robot, insert=True):
    """
    Locating the closest item, lifting it, and returning to the home with it.
    Putting down the item: inside the pile if insert is True, otherwise on the ground.

    robot: The iRobot Create3 instance
    insert: Boolean flag to insert the object into a pile
    return: True if an object was retrieved, False otherwise
    """
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
        # Calibrate with respect to the cup
        await robot.navigate_to(5, 5, -ROTATION_DEGREES // 2 + 285)
        await locate_home(robot)
        insert_cup()
    else:
        await robot.navigate_to(0, 0, (-ROTATION_DEGREES // 2 + 270) % 360)
        drop_cup()
    await robot.turn_right(((await robot.get_position()).heading - 90) % 360)
    return True

@event(robot.when_touched, [True, False])
async def test(robot):
    """
    Test function to locate the closest item when the robot is touched.

    robot: The iRobot Create3 instance
    """
    await locate_closest_item(robot)

@event(robot.when_touched, [False, True])
async def get_items(robot):
    """
    Main loop to retrieve items and place them in a pile.

    robot: The iRobot Create3 instance
    """
    await robot.reset_navigation()
    to_insert = False
    items = 0
    while await retrieve_object(robot, insert=to_insert):
        items += 1
        to_insert = True # After putting down the first cup, the rest will be put inside the pile.
        await robot.wait(0.2)
    await robot.set_lights_on_rgb(0, 255, 0)
    print(f"Picked up {items} cups")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Roomball Functionality')
    parser.add_argument('--host', type=str, help='myCobot server IP', default=COBOT_IP)
    parser.add_argument('--port', type=int, help='myCobot port number', default=COBOT_PORT)
    args = parser.parse_args()
    
    COBOT_IP = args.host
    COBOT_PORT = args.port

    robot.play()
    