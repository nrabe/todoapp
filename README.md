todoapp1 - sample web/mobile/api project
======================================

A kitchen-sink of useful tools/features/practices for relatively complex django projects:
	backend ( api, models, periodic processes, tools, etc )
    web
    mobile (webapp)
    admin


USEFUL FETURES/PRACTICES:

- very modular project layout, self-explanatory scripts for common tasks.

- app versioning, api versioning, client versioning... very flexible.

- local/dev/prod stages and settings (even particular settings for different developers or branches).

- color-coded and formatted logging.

- admin (and custom) foreign-key lookups, both manual (defining autocomplete views) and automatic ( converting selects to autocompletes )

- error handling and notification: web, api, periodic processes, etc.

- pretty basic, but useful, unit testing (mostly to catch the worst errors).

- unit testing using the actual database, instead of the django way of always creating a test database (requires care when testing! but the actual db and its data gets tested this way).


TIPS FOR PROJECTS:


- use few 3rd party packages/modules. 3rd party means new protocols/languages/documentation/maintenance issues... if it can be avoided, it's better.

- Little magic or implicit behavior... pages are views, api handlers are views, serializers are simply model methods, parameter validators are manually called functions.

- Do not use middlewares or context processors... they are "magic", hard to debug, understand and track down... and affect every request, not just the ones you think they should.

- Use keyword parameters... positional parameters are harder to understand, particularly when you're using somebody else's functions.

- Do not access the DB models (or other non-json-serializable stuff) outside backend1. Creating an API call is easy, and it separates the specific data storage from the rest of the system.

- Prefer JSON-RPC over REST: Designing REST APIs naming and relationships is pretty hard, and inefficient when there is no clear idea about where/how it will be used (you end up having 3 or 4 API calls for a particular view... wasteful).

- If it's not unit-tested (at least a very basic test), it's not complete. Others in the team do not know how to test the new feature, and you'll forget in a week.


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

    # HTTP POST/GET (internal usage only)
    curl -H Accept:application/json  -H X-CLIENT-VERSION:TEST.0.0.1 -H Cookie:sessionid=pnf77kqilqjm3q8y68vpauso4u48h37x -X POST -d 'venue_id=75edbcda7ff44c01abc534f708ae3c6a' https://api.table-4.me/api/0.1/api_sys_test/
    curl -H Accept:application/json -H X-CLIENT-VERSION:TEST.0.0.1 -X GET "https://api.table-4.me/api/0.1/api_sys_test/?venue_id=75edbcda7ff44c01abc534f708ae3c6a"


RECOMMENDED ADDITIONS

    throttling/limiting requests (to avoid DOS attacks)
    https://github.com/sobotklp/django-throttle-requests


ADDING A NEW APP/VERSION ( a section of the project, such as admin1, admin2, web1, mobile1 )
    
    - create a directory next to the others
    - add todoapp1.DIRECTORY to settings.INSTALLED_APPS
    - add the DIRECTORY/urls.py to the urls.py file


USEFUL SCRIPTS AND COMMANDS
    - scripts/test.sh to run all the unit tests.
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
    
    heroku plugins:install https://github.com/ddollar/heroku-push # needed for remote deployment
    git remote add heroku git@heroku.com:dev-todoapp1.git # needed for deployment
    git remote add production git@heroku.com:todoapp1.git # needed for deployment
