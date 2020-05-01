import glob
import os
import fnmatch
import datetime
import logging
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor, wait

from . import util

CACHE_EXT = ".cache"

class Builder(object):
    def __init__(self, source_folder, target_folder, cache_folder, staging_folder, config):
        self.source_folder = source_folder
        self.target_folder = target_folder
        self.cache_folder = cache_folder
        self.staging_folder = staging_folder
        self.config = config
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

    # def run_action(self, files, action, main_subs, source_folder, verbose=False):
    #     processed_files = []
        
    #     for f in files:
    #         # source_folder = self.source_folder if source == "source" else self.staging_folder
    #         target_folder = self.target_folder if action.target == "target" else self.staging_folder

    #         file_subs = util.build_substitutes(f, source_folder, target_folder)
            
    #         subs = {**self.config.globals, **main_subs, **file_subs}
            
    #         util.mkdir(subs["target_filepath_dir"])

    #         result = action.run(subs, verbose)
    #         if result:
    #             processed_files.append(f)

    #     return processed_files

    def run_action(self, f, action, main_subs, source_folder, verbose=False):
        processed_files = []
        
        # source_folder = self.source_folder if source == "source" else self.staging_folder
        target_folder = self.target_folder if action.target == "target" else self.staging_folder

        file_subs = util.build_substitutes(f, source_folder, target_folder, self.staging_folder)
        
        subs = {**self.config.globals, **main_subs, **file_subs}
        
        util.mkdir(subs["target_filepath_dir"])
        util.mkdir(subs["staging_filepath_dir"])

        return action.run(subs, verbose)

    def post_build(self, verbose=False):
        for action in self.config.post_build_actions:
            action.run(self.main_subs, verbose)

    def build(self, force=False, categories=None, verbose=False):
        list_of_outputs = []
        list_of_processed_files = []

        executor = ThreadPoolExecutor()

        # From source folder
        process = []
        for action_idx, files in self.get_grouped_files(self.source_folder).items():
            action = self.config.actions[action_idx]
            if not categories or action.category in categories:
                filtered_files = [f for f in files if self.need_update(f, action)] if not force else files
                
                for f in filtered_files:
                    process.append([f, 
                        executor.submit(self.run_action, f, action, self.main_subs, self.source_folder, verbose)
                    ])

        files = [x[0] for x in process]
        futus = [x[1] for x in process]
        
        wait(futus)

        # Update process time
        for f, futu in process:
            if futu.result():
                self.write_cached_mtime(f)

        process.clear()

        # From staging folder
        for action_idx, files in self.get_grouped_files(self.staging_folder).items():
            action = self.config.actions[action_idx]
            if not categories or action.category in categories:
                for f in files:
                    process.append([f, 
                        executor.submit(self.run_action, f, action, self.main_subs, self.staging_folder, verbose)
                    ])

        wait([x[1] for x in process])


        return list_of_outputs
