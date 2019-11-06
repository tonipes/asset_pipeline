import subprocess
import os

import logging as logger

from asset_builder import action
from asset_builder import util

class ExternalAction(action.Action):
    name = "external"

    def __init__(self, **kwargs):
        self.command = kwargs["command"]
        self.outputs = kwargs["outputs"]

        del kwargs["command"]
        del kwargs["outputs"]

        action.Action.__init__(self, **kwargs)

    def execute(self, **substitutes):
        util.mkdir(os.path.dirname(substitutes["output_filepath"]))

        cmd_subs = util.substitute(self.command.copy(), **substitutes)
        proc = subprocess.run(cmd_subs)
        
        status = "SUCCESS"
        
        if proc.returncode:
            status = "FAILED"
        
        logger.info(self.desc + ": " + substitutes["input_filepath"] + " : " + status)
        
        res = util.substitute(self.outputs.copy(), **substitutes)
        
        return res
