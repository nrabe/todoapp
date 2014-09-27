todoapp1 - sample web/mobile/api project
======================================

A 4 part project (in principle each backend1 + APP can be hosted independently ):
	backend ( api, models, tools, etc )
    web
    mobile (webapp)
    admin


USEFUL LINKS ( you must sign in to heroku for most of them to work )

    Website public interface
    http://dev-todoapp1.herokuapp.com/
    
    New Relic monitoring tool
    https://addons-sso.heroku.com/apps/dev-todoapp1/addons/newrelic:stark
    
    Papertrail logging storage
    https://addons-sso.heroku.com/apps/dev-todoapp1/addons/papertrail:choklad
    
    Node4j /  GrapheneDB interface
    https://addons-sso.heroku.com/apps/dev-todoapp1/addons/graphenedb:chalk


NICE/NOTABLE FEATURES:

- Mostly Django std features, with (relatively) few 3rd party libraries, so no new languages, protocols, documentation, and standards to follow.

- Little magic or implicit behavior... api handlers are views, serializers are simply model methods, parameter validators are manually called functions.

- flexible "versioning", being able to implement /0.2/signup/ alongside /0.1/signup/ or even a parallel "backend2" directory.

- advanced error handling ( usually the last thing you do, and pretty annoying to plan for ), handling webs, api, periodic processes, etc.

- color-coded and formatted logging.

- local/dev/prod stages and settings (even particular settings for different developers or branches).

- client versioning (as part of the url).

- scripts for common tasks, mostly self-explanatory.

- pretty basic unit testing, mostly to catch the worst errors.

- unit testing using the actual database, instead of the django way of always creating a test database (requires care when testing! but the actual db and its data is tested this way).


HINTS/TIPS/QUESTIONS:
    
- Do not use middlewares or context processors... they are "magic", hard to debug, understand and track down... and affect every request, not just the ones you think they should.

- Do not user third party dependencies unless it's unavoidable, and consult the rest of the team for alternatives... Third party libraries may seem cool, but over time they become unmaintained, or even the well maintained ones may fail to build for a few hours, days or weeks... and extra packages means extra documentation, extra know-how, and another source of conflicts and bugs.

- If it's not unit-tested (at least a very basic test), it's not complete. Others in the team do not know how to test the new feature, and you'll forget in a week.

- Use keyword parameters... positional parameters are harder to understand, particularly when you're using somebody else's functions.

- Do not user request.user outside the backend. It's tempting, but the API may change/censor user information.

- Do not access the DB models outside backend1. Creating an API call is easy, and just for that purpose, and it separates the specific data storage from the rest of the system.

- Why I prefer JSON-RPC and not REST: Designing REST APIs is pretty hard, different than python, and particularly inefficient when there is no clear idea on how it will be used (you end up having 3 or 4 API calls for a particular view... wasteful).


API FORMATS:

The communication methods are (in order of preference):

- JSON-RPC 2.0 over HTTP http://www.jsonrpc.org/specification (*),  with ISO 8601 date, datetime and time format.
- Python native.

There is also an HTTP POST / GET way, but it's not recommended for usage. JSON-RPC is clearer and allows batch calls.

(*) A simplified, more constrained implementation... It does not have:
    4.1 Notification
    4.2 Parameter Structures: by position

Special headers for JSON-RPC ( both are parameters for the API() instance in Python native format )
    - The "User-Agent" header, to determine platform and client version ( I.E. IOS.0.0.1 )
    - The "sessionid" cookie: required in every API call *after* a user is authenticated (this is the auth_token returned from signin/signup, or the cookie itself)


Examples:
    apicontext = backend.get_api_context()
    backend.api_sys_test(apicontext, test='ok')
    try:
        backend.api_sys_test(apicontext, test='error')
    except BackendError, e:
        raise

    export APISERVER=127.0.0.1:8600 
    curl -H Accept:application/json -H Content-Type:application/json -H X-CLIENT-VERSION:TEST.0.0.1 -H Cookie:sessionid=pnf77kqilqjm3q8y68vpauso4u48h37x -X POST -d '[{"jsonrpc": "2.0", "method": "api_sys_test", "params": {"test": "ok"}, "id": 0}]' "http://${APISERVER}/api/0.1/jsonrpc/console.test/"
    curl -H Accept:application/json -H Content-Type:application/json -H X-CLIENT-VERSION:TEST.0.0.1 -H Cookie:sessionid=pnf77kqilqjm3q8y68vpauso4u48h37x -X POST -d '[{"jsonrpc": "2.0", "method": "api_sys_test", "params": {"test": "ok"}, "id": 0}, {"jsonrpc": "2.0", "method": "api_sys_test", "params": {"test": "error"}, "id": 1}]' "http://${APISERVER}/api/0.1/jsonrpc/console.test/"

    HTTP POST/GET (internal usage only)
    curl -H Accept:application/json  -H X-CLIENT-VERSION:TEST.0.0.1 -H Cookie:sessionid=pnf77kqilqjm3q8y68vpauso4u48h37x -X POST -d 'venue_id=75edbcda7ff44c01abc534f708ae3c6a' https://api.table-4.me/api/0.1/api_sys_test/
    curl -H Accept:application/json -H X-CLIENT-VERSION:TEST.0.0.1 -X GET "https://api.table-4.me/api/0.1/api_sys_test/?venue_id=75edbcda7ff44c01abc534f708ae3c6a"


RECOMMENDED ADDITIONS

    throttling/limiting requests (to avoid DOS attacks)
    https://github.com/sobotklp/django-throttle-requests


USEFUL SCRIPTS AND COMMANDS

    - scripts/test.sh to run all the tests.
    - scripts/run-locally.sh to run a single development server instance
    - scripts/run-foreman.sh to run 2 server instances ( requires foreman and nginx installed )
    - scripts/upload-heroku.sh to upload to the DEVELOPMENT server
    - scripts/upload-heroku-prod.sh to upload to the PRODUCTION server


RUNTIME CONFIGURATION VARIABLES

    HINT: the ENVIRONMENT shell variable can be set in your ~/.bash_profile file in OSX, adding: export ENVIRONMENT=(your name)

    ENVIRONMENT: a shell variable (or heroku config setting for dev/prod) with one of this values:
        - your name
        - heroku_dev
        - heroku_prod
        ... each of those should be a setting.py file in todoapp1/settings/

    DATABASE_URL: postgres://USERNAME@localhost/DATABASE
        for local development, this is usually set in the local settings.py by adding the lines: 
        os.environ.setdefault('DATABASE_URL', 'postgres://USERNAME@localhost/DATABASE')
        DATABASES = postgresify()


CLONING FROM GITHUB (assumes the database is already set up)
    
    git clone git@github.com:StartupHouse/todoapp1.git
    cd todoapp1
    virtualenv --distribute --no-site-packages venv
    source venv/bin/activate
    LIBMEMCACHED=/opt/local pip install -r requirements.txt
    python manage.py migrate
    python manage.py check
    scripts/run-locally.sh


STARTING FROM SCRATCH
	
	mkdir todoapp1
	cd todoapp1
	virtualenv --distribute --no-site-packages venv
	source venv/bin/activate
	pip install https://www.djangoproject.com/download/1.7c1/tarball/
	LIBMEMCACHED=/opt/local pip install bunch ordereddict django-heroku-memcacheify django-heroku-postgresify gunicorn psycopg2 pylibmc futures requests

	django-admin.py startproject todoapp1
	(moved the contents of todoapp1/* to the parent dir) 
	django-admin.py startapp backend1
	django-admin.py startapp mobile1
	django-admin.py startapp web1

	sudo su postgres -c 'psql'
	CREATE USER xxxxx PASSWORD 'xxxxx' CREATEDB;
	psql92 -U xxxxx template1 -c 'CREATE DATABASE xxxxx;'


TO ADD A NEW APP/VERSION ( a section of the project, such as admin1, admin2, web1, mobile1 )
    
    - create a directory next to the others
    - add todoapp1.DIRECTORY to settings.INSTALLED_APPS
    - add the DIRECTORY/urls.py to the urls.py file
