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

        logger.info("Copying " + input_file + " => " + destination)
        
        shutil.copy(input_file, destination)

        return [substitutes["filepath_relative"]]
