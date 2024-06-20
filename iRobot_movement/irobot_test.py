from irobot_edu_sdk.backend.bluetooth import Bluetooth
from irobot_edu_sdk.robots import event, Create3
import argparse
import requests
import time


DRIVING_SPEED = 10
DETECTION_THRESHOLD = 80
TARGET_DISTANCE = 1000
ROTATION_SPEED = 1
REPOSITION_SPEED = 1

COLORS = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (255, 0, 255), (0, 255, 255), (255, 255, 255)]
ROTATIONS = [66, 38, 20, 0, -20, -38, -66]

GRAB_ANGLES = [15, -75, -70, 60, 0, -30]
MIDDLE_ANGLES = [15, -75, 0, 0, 0, -30]
DEFAULT_ANGLES = [15, 10, -100, 3, 0, -30]

robot = Create3(Bluetooth())

@event(robot.when_play)
async def move_until_close(robot, speed=100, distance=80):
    '''
    Move the robot until it is close to an object.
    Return the the sensor values.
    '''
    await robot.set_wheel_speeds(speed, speed)
    while max((await robot.get_ir_proximity()).sensors) < distance:
        pass
    await robot.set_wheel_speeds(0, 0)

    return (await robot.get_ir_proximity()).sensors

def call_cobot_function(ip_addr, port, func_name, *params):
    url = f"http://{ip_addr}:{port}/call/{func_name}?args="
    for i, param in enumerate(params):
        if type(param) == tuple:
            url += f"({','.join(str(x) for x in param)})"
        else:
            url += f"{param}"
        if i != len(params) - 1:
            url += ","
    return requests.get(url)


def grab_object():
    call_cobot_function("192.168.0.134", 12355, "set_gripper_value", 100, 50)
    time.sleep(1)
    call_cobot_function("192.168.0.134", 12355, "send_angles", GRAB_ANGLES, 50)
    time.sleep(1.5)
    call_cobot_function("192.168.0.134", 12355, "set_gripper_value", 100, 50)
    time.sleep(0.5)
    call_cobot_function("192.168.0.134", 12355, "send_angles", MIDDLE_ANGLES, 50)
    time.sleep(1)
    call_cobot_function("192.168.0.134", 12355, "send_angles", DEFAULT_ANGLES, 50)
    time.sleep(1)


@event(robot.when_play)
async def find_objects(robot):
    # set rgb based on sensor closest to object
    while True:
        ir_sensors = (await robot.get_ir_proximity()).sensors
        sense = max(ir_sensors)
        if sense > DETECTION_THRESHOLD:
            await robot.set_lights_on_rgb(*COLORS[ir_sensors.index(sense)])
        else:
            await robot.set_lights_off()


@event(robot.when_touched, [True, False])
async def find_objects_once(robot):
    # time.sleep(2)
    # call_cobot_function("192.168.0.134", 12355, "send_angles", MIDDLE_ANGLES, 50)
    # call_cobot_function("192.168.0.134", 12355, "send_angles", DEFAULT_ANGLES, 50)
    # move robot until it is close to an object
    # drive forward until object is detected
    await robot.set_wheel_speeds(DRIVING_SPEED, DRIVING_SPEED)
    while max((await robot.get_ir_proximity()).sensors) < DETECTION_THRESHOLD:
        pass
    await robot.set_wheel_speeds(0, 0)

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
    parser.add_argument('--host', type=str, help='host ip', default='192.168.0.134')
    parser.add_argument('--port', type=int, help='port number', default=12355)
    args = parser.parse_args()

    robot.play()
