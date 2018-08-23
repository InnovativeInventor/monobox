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
import sys


@click.version_option(prog_name="monobox")
@click.group(invoke_without_command=True,context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
@click.pass_context
def cli(ctx):
    """
    A uniform flexible environment for coding, testing, and deploying using Docker.

    See https://github.com/InnovativeInventor/monobox for more
    """
    if ctx.invoked_subcommand is None:
        ctx.invoke(bash)
    elif ctx.invoked_subcommand == "cmd":
        if len(sys.argv) <= 2:
            raise click.UsageError("Exec requries at least another argument")
        else:
            cmd()
    # else:
    #     print(ctx.invoked_subcommand)


def extra_args():
    if len(sys.argv) <=2:
        return None

    exec_cmd = sys.argv[2:] # Should try to use click instead of sys.argv
    # exec_cmd = ' '.join(str(i) for i in cmd_list)
        
    return exec_cmd


@click.option('--verbose', is_flag=True)
@cli.command(help="Runs whatever is specified", context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
def cmd(verbose):
    args = extra_args()
    if verbose:
        print(' '.join(str(i) for i in args))

    run(args)


@click.option('--verbose', is_flag=True)
@cli.command(help="Runs bash when starting up (default)", context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
def bash(verbose):
    args = ["bash"] + extra_args()
    if verbose:
        print(' '.join(str(i) for i in args))

    run(args)


@click.option('--verbose', is_flag=True)
@cli.command(help="Runs sh when starting up instead of bash", context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
def sh(verbose):
    args = ["sh"] + extra_args()
    if verbose:
        print(' '.join(str(i) for i in args))
    
    run(args)


@click.option('--verbose', is_flag=True)
@cli.command(help="Runs the python interperter instead of bash", context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
def python(verbose):
    args = ["python3"] + extra_args()
    if verbose:
        print(' '.join(str(i) for i in args))

    run(args)


@cli.command(help="Starts the container using your defaults", context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
def default():
    # This is for specifing things like CMD ["bash"] in your Monofile or Dockerfile
    run([])


@cli.command(help="Deploys your application using your Dockerfile")
def deploy():
    project_tag = os.path.split(os.getcwd())[1].lower() + ":deploy"
    workdir = combine(['Dockerfile'])

    client = docker.from_env()

    # Copies instead of mounting
    with open('.monobox', 'a') as dockerfile:
        dockerfile.write("COPY . " + workdir)

    # Builds
    with open('.monobox', 'rb') as dockerfile:
        client.images.build(fileobj=dockerfile, pull=True, tag=project_tag)


    docker_command = ["docker", "run", "-d", "--restart", "unless-stopped", "-w="+workdir]
    port_command = expose_ports()
    docker_command.extend(port_command)
    docker_command.append(project_tag)

    subprocess.call(docker_command)

    # subprocess.call(["docker", "run", "-d", "--restart", "unless-stopped", "-w="+workdir, "-v", os.getcwd()+":"+workdir, project_tag])
    print("Deployed! Run 'docker ps' to monitor the status.")


@cli.command(help="Builds the docker image")
def build():
    project_tag = os.path.split(os.getcwd())[1].lower()
    combine(['Dockerfile', 'Monofile']) # No need for workdir

    client = docker.from_env()

    # Builds
    with open('.monobox', 'rb') as dockerfile:
        client.images.build(fileobj=dockerfile, pull=True, tag=project_tag)

    print("Built as " + project_tag)

def run(command):
    project_tag = os.path.split(os.getcwd())[1].lower() + ":devel"
    workdir = combine(['Dockerfile', 'Monofile'])

    client = docker.from_env()

    # Builds
    with open('.monobox', 'rb') as dockerfile:
        client.images.build(fileobj=dockerfile, pull=True, tag=project_tag)

    docker_command = ["docker", "run", "--rm", "-w="+workdir, "-v", os.getcwd()+":"+workdir, "-it"]

    port_command = expose_ports()
    docker_command.extend(port_command)
    docker_command.append(project_tag)

    if command is not "" and check_command() is False:  # Will run command only if it is specified and if CMD is not used
        docker_command.extend(command)

    subprocess.call(docker_command)
    

def check_command():
    with open('.monobox', 'r') as monobox:
        for lines in monobox:
            if lines.partition(' ')[0] == "CMD" or lines.partition(' ')[0] == "ENTRYPOINT":
                return True
    return False


def expose_ports():
    ports = []
    with open('.monobox') as monobox:
        for lines in monobox:
            if lines.partition(' ')[0] == "EXPOSE":
                port_setting = lines.partition(' ')[2].rstrip()
                ports.append("-p")

                port_number = port_setting.partition(':')[0].rstrip()
                try:
                    internal_port_number = port_setting.partition(':')[3].rstrip()
                except IndexError:
                    internal_port_number = port_number

                # print("EXPOSE detected, automatically exposing " + port_number + ":" + internal_port_number)  # Debug
                ports.append(port_number+":"+internal_port_number)
    return ports


def combine(filenames):
    project_name = os.path.split(os.getcwd())[1]
    with open('.monobox', 'w') as monofile:
        for fname in filenames:
            if os.path.isfile(fname):
                with open(fname) as infile:
                    for line in infile:
                        if line.partition(' ')[0] == "MONOBOX":
                            lines_to_write = monocommand(line)
                            monofile.writelines(lines_to_write)
                        elif line.partition(' ')[0] == "WORKDIR":
                            monofile.write(line)
                            workdir = line
                        else:
                            monofile.write(line)
            else:
                print("Warning: " + fname + " does not exist!")

        try:
            if not workdir:
                workdir = "/"+project_name
            monofile.write('ENV PATH=\"' + workdir + ':${PATH}\"')
            return workdir
        except NameError:
            monofile.write('ENV PATH=\"/' + project_name + ':${PATH}\"')
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
        if "." in item:  # Can add your own boxes by using the url. Box names should not have periods in them
            print("Fetching remote box @" + item)
            boxfile = req.get(item)
        else:
            boxfile = req.get('https://raw.githubusercontent.com/InnovativeInventor/boxes/master/boxes/'+item+'/Monofile')
        boxfile.raise_for_status()
    except req.HTTPError or req.URLError:
        try:
            boxfile = req.get('https://boxes.homelabs.space/boxes/'+item+'/Monofile')
            boxfile.raise_for_status()
        except req.HTTPError or req.URLError:
            print("Monobox fetch error! The box you used does not exist")

    for each_line in io.StringIO(boxfile.content.decode('utf-8')):
        if each_line.partition(' ')[0] == "MONOBOX":
            lines = lines + monocommand(each_line)
        else:
            lines.append(each_line)

    return lines


if __name__ == "__main__":
    cli()
