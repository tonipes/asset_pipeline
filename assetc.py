#!/usr/bin/env python3

import sys
import os
import argparse
import logging
import logging as logger
import shutil
import zipfile
import yaml

from time import perf_counter

from depfile import gen_depfile

from assetc import Config, Builder

def make_action_constructor(T):
    return lambda loader, node: T(**loader.construct_mapping(node, deep=True))

def register_constructors():
    from assetc.action import all_action_types
    for T in all_action_types:
        yaml.add_constructor(
            "!{}".format(T.name), 
            make_action_constructor(T), 
            Loader=yaml.Loader
        )

def load_config(path, platform):
    import yaml
    from yaml import load, Loader

    register_constructors()

    with open(path) as config_file:
        res = load(config_file.read(), Loader=Loader)
        config = Config(res, platform)

    return config

def make_archive(base_name, root_dir):
    save_cwd = os.getcwd()
    
    base_name = os.path.abspath(base_name)

    os.chdir(root_dir)

    base_dir = os.curdir

    zip_filename = base_name
    archive_dir = os.path.dirname(base_name)
    os.makedirs(archive_dir, exist_ok=True)

    with zipfile.ZipFile(zip_filename, "w", compression=zipfile.ZIP_STORED) as zf:
        path = os.path.normpath(base_dir)

        for dirpath, dirnames, filenames in os.walk(base_dir):
            for name in filenames:
                path = os.path.normpath(os.path.join(dirpath, name))
                if os.path.isfile(path):
                    zf.write(path, "/" + path)

    os.chdir(save_cwd)

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
    
    pack_file = os.path.join(args.cache, "target.zip")

    if (args.verbose):
        print("source_folder: " + source_folder)
        print("target_folder: " + target_folder)
        print("cache_folder: " + cache_folder)
        print("staging_folder: " + staging_folder)

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

