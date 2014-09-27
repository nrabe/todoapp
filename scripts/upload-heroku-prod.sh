#!/bin/sh

# with this two lines we can disable the automatic
# collecstatic and upload process
# heroku labs:enable user-env-compile
# heroku config:set DISABLE_COLLECTSTATIC=1

DIR="$( cd "$( dirname "${0}" )" && pwd )"
cd "$(dirname $DIR)"
pwd


heroku releases --app xxxxxxx
echo "----------------- PRODUCTION! MAKE SURE THERE ARE NO CHANGES HERE:"
git status
echo "----------------- PRODUCTION! "
read -r -p "Are you sure? [y/N] (deploying: PRODUCTION! $1) " response
case $response in
    [yY][eE][sS]|[yY])
        echo "pushing to heroku"
        git push heroku master -v
        ;;
esac

