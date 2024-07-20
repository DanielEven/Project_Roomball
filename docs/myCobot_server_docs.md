# myCobot Server Programmer Manual

The server runs on http using the flask library.\
The server gets the function name, and checks if there exists a function with the same name in the `MyCobot` library. If there is, it parses the arguments, and passes them to the function. If the function is a custom function that isn't in the `MyCobot` library, it will run instead.

## Adding Custom Commands
Adding custom commands which don't come with the myCobot library can be useful in cases where fast calculations need to be made as the internet speed might limit them.\
In order to add them, a new function must be created in the `myCobot_server.py` file. The function must be wrapped with the wrapper `@app.route`. The url should be of the form `/call/{function_name}`. The arguments should be received using `request.args.get('args', '')`.\
For examples, look at the functions `get_ultrasonic_sensors`, `wait_for_obstacle`, and `close_server`.\
It is recommended to add the names of the functions that you use and the custom functions that you create to the `ServerCommands` class in `server_commands.py`, as it will help you make sure that you don't get errors caused by calling the wrong url.\
The server and client currently support parameters that are one of the following types: `int`, `float`, `tuple[int]`, `tuple[float]` (if the client receives a `list` then it will send it as a tuple), and `str`. If you need more input types, update the `parse_arg` function in `myCobot_server.py` to unparse the wanted type correctly and update the `call_cobot_function` function in `myCobot_server.py` to parse the wanted type correctly.

## Interfacing with the Arduino
In order to get information from the Arduino, we use the `serial` library.\
To connect more sensors, update the `SENSOR_CNT`, `trigPins` and `echoPins` variables in the Arduino program.\
If you want to use more types of sensors, write an Arduino program that prints their values to Serial, and in the server read those values and use them as wanted.\
If you want to pass information from the server to the arduino, this is probably possible by writing to the serial port from the server and reading it in the Arduino code, but we haven't tested this.