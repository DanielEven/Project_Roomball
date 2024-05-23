from flask import Flask, request, jsonify
from pymycobot.mycobot import MyCobot
import inspect
import re

app = Flask(__name__)


def parse_arg(arg: str):
    if arg.startswith('(') and arg.endswith(')'):
        if '.' in arg:
            return tuple(float(x.split()) for x in arg[1:-1].split(","))
        else:
            return tuple(int(x.split()) for x in arg[1:-1].split(","))
    elif arg.isdigit():
        return int(arg)
    elif arg.replace('.', '', 1).isdigit():
        return float(arg)
    else:
        return arg


def parse_args(args):
    args = re.split(r',(?![^()]*\))', args)
    return [parse_arg(arg) for arg in args]


@app.route('/call/<function_name>')
def call_function(function_name):
    func = getattr(MyCobot, function_name, None)
    if func is None or not inspect.isroutine(func):
        return jsonify({'error': f'No such function: {function_name}'}), 404

    args = request.args.get('args', '')
    try:
        result = func(*parse_args(args))
        return jsonify({'result': result})
    except Exception as e:
        return jsonify({'error': str(e)}), 400


if __name__ == "__main__":
    mc = MyCobot("/dev/ttyAMAO", 1000000)
    app.run(host="127.0.0.1", port=12355)
