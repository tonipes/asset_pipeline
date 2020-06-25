import glob
import os
import fnmatch
import datetime
import logging
import logging as logger
from time import perf_counter

from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, wait

from . import util

CACHE_EXT = ".cache"
LOG_FORMAT = "{:8} {:8.3f}s {:10} {}"

class Builder(object):
    def __init__(self, source_folder, target_folder, cache_folder, staging_folder, config):
        self.source_folder  = source_folder
        self.target_folder  = target_folder
        self.cache_folder   = cache_folder
        self.staging_folder = staging_folder
        self.config         = config
        
        self.main_subs = {**self.config.globals, **util.build_main_substitutions(self.source_folder, self.target_folder, self.staging_folder)}

    def get_current_mtime(self, filepath):
        return os.path.getmtime(os.path.join(self.source_folder, filepath))

    def get_cache_file(self, filepath):
        return os.path.normpath(os.path.join(self.cache_folder, filepath)) + CACHE_EXT

    def get_cached_mtime(self, filepath):
        cache_file = self.get_cache_file(filepath)

        if os.path.isfile(cache_file):
            try:
                with open(cache_file, "r") as f:
                    return float(f.read())
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

        for action_key, action in self.config.actions.items():
            for g in action.globs:
                for source_file in source_files:
                    relative = os.path.relpath(source_file, folder)
                    if fnmatch.fnmatch(relative, g):
                        grouped[action_key].append(relative)

        return grouped

    def run_action(self, f, action_key, action, main_subs, source_folder, verbose=False):
        processed_files = []
        
        target_folder = self.target_folder if action.target == "target" else self.staging_folder

        file_subs = util.build_substitutes(f, source_folder, target_folder, self.staging_folder)
        
        subs = {**self.config.globals, **main_subs, **file_subs}
        
        util.mkdir(subs["target_filepath_dir"])
        util.mkdir(subs["staging_filepath_dir"])

        start = perf_counter()
        status = action.run(subs, verbose)
        end = perf_counter()

        filename = subs["filepath_relative"] if "filepath_relative" in subs else action_key
        logger.info(LOG_FORMAT.format(("SUCCESS" if status else "FAILED"), end-start, action_key, filename))

        return status

    def build(self, force=False, categories=None, verbose=False):
        list_of_inputs = []
        list_of_outputs = []
        list_of_processed_files = []

        executor = ThreadPoolExecutor()
        
        updated = False

        # From source folder
        process = []
        for action_key, files in self.get_grouped_files(self.source_folder).items():
            list_of_inputs += files
            action = self.config.actions[action_key]
            if not categories or action.category in categories:
                for f in files:
                    if self.need_update(f, action):
                        updated = True
                        process.append([f, 
                            executor.submit(self.run_action, f, action_key, action, self.main_subs, self.source_folder, verbose)
                        ])

        files = [x[0] for x in process]
        futus = [x[1] for x in process]
        
        wait(futus)

        # Update process time
        for f, futu in process:
            if futu.result():
                self.write_cached_mtime(f)

        process.clear()

        wait([x[1] for x in process])

        return list_of_inputs, updated, list_of_outputs
