from irobot_edu_sdk.backend.bluetooth import Bluetooth
from irobot_edu_sdk.robots import event, Create3
import argparse
import time

from os import sys, path
sys.path.append(path.dirname(path.dirname(path.abspath(__file__))))
from myCobot_client.myCobot_client import call_cobot_function

COBOT_IP = "192.168.0.134"
COBOT_PORT = 12335 

DRIVING_SPEED = 10
DETECTION_THRESHOLD = 80
DETECTION_DISTANCE_THRESHOLD = 10
TARGET_DISTANCE = 1000
ROTATION_SPEED = 1
REPOSITION_SPEED = 1

COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255), (255, 255, 255)]
ROTATIONS = [66, 38, 20, 0, -20, -38, -66]

GRAB_ANGLES = [15, -75, -70, 60, 0, -30]
MIDDLE_ANGLES = [15, -75, 0, 0, 0, -30]
DEFAULT_ANGLES = [15, 10, -100, 3, 0, -30]

robot = Create3(Bluetooth())


def grab_object():
    call_cobot_function(COBOT_IP, COBOT_PORT, "set_gripper_value", 100, 50)
    time.sleep(1)
    call_cobot_function(COBOT_IP, COBOT_PORT, "send_angles", GRAB_ANGLES, 50)
    time.sleep(1.5)
    call_cobot_function(COBOT_IP, COBOT_PORT, "set_gripper_value", 100, 50)
    time.sleep(0.5)
    call_cobot_function(COBOT_IP, COBOT_PORT, "send_angles", MIDDLE_ANGLES, 50)
    time.sleep(1)
    call_cobot_function(COBOT_IP, COBOT_PORT, "send_angles", DEFAULT_ANGLES, 50)
    time.sleep(1)


@event(robot.when_play)
async def find_objects(robot):
    # set rgb based on sensor closest to object
    # while True:
    #     ir_sensors = (await robot.get_ir_proximity()).sensors
    #     print(ir_sensors[3])
    #     sense = max(ir_sensors)
    #     if sense > DETECTION_THRESHOLD:
    #         await robot.set_lights_on_rgb(*COLORS[ir_sensors.index(sense)])
    #     else:
    #         await robot.set_lights_off()
    await robot.set_wheel_speeds(DRIVING_SPEED, DRIVING_SPEED)
    call_cobot_function(COBOT_IP, COBOT_PORT, "wait_for_obstacle", DETECTION_DISTANCE_THRESHOLD)
    await robot.set_wheel_speeds(0, 0)
    call_cobot_function(COBOT_IP, COBOT_PORT, "get_ultrasonic_sensors")


@event(robot.when_touched, [True, False])
async def find_objects_once(robot):
    # time.sleep(2)
    # call_cobot_function(COBOT_IP, COBOT_PORT, "send_angles", MIDDLE_ANGLES, 50)
    # call_cobot_function(COBOT_IP, COBOT_PORT, "send_angles", DEFAULT_ANGLES, 50)
    # move robot until it is close to an object
    # drive forward until object is detected
    await robot.set_wheel_speeds(DRIVING_SPEED, DRIVING_SPEED)
    call_cobot_function(COBOT_IP, COBOT_PORT, "wait_for_obstacle", DETECTION_DISTANCE_THRESHOLD)
    await robot.set_wheel_speeds(0, 0)
    call_cobot_function(COBOT_IP, COBOT_PORT, "get_ultrasonic_sensors")


    time.sleep(1)

    # rotate to put object at center of robot
    ir_sensors = (await robot.get_ir_proximity()).sensors
    detected_distance = max(ir_sensors)
    # if ir_sensors.index(detected_distance) < 3:
    #     await robot.set_wheel_speeds(-ROTATION_SPEED, ROTATION_SPEED)
    # elif ir_sensors.index(detected_distance) > 3:
    #     await robot.set_wheel_speeds(ROTATION_SPEED, -ROTATION_SPEED)
    # while (await robot.get_ir_proximity()).sensors[3] < detected_distance * 0.85:
    #     pass
    # await robot.set_wheel_speeds(0, 0)
    await robot.turn_left(ROTATIONS[ir_sensors.index(detected_distance)])

    time.sleep(1)

    # move robot to put object at correct distance
    # middle_sensor = (await robot.get_ir_proximity()).sensors[3]
    # if middle_sensor < TARGET_DISTANCE:
    #     await robot.set_wheel_speeds(REPOSITION_SPEED, REPOSITION_SPEED)
    #     dist = (await robot.get_ir_proximity()).sensors[3]
    #     while dist < TARGET_DISTANCE:
    #         # print(dist, TARGET_DISTANCE)
    #         dist = (await robot.get_ir_proximity()).sensors[3]
    #     await robot.set_wheel_speeds(0, 0)
    # elif middle_sensor > TARGET_DISTANCE:
    #     await robot.set_wheel_speeds(-REPOSITION_SPEED, -REPOSITION_SPEED)
    #     dist = (await robot.get_ir_proximity()).sensors[3]
    #     while dist > TARGET_DISTANCE:
    #         # print(dist, TARGET_DISTANCE)
    #         dist = (await robot.get_ir_proximity()).sensors[3]
    #     await robot.set_wheel_speeds(0, 0)
    # time.sleep(1)
    print((await robot.get_ir_proximity()).sensors[3])


@event(robot.when_touched, [False, True])
async def drive(robot):
    await robot.move(30)
    time.sleep(1)
    await robot.move(-30)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='mycobot server')
    parser.add_argument('--host', type=str, help='host ip', default=COBOT_IP)
    parser.add_argument('--port', type=int, help='port number', default=COBOT_PORT)
    args = parser.parse_args()

    robot.play()
