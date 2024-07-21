## Overview

The iCreate operates in a continuous loop to locate, pick up, and stack items. This manual provides details about the core algorithm and important constants, and guides programmers on how to extend the functionality of the code.

## Algorithm

The robot performs the following steps in a loop:

1. Locate the closest item and navigate to it.
2. Pick up the item.
3. Return to the home position.
4. Stack the item.

### `locate_closest_item` Algorithm

This function locates the closest item and moves towards it, ensuring a consistent distance and angle from the item. The steps are as follows:

1. The robot spins 90 degrees to the right to locate the closest item, then spins back to face the item.
2. The robot moves towards the item in a loop:
    - Detect the distance from the item.
    - Move half the detected distance.
    - Correct the angle by turning right until the middle sensor realigns with the item.
    - Repeat until the robot is close enough to the item.
3. Determine the item's orientation (standing or lying down):
    - Spin to the right until the left sensor detects the item, then stop.
    - Spin to the left until the right sensor detects the item, then stop.
    - Measure the time taken to identify the item's orientation.
4. Position the robot at a constant distance, allowing the `pick_up_cup` function to be called.

## Important Constants

- `COBOT_IP = "192.168.0.134"`: Default IP address for the myCobot server.
- `COBOT_PORT = 12355`: Default port for the myCobot server.
- `DETECTION_DISTANCE_THRESHOLD = 60`: Maximum distance (in cm) for detecting items.
- `ROTATION_DEGREES = 90`: Rotation angle (in degrees) for searching items. It should be less than 360 to allow space for stacking items.

## Useful Function Conventions
### Calling the Server with `call_cobot_function`

The iCreate communicates with the myCobot server using the `call_cobot_function` client function. This function sends commands to the server to control the robot's movements and actions, in the following format:

```python
call_cobot_function(<COBOT_IP>, <COBOT_PORT>, ServerCommands.<COMMAND_NAME>, <args> ...)
```

- `<COBOT_IP>`: The IP address of the myCobot server.
- `<COBOT_PORT>`: The port number of the myCobot server.
- `ServerCommands.<COMMAND_NAME>`: The command to be executed by the server.
- `*args`: Additional arguments required by the command.

### Controlling the Robot with asynchronous Functions
THe iCreate interface provides asynchronous functions to control the robot's movements, with the following python async/await format:
- Calling a function:
    ```python
    await robot.<function_name>(<args> ...)
    ```
- Defining a function which calls a robot function:
    ```python
    async def my_function(<args> ...):
        await robot.<function_name>(<args> ...)
    ```

A link to the full iCreate interface documentation can be found [here](https://python.irobot.com/assets/doc/sdk_commands.pdf).