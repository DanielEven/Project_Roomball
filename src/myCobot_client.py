import requests

# calls a command from the myCobot server
# gets the arguments as a list of params and parses them to the correct format
# if the command isn't a command from the myCobot library, set custom to True
def call_cobot_function(ip_addr, port, func_name, *params):
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
