import requests
import json

def call_cobot_function(ip_addr, port, func_name, *params, custom=False):
    url = f"http://{ip_addr}:{port}/call{"custom" if custom else ""}/{func_name}?args="
    for i, param in enumerate(params):
        if type(param) == tuple:
            url += f"({','.join(str(x) for x in param)})"
        else:
            url += f"{param}"
        if i != len(params) - 1:
            url += ","
    response = requests.get(url)
    response_json = json.loads(response.get_data().decode())
    return_val = response_json["result"]
    print(return_val)
    return requests.get(url)