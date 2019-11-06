import glob
import os
import fnmatch
import datetime
import logging
from collections import defaultdict

from . import util

CACHE_EXT = ".cache"

class Builder(object):
    def __init__(self, input_folder, output_folder, cache_folder, config):
        self.input_folder = input_folder
        self.output_folder = output_folder
        self.cache_folder = cache_folder
        self.config = config

    def get_current_mtime(self, filepath):
        return os.path.getmtime(os.path.join(self.input_folder, filepath))

    def get_cache_file(self, filepath):
        return os.path.normpath(os.path.join(self.cache_folder, filepath)) + CACHE_EXT

    def get_cached_mtime(self, filepath):
        cache_file = self.get_cache_file(filepath)

        if os.path.isfile(cache_file):
            try:
                with open(cache_file, "r") as f:
                    return float( f.read())
            except ValueError:
                pass

        return None
    
    def need_update(self, f, action):
        if action.force_build: return True

        cached_time = self.get_cached_mtime(f)
        current_time = self.get_current_mtime(f)

        if cached_time:
            return current_time > cached_time
        else:
            return True

    def write_cached_mtime(self, filepath):
        cache_file = self.get_cache_file(filepath)

        util.mkdir(os.path.dirname(cache_file))

        with open(cache_file, "w") as f:
            f.write(str(self.get_current_mtime(filepath)))

    def build(self, input_files):
        grouped = defaultdict(list)

        for i, action in enumerate(self.config.actions):
            for g in action.globs:
                for input_file in input_files:
                    relative = os.path.relpath(input_file, self.input_folder)
                    if fnmatch.fnmatch(relative, g):
                        grouped[i].append(relative)

        list_of_outputs = []

        for action_idx, files in grouped.items():
            action = self.config.actions[action_idx]
            
            filtered_inputs = [f for f in files if self.need_update(f, action)]

            for f in files:
                self.write_cached_mtime(f)
            if filtered_inputs:
                outputs = action.run(filtered_inputs, self.input_folder, self.output_folder)
                list_of_outputs += outputs

        return list_of_outputs
