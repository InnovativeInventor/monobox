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
import shutil
import click
import os
import requests as req
import io
import subprocess
from pathlib import Path
import configparser

@click.group()
@click.pass_context
def cli(ctx):
	"""
	A uniform flexible environment for coding, testing, and deploying using Docker
	"""

@click.command()
@click.pass_context
def main(ctx):
	run("bash")
	# client.containers.run(project_tag, 'echo "test"', name=project_name, stdout=True, stderr=True, tty=True)
	# client.containers.remove()
	# client.attach()

def run(command):
	home = os.getenv("HOME")
	project_tag = os.path.split(os.getcwd())[1] + ":devel"
	project_name = os.path.split(os.getcwd())[1]+"-devel"
	workdir = combine()

	client = docker.from_env()

	with open('mono/Dockerfile', 'rb') as dockerfile:
		client.images.build(fileobj=dockerfile, pull=True, tag=project_tag)

	subprocess.call(["docker","run","--rm","-w="+workdir,"-v",os.getcwd()+":"+workdir,"-it",project_tag])

def combine():
	project_name = os.path.split(os.getcwd())[1]
	monocommands = []
	filenames = ['Dockerfile', 'Monofile']
	with open('mono/Dockerfile', 'w') as outfile:
		for fname in filenames:
			# Check if file exists here
			with open(fname) as infile:
				for line in infile:
					if line.partition(' ')[0] == "MONOBOX":
						outfile.writelines(monocommand(line))
					elif line.partition(' ')[0] == "WORKDIR":
						workdir=line
					else:
						outfile.write(line)
	try:
		if not workdir:
			workdir = "/"+project_name
		return workdir
	except:
		return "/"+project_name

def monocommand(line):
	boxes = []

	for boxcommand in line.split(' ')[1:]:
		processed_command = boxcommand.rstrip()
		# try:
		if os.path.isfile('boxes/'+processed_command+'/Monofile'):
			with open('boxes/'+processed_command+'/Monofile') as infile:
				for infile_line in infile:
					if infile_line.partition(' ')[0] == "MONOBOX":
						boxes = boxes + monocommand(infile_line)
					else:
						boxes.append(infile_line)
		else:
			boxes = boxes + fetch_box(processed_command)
		# except:
		# 	print("MONOBOX command failed!") # In the future, silently log this

	return boxes

def fetch_box(item):
	lines = []
	try:
		if "." in item:
			boxfile = req.get(item)
		else:
			boxfile = req.get('https://raw.githubusercontent.com/InnovativeInventor/editable-twitter/master/monofile/boxes/'+item+'/Monofile')
		boxfile.raise_for_status()
	except:
		print("MONOBOX fetch failed!") # In the future, silently log this
		return

	for each_line in io.StringIO(boxfile.content.decode('utf-8')):
		if each_line.partition(' ')[0] == "MONOBOX":
			lines = lines + monocommand(each_line)
		else:
			lines.append(each_line)

	return lines

# @cli.command()
# @click.pass_context
# def deploy():
# 	project_tag = os.path.split(os.getcwd())[1] + ":deploy"
# 	with open('Dockerfile', 'rb') as dockerfile:
# 		client.images.build(fileobj=dockerfile, pull=True, tag=project_tag)
#
# 	subprocess.call(["docker","run","--rm","-w="+workdir,"-v",os.getcwd()+":"+workdir,"-it",project_tag])
# 	print("Deployed!")

@cli.command()
@click.pass_context
def python():
	run(python3)

if __name__ == "__main__":
	main()
