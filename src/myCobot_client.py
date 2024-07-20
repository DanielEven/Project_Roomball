import requests


def call_cobot_function(ip_addr, port, func_name, *params):
    '''
    Calls a function from the myCobot server with the given parameters.
    The function gets the arguments as a list of params and parses them to the correct format.
    If the command isn't a command from the myCobot library, set custom to True.

    ip_addr: The IP address of the myCobot server.
    port: The port of the myCobot server.
    func_name: The name of the function to call.
    params: The parameters to pass to the function.
    '''
    url = f"http://{ip_addr}:{port}/call/{func_name}?args="
    for i, param in enumerate(params):
        if type(param) in [tuple, list]:
            url += f"({','.join(str(x) for x in param)})"
        else:
            url += f"{param}"
        if i != len(params) - 1:
            url += ","
    response = requests.get(url)
    response_json = response.json()
    return_val = response_json["result"]
    return return_val
