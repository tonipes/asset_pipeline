import logging as logger
import json
import yaml

from .action import all_action_types

class Config(object):
    def __init__(self, data, platform="unknown"):
        self.actions = data["actions"]

        self.globals = data["globals"]["default"]

        if platform in data["globals"]:
            dict.update(self.globals, data["globals"][platform])

def make_action_constructor(T):
    return lambda loader, node: T(**loader.construct_mapping(node, deep=True))

def register_constructors():
    from assetc.action import all_action_types
    for T in all_action_types:
        yaml.add_constructor(
            "!{}".format(T.name), 
            make_action_constructor(T), 
            Loader=yaml.Loader
        )

def load_config(path, platform):
    import yaml
    from yaml import load, Loader

    register_constructors()

    with open(path) as config_file:
        res = load(config_file.read(), Loader=Loader)
        config = Config(res, platform)

    return config
