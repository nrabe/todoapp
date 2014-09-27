#!/bin/sh

DIR="$( cd "$( dirname "${0}" )" && pwd )"
cd "$(dirname $DIR)"

CURRENT_BRANCH=$(git branch | grep \* | cut -d " " -f2)
if [[ "$CURRENT_BRANCH" != "PROD" ]]
then
    echo "Please checkout the PRODUCTION branch to proceed"
    exit 1
fi

heroku releases --app todoapp1
echo "----------------- PRODUCTION! MAKE SURE THERE ARE NO CHANGES HERE:"
git status
echo "----------------- PRODUCTION! "
read -r -p "Are you sure? [y/N] (deploying: PRODUCTION! $1) " response
case $response in
    [yY][eE][sS]|[yY])
        echo "pushing to heroku"
        git push -v production PRODUCTION:master
        ;;
esac
