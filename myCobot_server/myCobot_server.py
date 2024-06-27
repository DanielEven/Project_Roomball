from flask import Flask, request, jsonify
from pymycobot.mycobot import MyCobot
import inspect
import re
import argparse
import logging
import serial
import termios
import json

DEFAULT_IP = '192.168.0.134'
DEFAULT_PORT = 12355

app = Flask(__name__)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Start Serial communication
try:
    ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
except serial.SerialException:
    logger.error("Failed to open serial port")
    ser = None

def parse_arg(arg: str):
    """
    Parse a single argument from string format to the appropriate type.
    Supports int, float, tuple of int/float, and str.
    """
    if arg.startswith('(') and arg.endswith(')'):
        elements = arg[1:-1].split(",")
        return tuple(float(x) if '.' in x else int(x) for x in elements)
    elif arg.isdigit():
        return int(arg)
    elif arg.replace('.', '', 1).isdigit():
        return float(arg)
    else:
        return arg


def parse_args(args: str):
    """
    Parse a comma-separated string of arguments into a list of parsed arguments.
    """
    args = re.split(r',(?![^()]*\))', args)
    return [parse_arg(arg) for arg in args]


@app.route('/call/<function_name>', methods=['GET'])
def call_function(function_name):
    """
    Endpoint to call a function of the MyCobot class by name with optional arguments.
    """
    func = getattr(MyCobot, function_name, None)
    if func is None or not inspect.isroutine(func):
        return jsonify({'error': f'No such function: {function_name}'}), 404

    args = request.args.get('args', '')
    try:
        parsed_args = parse_args(args)
        logger.info(f"Calling function {function_name} with arguments {parsed_args}")
        result = func(mc, *parsed_args)
        return jsonify({'result': result})
    except Exception as e:
        logger.error(f"Error calling function {function_name}: {e}")
        return jsonify({'error': str(e)}), 400


@app.route('/call_custom/get_ultrasonic_sensors', methods=['GET'])
def get_ultrasonic_sensors():
    logger.info(f"Calling custom function get_ultrasonic_sensors with arguments []")
    global ser
    if ser is None:
        try:
            ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
        except serial.SerialException:
            logger.error("Failed to open serial port")
            return jsonify({'error': 'Failed to open serial port'}), 400
    try:
        ser.reset_input_buffer()
        line = ser.readline().decode()
        while not line.startswith("Distances:"):
            line = ser.readline().decode()
        return jsonify({'result': [float(x) for x in line.split()[1:]]})
    except termios.error:
        ser = None
        logger.error("Failed to open serial port")
        return jsonify({'error': 'Failed to open serial port'}), 400


@app.route('/call_custom/wait_for_obstacle', methods=['GET'])
def wait_for_obstacle():
    global ser
    args = request.args.get('args', '')
    parsed_args = parse_args(args)
    distance = parsed_args[0]
    logger.info(f"Calling custom function wait_for_obstacle with arguments {parsed_args}")

    if ser is None:
        try:
            ser = serial.Serial('/dev/ttyUSB0', 9600, timeout=1)
        except serial.SerialException:
            logger.error("Failed to open serial port")
            return jsonify({'error': 'Failed to open serial port'}), 400
    try:
        ser.reset_input_buffer()
        line = ser.readline().decode()
        while not line.startswith("Distances:"):
            line = ser.readline().decode()
        sensor_values =  [float(x) for x in line.split()[1:]]
        while min(sensor_values) > distance:
            line = ser.readline().decode()
            while not line.startswith("Distances:"):
                line = ser.readline().decode()
            sensor_values =  [float(x) for x in line.split()[1:]]
        return jsonify({'result': [float(x) for x in line.split()[1:]]})
    except termios.error:
        ser = None
        logger.error("Failed to open serial port")
        return jsonify({'error': 'Failed to open serial port'}), 400


@app.route('/call_custom/close_server', methods=['GET'])
def close_server():
    """
    Close the flask server and disconnect the myCobot instance.
    """
    try:
        mc.close()
    except Exception as e:
        logger.error(f"Error closing myCobot: {e}")
        return jsonify({'error': str(e)}), 500

    exit(0)

def get_arguments():
    """
    Parse command line arguments for the Flask server.
    """
    parser = argparse.ArgumentParser(description='myCobot 3 Command Server.🚀🔥')
    parser.add_argument('--host', type=str, help='host ip', default=DEFAULT_IP)
    parser.add_argument('--port', type=int, help='port number', default=DEFAULT_PORT)
    return parser.parse_args()


if __name__ == "__main__":
    args = get_arguments()

    try:
        mc = MyCobot("/dev/ttyAMA0", 1000000)
        logger.info("myCobot initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize myCobot: {e}")
        exit(1)

    app.run(host=args.host, port=args.port)
