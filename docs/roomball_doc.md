# Roomball Programmer Manual

## Algorithm
The robot runs in a loop:
- Locate closest item and go to that item
- Pick the item up
- Return to home
- Put the item in a stack

### locate_closest_item algorithm
This function finds the closest item, and moves toward it, always ending in the same distance and angle from the item.
- The robot spins 90 degrees right, and finds the closest item to the robot. Then spins back to point to that item.
- The robot moves to the item in a loop:
    - Detect distance from the item.
    - Move half that distance.
    - Correct the angle, turn right until middle sensor finds the item again.
    - Continue the loop until the robot is close enough to the item.
- Recognize if the cup is standing or lying down.
    - Spin to the right until left sensor can see the item, then stops.
    - Spin to the left until right sensor can see the item, then stops.
    - Measure the time it took to decide the cup's orientation.
- Move to be at constant distance, and now the pick_up_cup functions can be called.

## Important Constants
`COBOT_IP = "192.168.0.134"` - Default IP for myCobot server\
`COBOT_PORT = 12355` - Default port for myCobot server\
`DETECTION_DISTANCE_THRESHOLD = 60` - The distance in cm that the robot will search for cups, won't find anything further than that.\
`ROTATION_DEGREES = 90` - The amount of degrees to search for cups in. Should be less than 360 in order for the robot to have a place to pile the cups.