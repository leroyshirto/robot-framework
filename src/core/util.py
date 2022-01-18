import json


def load_json_config(config_path: str):
    with open(config_path) as json_file:
        return json.load(json_file)
