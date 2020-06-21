import logging as logger
import json

from .action import all_action_types

def unpack(l):
    return [i for s in l for i in s]

def action_decoder(obj):
    if 'type' in obj:
        matches = list(filter(lambda t: t.name == obj['type'], all_action_types))

        if not matches:
            logger.error("No action of type " + obj['type'] + " found")
        
        return matches[0](**obj)

    return obj

class Config(object):
    def __init__(self, data, platform="unknown"):
        self.actions = data["actions"]

        self.globals = data["globals"]["default"]

        if platform in data["globals"]:
            dict.update(self.globals, data["globals"][platform])

        self.globs = unpack([action.globs for action in self.actions])
