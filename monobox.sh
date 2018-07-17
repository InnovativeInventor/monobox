#!/usr/bin/env bash

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

while [[ $# -gt 0 ]];
do
key="$1"

case $key in
    deploy|-d|--deploy)
    deploy=YES
    shift # past argument
    ;;
    install|-i|--install)
    install=YES
    shift # past argument
    ;;
    -h|--help)
    help=YES
    shift # past argument
    ;;
esac;
done

build() {
	docker build . -t ${PWD##*/}
}

help() {
	echo "help"
}

main() {
	build
	name=$(pwd | sed 's#.*/##')

	echo $name

     rm -r mono
     mkdir mono
     cp Dockerfile mono/
     cat Monofile >> mono/Dockerfile
     sed -i '^MONOBOX' mono/Dockerfile

     if [[ "$deploy" == "YES" ]]; then
          container="$name-deploy"
          docker build . -t $name -v ${PWD}:/:ro
          docker run $name --name $container
     elif [[ "$install" == "YES" ]]; then
          curl -fsSL get.docker.com | sh
          exit
     elif [[ "$help" == "YES" ]]; then
          help
     	exit
     else
          container="$name-develop"
          docker build mono -t ${PWD##*/}
          docker run $name --name $container -v ${PWD}:/
     fi

     docker exec -it $container bash
}

main
