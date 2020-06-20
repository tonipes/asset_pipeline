import subprocess
import os

from assetc import action
from assetc import util

class ExternalAction(action.Action):
    name = "external"

    def __init__(self, **kwargs):
        self.commands = kwargs["commands"]

        del kwargs["commands"]

        action.Action.__init__(self, **kwargs)

    def execute(self, verbose=False, **substitutes):
        for command in self.commands:
            cmd_subs = util.substitute(command.copy(), **substitutes)

            proc = subprocess.run(cmd_subs, 
                capture_output=True,
                universal_newlines=True
            )

            status = True
            
            if proc.returncode:
                status = False
            
            if (not status) or verbose:
                if len(proc.stdout) > 0: print(proc.stdout)
                if len(proc.stderr) > 0: print(proc.stderr)

        return status
