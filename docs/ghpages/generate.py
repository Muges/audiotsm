#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Generate example page for github pages.
"""

import os
import re
from distutils.dir_util import copy_tree
from docutils.core import publish_parts
from jinja2 import Environment, FileSystemLoader, Markup
import sass

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(SCRIPT_DIR, "..", "..")

ASSETS_DIR = os.path.join(SCRIPT_DIR, "assets")
TEMPLATES_DIR = os.path.join(SCRIPT_DIR, "templates")
CREDITS_PATH = os.path.join(ROOT, "tests", "integration", "data", "README.rst")
DESTINATION_DIR = os.path.join(ROOT, "build", "ghpages")
EXAMPLES_DIR = os.path.join(DESTINATION_DIR, "examples")

CSS_FILE = os.path.join(SCRIPT_DIR, "scss", "audiotsm.scss")

ENVIRONMENT = Environment(
    loader=FileSystemLoader(TEMPLATES_DIR),
    autoescape=True, trim_blocks=False)

SPEED_DIR_RE = re.compile(r'speed-([\d\.]+)')
FILE_RE = re.compile(r'(.+)_([^_]+)\.wav')

METHOD_NAME = {
    'ola': 'OLA',
    'wsola': 'WSOLA'
}
METHOD_SORT = ['ola', 'wsola']


def get_examples():
    speeds = set()
    methods = set()
    files = {}

    for speed_dir in os.listdir(EXAMPLES_DIR):
        match = SPEED_DIR_RE.match(speed_dir)
        if match:
            speed = match.group(1)
            speeds.add(speed)
            files[speed] = {}
        elif speed_dir == 'orig':
            speed = 'orig'
            files[speed] = {}
        else:
            print('invalid speed directory "{}"'.format(speed_dir))
            continue

        speed_dir = os.path.join(EXAMPLES_DIR, speed_dir)
        for root, _, filenames in os.walk(speed_dir):
            for filename in filenames:
                fullpath = os.path.join(root, filename)
                path = os.path.relpath(fullpath, DESTINATION_DIR)
                name = os.path.relpath(fullpath, speed_dir)

                if speed == 'orig':
                    name = os.path.splitext(name)[0]
                    files[speed][name] = path
                else:
                    match = FILE_RE.match(name)
                    if match:
                        name = match.group(1)
                        method = match.group(2)
                        methods.add(method)
                        if name not in files[speed]:
                            files[speed][name] = {}
                        files[speed][name][method] = path
                    else:
                        print('invalid example file "{}"'.format(filename))

    return {
        'speeds': sorted(speeds, key=float),
        'methods': [
            (method, METHOD_NAME[method])
            for method in sorted(methods, key=METHOD_SORT.index)
        ],
        'files': files
    }


def generate_css():
    """Generate css stylesheet."""
    css = sass.compile(filename=CSS_FILE)

    css_dir = os.path.join(DESTINATION_DIR, "css")
    if not os.path.isdir(css_dir):
        os.makedirs(css_dir)

    filename = os.path.join(css_dir, "audiotsm.css")
    with open(filename, 'w') as fileobj:
        fileobj.write(css)


def generate_index():
    """Generate index.html."""
    context = get_examples()

    with open(CREDITS_PATH) as fileobj:
        context['credits'] = Markup(
            publish_parts(fileobj.read(), writer_name='html')['fragment'])

    filename = os.path.join(DESTINATION_DIR, 'index.html')
    with open(filename, 'w') as fileobj:
        template = ENVIRONMENT.get_template('index.html')
        html = template.render(context)
        fileobj.write(html)


def main():
    """Generate github pages."""
    # Copy assets
    copy_tree(ASSETS_DIR, DESTINATION_DIR)

    generate_css()
    generate_index()


if __name__ == "__main__":
    main()
