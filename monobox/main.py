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
import click


@click.group(invoke_without_command=True)
@click.pass_context
def cli(ctx):
    """
    A uniform flexible environment for coding, testing, and deploying using Docker.

    See https://github.com/InnovativeInventor/monobox for more
    """
    if ctx.invoked_subcommand is None:
        ctx.invoke(bash)


@cli.command(help="Runs bash when starting up")
def bash():
    run("bash")


@cli.command(help="Runs sh when starting up")
def sh():
    run("sh")


@cli.command(help="Runs the python interperter instead of bash")
def python():
    run("python3")


@cli.command(help="Starts the container using your defaults")
def default():
    # This is for specifing things like CMD ["bash"] in your Monofile or Dockerfile
    run("")


@cli.command(help="Deploys your application using your Dockerfile")
def deploy():
    project_tag = os.path.split(os.getcwd())[1] + ":deploy"
    workdir = combine(['Dockerfile'])

    client = docker.from_env()
    with open('.monobox', 'a') as dockerfile:
        dockerfile.write("COPY . " + workdir)

    with open('.monobox', 'rb') as dockerfile:
        client.images.build(fileobj=dockerfile, pull=True, tag=project_tag)

    docker_command = ["docker", "run", "-d", "--restart", "unless-stopped", "-P", "-w="+workdir]
    docker_command.append(project_tag)

    subprocess.call(docker_command)
    print("Deployed! Run 'docker ps' to monitor the status.")


def run(command):
    project_tag = os.path.split(os.getcwd())[1] + ":devel"
    workdir = combine(['Dockerfile', 'Monofile'])

    client = docker.from_env()

    with open('.monobox', 'rb') as dockerfile:
        client.images.build(fileobj=dockerfile, pull=True, tag=project_tag)

    docker_command = ["docker", "run", "--rm", "-w="+workdir, "-P", "-v", os.getcwd()+":"+workdir, "-it"]
    docker_command.append(project_tag)

    if command is not "" and check_command is False:  # Will run command only if it is specified and if CMD is not used
        docker_command.append(command)

    subprocess.call(docker_command)


def check_command():
    with open('.monobox', 'rb') as monobox:
        for lines in monobox:
            if lines.partition(' ')[0] == "CMD":
                return True
    return False


def combine(filenames):
    project_name = os.path.split(os.getcwd())[1]
    with open('.monobox', 'w') as outfile:
        for fname in filenames:
            if os.path.isfile(fname):
                with open(fname) as infile:
                    for line in infile:
                        if line.partition(' ')[0] == "MONOBOX":
                            outfile.writelines(monocommand(line))
                        elif line.partition(' ')[0] == "WORKDIR":
                            workdir = line
                        else:
                            outfile.write(line)
            else:
                print("Error: " + fname + " does not exist!")
                exit(1)
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


if __name__ == "__main__":
    cli()
