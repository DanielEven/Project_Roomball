import requests

def call_cobot_function(ip_addr, port, func_name, *params, custom=False):
    url = f"http://{ip_addr}:{port}/call{'_custom' if custom else ''}/{func_name}?args="
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
