#!/bin/sh

DIR="$( cd "$( dirname "${0}" )" && pwd )"
cd "$(dirname $DIR)"

heroku releases --app dev-todoapp1
echo "----------------- MAKE SURE THERE ARE NO CHANGES HERE:"
git status
echo "-----------------"
read -r -p "Are you sure? [y/N] (deploying: $1) " response
case $response in
    [yY][eE][sS]|[yY])
        git push heroku master -v
        ;;
esac
