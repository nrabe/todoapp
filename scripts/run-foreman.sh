#!/bin/sh

DIR="$( cd "$( dirname $( dirname "${BASH_SOURCE[0]}" ))" && pwd )"
cd $DIR

source venv/bin/activate

PORT=8600 foreman start -c web=2
