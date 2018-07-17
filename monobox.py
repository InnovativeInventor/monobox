#!/usr/bin/env python3

# Made by Innovative Inventor at https://github.com/innovativeinventor.
# If you like this code, star it on GitHub!
# Contributions are always welcome.

# MIT License
# Copyright (c) 2018 InnovativeInventor

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import docker
import os
import requests as req
import io
import subprocess
import argparse


def run(command):
    project_tag = os.path.split(os.getcwd())[1] + ":devel"
    workdir = combine()

    client = docker.from_env()

    with open('.monobox', 'rb') as dockerfile:
        client.images.build(fileobj=dockerfile, pull=True, tag=project_tag)

    subprocess.call(["docker", "run", "--rm", "-w="+workdir, "-v", os.getcwd()+":"+workdir, "-it", project_tag, command])


def combine():
    project_name = os.path.split(os.getcwd())[1]
    filenames = ['Dockerfile', 'Monofile']
    with open('.monobox', 'w') as outfile:
        for fname in filenames:
            # Check if file exists here
            with open(fname) as infile:
                for line in infile:
                    if line.partition(' ')[0] == "MONOBOX":
                        outfile.writelines(monocommand(line))
                    elif line.partition(' ')[0] == "WORKDIR":
                        workdir = line
                    else:
                        outfile.write(line)
    try:
        if not workdir:
            workdir = "/"+project_name
        return workdir
    except NameError:
        return "/"+project_name


def monocommand(line):
    boxes = []

    for boxcommand in line.split(' ')[1:]:
        processed_command = boxcommand.rstrip()
        if os.path.isfile('boxes/'+processed_command+'/Monofile'):
            with open('boxes/'+processed_command+'/Monofile') as infile:
                for infile_line in infile:
                    if infile_line.partition(' ')[0] == "MONOBOX":
                        boxes = boxes + monocommand(infile_line)
                    else:
                        boxes.append(infile_line)
        else:
            boxes = boxes + fetch_box(processed_command)
    return boxes


def fetch_box(item):
    lines = []
    try:
        if "." in item:
            boxfile = req.get(item)
        else:
            boxfile = req.get('https://raw.githubusercontent.com/InnovativeInventor/monobox/master/boxes/'+item+'/Monofile')
        boxfile.raise_for_status()
    except req.HTTPError:
        print("MONOBOX fetch failed!: HTTPError")  # In the future, silently log this
        return
    except req.URLError:
        print("MONOBOX fetch failed!: URLError")  # In the future, silently log this
        return

    for each_line in io.StringIO(boxfile.content.decode('utf-8')):
        if each_line.partition(' ')[0] == "MONOBOX":
            lines = lines + monocommand(each_line)
        else:
            lines.append(each_line)

    return lines


def arguments():
    parser = argparse.ArgumentParser(description='A uniform flexible environment for coding, testing, and deploying using Docker')
    parser.add_argument("--python", "-p", help="Runs the python interperter instead of bash (default=bash)", action='store_true')
    args = parser.parse_args()
    return args


if __name__ == "__main__":
    args = arguments()
    if args.python:
        run("python")
    else:
        run("bash")
