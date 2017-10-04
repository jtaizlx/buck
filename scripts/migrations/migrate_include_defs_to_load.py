#!/usr/bin/env python3

import argparse
import logging
import subprocess
import os
import json
import tempfile
import pathlib

from typing import Dict, List

MY_DIR = os.path.dirname(os.path.realpath(__file__))


def load_cell_roots(repo_dir: str) -> Dict[str, str]:
    """Returns a map with cell keys and their roots as values."""
    cell_config = subprocess.check_output(['buck', 'audit', 'cell'], cwd=repo_dir).decode().strip()
    cell_roots = {}
    for config in cell_config.split(os.linesep):
        cell, path = map(lambda s: s.strip(), config.split(':'))
        cell_roots[cell] = path
    logging.debug('Loaded following cell roots: %r' % cell_roots)
    return cell_roots


def load_export_map(repo: str, cell_roots: Dict[str, str], build_file: str):
    """Returns a dictionary with import string keys and all symbols they export as values."""
    cell_root_args = []
    for cell, root in cell_roots.items():
        cell_root_args.extend(['--cell_root', cell + '=' + root])
    return json.loads(subprocess.check_output([
                                                  os.path.join(MY_DIR, 'dump.py'), '--json',
                                                  '--repository', repo] + cell_root_args + [
                                                  'export_map',
                                                  '--use_load_function_import_string_format',
                                                  build_file
                                              ]).decode().strip())


class Buildozer:
    """Represents a buildozer tool."""

    def __init__(self, path: str, repo: str):
        self.path = path
        self.repo = repo

    def run(self, *commands: str) -> None:
        with tempfile.NamedTemporaryFile('w') as commands_file:
            for command in commands:
                commands_file.write(command)
                commands_file.write(os.linesep)
            commands_file.flush()
            try:
                subprocess.check_output([self.path, '-f', commands_file.name], cwd=self.repo)
            except subprocess.CalledProcessError as e:
                if e.returncode != 3:  # return code 3 is returned when there are no changes
                    raise


def add_load_funcs(buildozer: Buildozer, load_funcs: Dict[str, List[str]], package: str) -> None:
    """Add load functions to package."""
    commands = []
    for import_string, symbols in load_funcs.items():
        commands.append(
            'new_load ' + import_string + ' ' + ' '.join(symbols) + '|' + package + ':__pkg__')
    buildozer.run(*commands)


def remove_include_defs(buildozer: Buildozer, package: str) -> None:
    """Remove all include_defs functions from package."""
    buildozer.run('delete|' + package + ':%include_defs')


def fix_unused_loads(buildozer: Buildozer, package: str) -> None:
    """Remove all unused load symbols from package."""
    buildozer.run('fix unusedLoads|' + package + ':__pkg__')


def test_build_file(build_file: str, repo: str):
    """Verify that build file syntax is correct."""
    logging.debug('Testing %s...', build_file)
    subprocess.check_output(['buck', 'audit', 'rules', build_file], cwd=repo)


def main():
    parser = argparse.ArgumentParser(
        description='Migrates usages of include_defs function to load .'
    )
    parser.add_argument('-v', '--verbose', action='store_true',
                        help='Enable verbose diagnostic messages.')
    parser.add_argument('build_file', metavar='FILE', help='Build file path.')
    parser.add_argument('--repository', metavar='DIRECTORY', required='True',
                        help='Repository path.')
    parser.add_argument('--buildozer', metavar='FILE', required=True, help='Buildozer path.')
    parser.add_argument('--test', action='store_true',
                        help='Whether new build file should be tested in the end.')
    args = parser.parse_args()
    logging_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(level=logging_level, format=(
        '%(asctime)s [%(levelname)s][%(filename)s:%(lineno)d] %(message)s'
    ))
    cell_roots = load_cell_roots(args.repository)
    buildozer = Buildozer(args.buildozer, args.repository)
    package_dir = os.path.dirname(args.build_file)
    package = str(pathlib.Path(package_dir).relative_to(args.repository))
    load_funcs = load_export_map(args.repository, cell_roots, args.build_file)
    logging.debug(load_funcs)
    add_load_funcs(buildozer, load_funcs, package)
    remove_include_defs(buildozer, package)
    fix_unused_loads(buildozer, package)
    if args.test:
        test_build_file(args.build_file, args.repository)


if __name__ == '__main__':
    main()
