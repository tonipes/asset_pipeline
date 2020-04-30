import os
import shutil

import logging as logger

from asset_builder import action
from asset_builder import util

class CopyAction(action.Action):
    name = "copy"

    def execute(self, **substitutes):        
        input_file = substitutes["source_filepath"]
        destination = substitutes["target_filepath"]

        status = False

        try:
            shutil.copy(input_file, destination)
            status = True
        except:
            pass
        
        # logger.info("{:8}: {:8}: {}".format("copy", ("SUCCESS" if status else "FAILED"), substitutes["filepath_relative"]))
        
        return status
