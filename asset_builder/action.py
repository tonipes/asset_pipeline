import os
from .util import build_substitutes
from .util import mkdir

all_action_types = set()


class ActionRegistery(type):
    def __new__(cls, clsname, bases, attrs):
        newclass = super(ActionRegistery, cls).__new__(cls, clsname, bases, attrs)
        if bases:
            all_action_types.add(newclass)
        return newclass


class Action(metaclass=ActionRegistery):
    force_build = False

    def __init__(self, **kwargs):
        print(kwargs)
        self.target = kwargs["target"] if "target" in kwargs else "target"
        self.globs = kwargs["globs"]
        self.desc = kwargs["desc"]

    def execute(self, **substitutes):
        return []

    def run(self, inputs, input_root_folder, output_root_folder, temp_root_folder, source = "source"):
        if (source == self.target):
            logger.warn("Action with same source and target!")

        outputs = []
        
        for i in inputs:
            substitutions = build_substitutes(i, input_root_folder, output_root_folder, temp_root_folder, source, self.target)
            mkdir(substitutions["target_filepath_dir"]) # Make sure that output path is created
            
            outputs += self.execute(**substitutions)

        return outputs
