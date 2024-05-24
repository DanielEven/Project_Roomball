from irobot_edu_sdk.backend.bluetooth import Bluetooth
from irobot_edu_sdk.robots import event, Create3

robot = Create3(Bluetooth())


@event(robot.when_play)
async def draw_square(robot):
    # move robot until it is close to an object
    await robot.set_wheel_speeds(100, 100)
    while max((await robot.get_ir_proximity()).sensors) < 80:
        pass
    await robot.set_wheel_speeds(0, 0)

    # set rgb based on distance to closest object
    while True:
        ir_sensors = (await robot.get_ir_proximity()).sensors
        print(ir_sensors)
        if max(ir_sensors) > 1500:
            await robot.set_lights_on_rgb(0, 0, 255)
        elif max(ir_sensors) > 500:
            await robot.set_lights_on_rgb(0, 255, 0)
        elif max(ir_sensors) > 100:
            await robot.set_lights_on_rgb(255, 0, 0)
        else:
            await robot.set_lights_off()


robot.play()
