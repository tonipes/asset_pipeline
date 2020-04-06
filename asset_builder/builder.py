import glob
import os
import fnmatch
import datetime
import logging
from collections import defaultdict

from . import util

CACHE_EXT = ".cache"

class Builder(object):
    def __init__(self, source_folder, target_folder, cache_folder, temp_folder, config):
        self.source_folder = source_folder
        self.target_folder = target_folder
        self.cache_folder = cache_folder
        self.temp_folder = temp_folder
        self.config = config

    def get_current_mtime(self, filepath):
        return os.path.getmtime(os.path.join(self.source_folder, filepath))

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

    def get_grouped_files(self, folder):
        source_files = util.all_files_in(folder)
        grouped = defaultdict(list)

        for i, action in enumerate(self.config.actions):
            for g in action.globs:
                for source_file in source_files:
                    relative = os.path.relpath(source_file, folder)
                    if fnmatch.fnmatch(relative, g):
                        grouped[i].append(relative)

        return grouped

    def build(self):
        list_of_outputs = []
        list_of_processed_files = []

        # From source folder
        for action_idx, files in self.get_grouped_files(self.source_folder).items():
            action = self.config.actions[action_idx]

            filtered_files = [f for f in files if self.need_update(f, action)]

            list_of_processed_files += filtered_files

            if filtered_files:
                outputs = action.run(filtered_files, self.source_folder, self.target_folder, self.temp_folder, "source")
                list_of_outputs += outputs

        for f in list_of_processed_files:
            self.write_cached_mtime(f)

        # From temp folder
        for action_idx, files in self.get_grouped_files(self.temp_folder).items():
            action = self.config.actions[action_idx]
            if files:
                outputs = action.run(files, self.source_folder, self.target_folder, self.temp_folder, "temp")

        return list_of_outputs
