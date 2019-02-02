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
import json
from shutil import copyfile
from pathlib import Path


@click.version_option(prog_name="monobox")
@click.option('--verbose', is_flag=True)
@click.group(invoke_without_command=True,context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
@click.pass_context
def default(ctx, verbose):
    """
    A uniform flexible environment for coding, testing, and deploying using Docker.

    See https://github.com/InnovativeInventor/monobox for more
    """
    cmd_list = ['cmd', 'start', 'deploy', 'config']
    if ctx.invoked_subcommand in cmd_list:
        if len(sys.argv) <= 2 and not ctx.invoked_subcommand == 'config':
            raise click.UsageError("Exec requries at least another argument")
        else:
            # cmd_obj = ctx.get_command(ctx,ctx.invoked_subcommand)
            # ctx.forward(cmd_obj)# This will allow extra commands to be passed through
            eval(ctx.invoked_subcommand)
    else:
        run([])

def extra_args():
    if len(sys.argv) <=2:
        return []

    exec_cmd = sys.argv[2:] # Should try to use click instead of sys.argv
        
    return exec_cmd


@click.option('--verbose', is_flag=True)
@default.command(help="Runs whatever is specified", context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
def cmd(verbose):
    args = ['cmd'] + extra_args()
    if verbose:
        print(' '.join(str(i) for i in args))
    print(args) 
    run(args)


@click.option('--verbose', is_flag=True)
@default.command(help="Creates a vm with whatever is specified and starts bash", context_settings=dict(ignore_unknown_options=True, allow_extra_args=True))
def start(verbose):
    args = ['start'] + extra_args()

    if verbose:
        print(' '.join(str(i) for i in args))
    
    run(args)


@click.option('--verbose', is_flag=True)
@default.command(help = "Edit config", context_settings=dict(ignore_unknown_options=False, allow_extra_args=True))
def config(verbose):
    sources = fetch_config()
    print(json.dumps(sources, indent=4, sort_keys=True)) 
    
    print("Do you want to add a source? [Y/N]", end=' ')
    response = input()
    if response in ["Y","y","YES","yes"]:
        print('Please input your URL:')
        url = input().rstrip()
        if 'Custom' not in sources:
            sources['Custom'] = {}
        
        if 'boxes' not in sources['Custom']:
            sources['Custom'].update({'boxes': [url]})
        else:
            sources['Custom']['boxes'] += [url] 


    print("Do you want to change the default Monofile and Dockerfile? [Y/N]", end=' ')
    response = input()
    if response in ["Y","y","YES","yes"]:
        print('Please input your URL:')
        url = input().rstrip()
        if 'Custom' not in sources:
            sources['Custom'] = {}
        
        if 'boxes' not in sources['Custom']:
            sources['Custom'].update({'default': url})
        else:
            sources['Custom']['default'] = url
    with open(str(Path.home()) + '/.config/monobox/sources.json', 'w') as outfile:
        json.dump(sources, outfile, indent = 4)

@default.command(help="Deletes Monofile, Dockerfile, and .monobox")
def rm():
    if os.path.exists('Monofile'):
        os.remove('Monofile')
    if os.path.exists('Dockerfile'):
        os.remove('Dockerfile')
    if os.path.exists('.monobox'):
        os.remove('.monobox')


def check_config():
    if not os.path.exists(str(Path.home()) + '/.config/monobox/'):
        os.mkdir(str(Path.home()) + '/.config/monobox/')

    if not os.path.isfile(str(Path.home()) + '/.config/monobox/sources.json'):
        copyfile('sources.json', str(Path.home()) + '/.config/monobox/sources.json')


@default.command(help="Deploys your application using your Dockerfile")
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


@default.command(help="Builds the docker image")
def build():
    project_tag = os.path.split(os.getcwd())[1].lower()
    combine(['Dockerfile', 'Monofile']) # No need for workdir

    client = docker.from_env()

    # Builds
    with open('.monobox', 'rb') as dockerfile:
        client.images.build(dockerfile='.monobox', path=os.getcwd(), pull=True, tag=project_tag)

    print("Built as " + project_tag)


def run(command, verbose = False):
    build_dir = os.getcwd()
    project_tag = os.path.split(build_dir)[1].lower() + ":devel"
    workdir = combine(['Dockerfile', 'Monofile'], cmd=command)

    client = docker.from_env()

    # Builds
    with open('.monobox', 'rb') as dockerfile:
        client.images.build(dockerfile='.monobox', path=build_dir, pull=True, tag=project_tag)

    docker_command = ["docker", "run", "--rm", "-v", build_dir+":"+workdir, "-it"]

    port_command = expose_ports()
    docker_command.extend(port_command)
    docker_command.append(project_tag)

    if command and check_command() is False:  # Will run command only if it is specified and if CMD is not used
        print(command)
        if command[0] == 'cmd':
            command = command[1:]
        elif command[0] == 'start':
            command = ['bash'] # Later on, build a smarter way of doing this 
        else:
            command = [command[0]] # When does this get used?
        docker_command.extend(command)

    if verbose == True:
        print(docker_command)

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

                ports.append(port_number+":"+internal_port_number)
    return ports


def combine(filenames, cmd = None, temp=False):
    """
    This will combine the Monofile and Dockerfile into .monobox. If these files
    do not exist, they will be created.
    """
    source = fetch_config()
    project_name = os.path.split(os.getcwd())[1]

    files = []
    for each_filename in filenames:
        if os.path.isfile(each_filename):
            files.append(each_filename)
        else:
            pass
            # print("Warning: " + fname + " does not exist!")

    with open('.monobox', 'w') as monofile:
        # print("files:" + str(files), len(files))
        if cmd: 
            if cmd[0] == 'cmd':
                cmd = [cmd[1]]

            if cmd[0] == 'start':
                cmd = cmd[1:]

            if len(files) == 0 and not temp:
                # This will only happen if default is triggered or nothing exists (need to test)
                files = fetch_raw(cmd, source, temp=False)
            else: # Should default to not being intrusive
                files = fetch_raw(cmd, source, temp=True)
        workdir = False
        for fname in files:
            with open(fname) as infile:
                for line in infile:
                    if line.partition(' ')[0] == "MONOBOX":
                        lines_to_write = monocommand(line.rstrip(), source)
                        monofile.writelines(lines_to_write)
                    elif line.partition(' ')[0] == "WORKDIR":
                        monofile.write(line)
                        workdir = line
                    else:
                        monofile.write(line)

                    if 'FROM' in line:
                        monofile.write('WORKDIR /' + project_name + '\n')

        if not workdir:
            workdir = "/" + project_name
        
        return workdir


def fetch_raw(cmd, source, temp=True):
    """
    Fetches the default Monofile and Dockerfile given the cmd, source, and temp
    preferences. If temp is True, only .monobox is written to. Otherwise,
    Monobox and Dockerfile are also written to.
    """
    temp = False # Debug
    if 'Custom' in source:
        if 'default' in source['Custom']:
            default = source['Custom']['default']
        else:
            default = source['Official']['default']

        if 'boxes' in source['Custom']:
            boxes = source['Custom']['boxes']
        else:
            boxes = source['Official']['boxes']

    else:
        default = source['Official']['default']
        boxes = source['Official']['boxes']

    if temp:
        monofile = '.monobox'
        dockerfile = '.monobox'
    else:
        monofile = 'Monofile'
        dockerfile = 'Dockerfile'

    with open(dockerfile, 'w+') as new_dockerfile:
        new_dockerfile.write(req.get(default + 'Dockerfile').content.decode('utf-8'))
    
    if cmd == None or len(boxes) == 0:
        with open(monofile, 'a+') as new_monofile:
            new_monofile.write(req.get(default + 'Monofile').content.decode('utf-8'))
    else:
        for each_cmd in cmd:
            for each_box in boxes:
                try:
                    with open(monofile, 'a+') as new_monofile:
                        req_monofile = req.get(each_box+each_cmd+'/Monofile')
                        req_monofile.raise_for_status()
                        new_monofile.write(req_monofile.content.decode('utf-8'))
                except:
                    pass

    if not os.path.isfile(monofile):
        fetch_raw(None)
    if temp:
        return ['.monobox']
    else:
        return ['Dockerfile', 'Monofile']


def monocommand(line, source):
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
            boxes += fetch_box(processed_command, source)
    return boxes


def fetch_box(item, source):
    if 'Custom' in source:
        boxes = source['Custom']['boxes']
    else:
        boxes = source['Official']['boxes']
    
    lines = []
    try:
        if "." in item:  # Can add your own boxes by using the url. Box names should not have periods in them
            print("Fetching remote box @" + item)
            boxfile = req.get(item)
        else:
            for each_source in boxes:
                try:
                    print(each_source + item + '/Monofile')
                    boxfile = req.get(each_source + item + '/Monofile')
                    boxfile.raise_for_status()
                    break
                except:
                    pass
            boxfile.raise_for_status()
    except:
        try:
            boxfile = req.get('https://boxes.homelabs.space/boxes/'+item+'/Monofile')
            boxfile.raise_for_status()
        except req.HTTPError or req.URLError:
            print("Monobox fetch error! The box you used does not exist anywhere.")

    for each_line in io.StringIO(boxfile.content.decode('utf-8')):
        if each_line.partition(' ')[0] == "MONOBOX":
            lines = lines + monocommand(each_line, source)
        else:
            lines.append(each_line)

    return lines


def fetch_config() -> list:
    """
    Fetches the config file (source.json) or creates one if it doesn't exist.
    """
    check_config()

    with open(str(Path.home()) + '/.config/monobox/sources.json') as sources_json:
        sources = json.load(sources_json)
    
    return sources


if __name__ == "__main__":
    default()
