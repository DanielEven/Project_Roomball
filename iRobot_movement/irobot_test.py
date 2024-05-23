#
# Licensed under 3-Clause BSD license available in the License file. Copyright (c) 2021-2023 iRobot Corporation. All rights reserved.
#

# Want to draw a square?

from irobot_edu_sdk.backend.bluetooth import Bluetooth
from irobot_edu_sdk.robots import event, hand_over, Color, Robot, Root, Create3
from irobot_edu_sdk.music import Note
import time

robot = Root(Bluetooth())
#robot = Create3(Bluetooth())

notes = "eee eee egcde fff ffee eeggfdc "
beats = [2,2,3,1, 2,2,3,1, 2,2,3,1,4,4, 2,2,3,0, 1,2,2,2,0, 1,1,2,2,2,2,4,4]
songLength = len(notes)
tempo = 0.1

@event(robot.when_play)
async def draw_square(robot):
    # await robot.navigate_to(16,16)  # Will have no effect on Create 3.

    # The "_" means that we are not using the temporal variable to get any value when iterating.
    # So the purpose of this "for" loop is just to repeat 4 times the actions inside it:
    
    await robot.move(50)  # cm
    #await robot.turn_left(90)  # deg
    await robot.move(-50)  # Will have no effect on Create 3.

    for i in range(songLength):
        duration = beats[i] * tempo
        if (notes[i] == ' '):
            time.sleep(duration)
        else:
            await robot.play_note(eval(f"Note.{notes[i].capitalize()}4"), duration)

robot.play()
