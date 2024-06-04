from flask import Flask, request, jsonify
from pymycobot.mycobot import MyCobot
import inspect
import re
import argparse

DEFAULT_IP = '192.168.0.134'
DEFAULT_PORT = 12355

app = Flask(__name__)


def parse_arg(arg: str):
    """
    Parse a single argument from string format to the appropriate type.
    Supports int, float, tuple of int/float, and str.
    """
    if arg.startswith('(') and arg.endswith(')'):
        elements = arg[1:-1].split(",")
        if all(element.replace('.', '', 1).isdigit() for element in elements):
            return tuple(float(x) if '.' in x else int(x) for x in elements)
        else:
            return tuple(elements)
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
        result = func(mc, *parsed_args)
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


@app.route('/close_server', methods=['GET'])
def close_server():
    """
    Close the flask server and disconnect the myCobot instance.
    """
    mc.close()
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

    mc = MyCobot("/dev/ttyAMA0", 1000000)

    app.run(host=args.host, port=args.port)
