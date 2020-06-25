#!/usr/bin/env python3

import sys
import os
import argparse
import logging
import logging as logger
import shutil
import yaml

from time import perf_counter

from depfile import gen_depfile

from assetc import Config, Builder, load_config

if __name__ == "__main__":
    logger.basicConfig(level=logger.INFO,
                        format='%(asctime)s - %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')

    parser = argparse.ArgumentParser(description='assetc')

    parser.add_argument('--input',      type=str,               help="Input")
    parser.add_argument('--output',     type=str,               help="Output")
    parser.add_argument('--cache',      type=str,               help="Cache")
    parser.add_argument('--depfile',    type=str,               help="Depfile")
    parser.add_argument('--platform',   type=str,               help="Platform")
    parser.add_argument('--config',     type=str,               help="Config")
    parser.add_argument('--clean',      action="store_true",    help="Clean")
    parser.add_argument('--build',      action="store_true",    help="Build")
    parser.add_argument('--verbose',    action="store_true",    help="Verbose")

    args = parser.parse_args()
    
    if (args.verbose):
        for arg in vars(args):
            print("{:10}: {}".format(arg, getattr(args, arg)))

    os.makedirs(args.cache, exist_ok=True)
    
    config = load_config(args.config, args.platform)
    
    source_folder = args.input
    target_folder = args.cache

    source_folder   = os.path.normpath(os.path.join(args.input))
    target_folder   = os.path.normpath(os.path.join(args.cache, "target"))
    cache_folder    = os.path.normpath(os.path.join(args.cache, "cache"))
    staging_folder  = os.path.normpath(os.path.join(args.cache, "staging"))
    
    if args.verbose:
        print("source_folder: "     + source_folder)
        print("target_folder: "     + target_folder)
        print("cache_folder: "      + cache_folder)
        print("staging_folder: "    + staging_folder)

    builder = Builder(source_folder, target_folder, cache_folder, staging_folder, config)
    
    if args.clean:
        logger.info("Cleaning output folder")
        shutil.rmtree(cache_folder, ignore_errors=True)
        os.makedirs(cache_folder, exist_ok=True)

    if args.build:
        logger.info("Building assets")

        inputs, updated, outputs = builder.build(True, None, args.verbose)

        depfile = gen_depfile(args.output, [os.path.normpath(os.path.join(source_folder, f)) for f in inputs])
        depfile_path = args.output + '.d'

        with open(depfile_path, 'w') as df:
            df.write(depfile)

        if updated:
            start = perf_counter()

            shutil.rmtree(args.output, ignore_errors=True)   
            shutil.copytree(target_folder, args.output)
            
            end = perf_counter()
        else:
            logger.info("No assets updated")

        logger.info("Done")
