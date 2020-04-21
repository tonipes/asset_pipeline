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
        for command in self.commands:
            cmd_subs = util.substitute(command.copy(), **substitutes)
            proc = subprocess.run(cmd_subs, 
                # capture_output=True,
                universal_newlines=True
            )

            status = True
            
            if proc.returncode:
                status = False
                print(proc.stdout)
                print(proc.stderr)

        logger.info(self.name + ": " + substitutes["filepath_relative"] + " : " + ("SUCCESS" if status else "FAILED"))

        return status
