import os
from .util import build_substitutes
from .util import mkdir
from time import perf_counter
import logging as logger

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
        self.target     = kwargs["target"]      if "target"     in kwargs else "target"
        self.globs      = kwargs["globs"]       if "globs"      in kwargs else []
        self.category   = kwargs["category"]    if "category"   in kwargs else None

    def execute(self, **substitutes):
        return True

    def run(self, subs, verbose=False):
        return self.execute(**subs, verbose=verbose)
