#!/bin/sh

DIR="$( cd "$( dirname $( dirname "${BASH_SOURCE[0]}" ))" && pwd )"
cd $DIR

tar cvzf ~/Dropbox/todoapp1.$(date "+%Y-%m-%d.%H.%M").tgz --exclude=venv/ ../todoapp1/
