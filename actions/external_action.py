import subprocess
import os


from asset_builder import action
from asset_builder import util

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
                print(proc.stdout)
                print(proc.stderr)
        
        # if "filepath_relative" in substitutes:
        #     logger.info("{:8}: {:8}: {}".format(self.name, ("SUCCESS" if status else "FAILED"), substitutes["filepath_relative"]))
        # else:
        #     logger.info("{:8}: {:8}".format(self.name, ("SUCCESS" if status else "FAILED")))

        # logger.info(self.name + ": " + substitutes["filepath_relative"] + " : " + ("SUCCESS" if status else "FAILED"))

        return status
