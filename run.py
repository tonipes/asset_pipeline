#!/usr/bin/env python3

import sys
import os
import time
import argparse
import shutil
import subprocess
import logging
import logging as logger

from asset_builder import Watcher, Reporter, Builder, Config, util

from actions import copy_action
from actions import external_action

# FORMAT = '%(asctime)-15s %(clientip)s %(user)-8s %(message)s'
# logging.basicConfig(format=FORMAT)

def load_config(path):
    config_file = open(path)
    config = Config(config_file.read())
    config_file.close()
    return config

if __name__ == "__main__":
    logger.basicConfig(level=logger.INFO,
                        format='%(asctime)s - %(message)s',
                        # format='%(threadName)-15s : %(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    parser = argparse.ArgumentParser(description='Asset Builder')

    parser.add_argument('-w', '--watch', action="store_true", 
        help="Watch for changes")

    parser.add_argument('-d', '--delay', default=1, type=int, 
        help="Delay for watching")

    parser.add_argument('-a', '--address', default="localhost", type=str, 
        help="Address to report changes")

    # parser.add_argument('-p', '--port', default=6066, type=int, 
    #     help="Port to report builded files to")

    parser.add_argument('-c', '--clean', action="store_true", 
        help="Clean before build")

    parser.add_argument('-b', '--build', action="store_true", 
        help="Do build")

    parser.add_argument('-p', '--post', action="store_true", 
        help="Do post puild")

    parser.add_argument('-C', '--config', required=True,
        help="Config file")

    parser.add_argument('-s', '--source', required=True,
        help="Source folder. Example: ./assets")

    parser.add_argument('-t', '--target', required=True,
        help="Target folder. Example: ./build/assets")

    parser.add_argument('-g', '--categories', required=False, type=str, nargs='+',
        help="Categories to build. Defaults to all")

    parser.add_argument('-f', '--force', required=False, action="store_true", 
        help="Force. Disable cache check")

    parser.add_argument('-v', '--verbose', required=False, action="store_true", 
        help="Verbose")

    parser.add_argument('-o', '--cache',  required=True,
        help="Folder for cache files. \
            These files are used to detect changes in source files \
            and prevent unnecessary build actions \
            Example: ./build/assets/cache")

    parser.add_argument('-m', '--staging',  required=True,
        help="Folder for staging files. \
            Example: ./build/assets/staging")

    args = parser.parse_args()
    
    # print(args.force)
    # exit(0)

    source_folder   = os.path.normpath(os.path.join(".", args.source))
    target_folder   = os.path.normpath(os.path.join(".", args.target))
    cache_folder    = os.path.normpath(os.path.join(".", args.cache))
    staging_folder  = os.path.normpath(os.path.join(".", args.staging))

    config = load_config(args.config)

    config_path = os.path.dirname(args.config)
    config_file = os.path.basename(args.config)
    
    modified = False
    command_ran = False

    builder = Builder(source_folder, target_folder, cache_folder, staging_folder, config)

    shutil.rmtree(staging_folder, ignore_errors=True)
    util.mkdir(staging_folder)

    if args.clean:
        command_ran = True
        logger.info("Cleaning output folder")

        shutil.rmtree(target_folder, ignore_errors=True)
        shutil.rmtree(cache_folder, ignore_errors=True)
        shutil.rmtree(staging_folder, ignore_errors=True)

        util.mkdir(target_folder)
        util.mkdir(cache_folder)

    if args.build:
        command_ran = True
        logger.info("Asset build actions")

        outputs = builder.build(args.force, args.categories, args.verbose)

    if args.post:
        command_ran = True
        logger.info("Post build actions")
        builder.post_build(args.verbose)

    if args.watch:
        command_ran = True
        logger.info("Watching for changes")

        reporter = Reporter(args.address, args.port)
          
        def callback(modified):
            reporter.report(modified)

        watcher = Watcher(builder, callback, args.delay)

        watcher.watch(source_folder)

    if not command_ran:
        logger.info("No commands profided")
    else:
        logger.info("All done")
