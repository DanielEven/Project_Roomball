# myCobot Server Programmer Manual

## Overview

The myCobot server runs on HTTP using the Flask library. It receives function names, checks if corresponding functions exist in the `MyCobot` library, parses arguments, and passes them to the functions. If the function is custom and not part of the `MyCobot` library, the custom function is executed instead.

## Adding Custom Commands

Adding custom commands that are not included in the myCobot library can be useful, especially for performing fast calculations without relying on internet speed. To add custom commands, follow these steps:

1. **Create a New Function**: Define a new function in the `myCobot_server.py` file. Wrap the function with the `@app.route` decorator. The URL should be in the form `/call/{function_name}`.
    ```python
    @app.route('/call/custom_function_name')
    def custom_function_name():
        args = request.args.get('args', '')
        # Function implementation
        pass
    ```

2. **Receive Arguments**: Use `request.args.get('args', '')` to receive arguments for your function.

3. **Refer to Examples**: Look at existing functions such as `get_ultrasonic_sensors`, `wait_for_obstacle`, and `close_server` for examples.

4. **Update `ServerCommands` Class**: Add the names of your functions to the `ServerCommands` class in `server_commands.py`. This helps ensure that you do not encounter errors caused by incorrect URLs.
    ```python
    class ServerCommands:
        ...
        CUSTOM_FUNCTION_NAME = 'custom_function_name'
        ...
    ```

5. **Support Additional Parameter Types**: The server and client currently support `int`, `float`, `tuple[int]`, `tuple[float]`, and `str` parameter types. To add more types, update the `parse_arg` function in `myCobot_server.py` to correctly unparse the desired type and the `call_cobot_function` in `myCobot_client.py` function to parse it.

## Interfacing with the Arduino

To interface with the Arduino and retrieve sensor information, the `serial` library is used.

### Connecting More Sensors

1. **Update Arduino Program** at `arduino/ultrasonic_test.ino`: Modify the `SENSOR_CNT`, `trigPins`, and `echoPins` variables in the Arduino program to connect more sensors.
    ```cpp
    const int SENSOR_CNT = new_value;
    const int trigPins[SENSOR_CNT] = {trig_pin_values};
    const int echoPins[SENSOR_CNT] = {echo_pin_values};
    ```

2. **Add New Sensor Types**: Write an Arduino program that prints sensor values to the Serial monitor. In the server, read these values and use them as needed.

### Passing Information to the Arduino

To pass information from the server to the Arduino, write to the serial port from the server and read it in the Arduino code. Although this has not been tested, it is likely possible.
