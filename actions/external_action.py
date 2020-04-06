import subprocess
import os

import logging as logger

from asset_builder import action
from asset_builder import util

class ExternalAction(action.Action):
    name = "external"

    def __init__(self, **kwargs):
        self.commands = kwargs["commands"]

        del kwargs["commands"]

        action.Action.__init__(self, **kwargs)

    def execute(self, **substitutes):
        util.mkdir(substitutes["target_filepath_dir"])

        for command in self.commands:
            cmd_subs = util.substitute(command.copy(), **substitutes)
            proc = subprocess.run(cmd_subs)

            status = "SUCCESS"
            
            if proc.returncode:
                status = "FAILED"

        logger.info(self.desc + ": " + substitutes["filepath_relative"] + " : " + status)

        return []
