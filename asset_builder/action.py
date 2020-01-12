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
        self.globs = kwargs["globs"]
        self.desc = kwargs["desc"]

    def execute(self, **substitutes):
        return []

    def run(self, inputs, input_root_folder, output_root_folder, temp_root_folder):
        outputs = []
        rel_inputs = [os.path.join(input_root_folder, i) for i in inputs]
        
        for i in rel_inputs:
            substitutions = build_substitutes(i, input_root_folder, output_root_folder, temp_root_folder)
            mkdir(substitutions["output_local_folder"]) # Make sure that output path is created
            
            outputs += self.execute(**substitutions)

        return outputs
