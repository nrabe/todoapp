.. tablenow documentation master file, created by
   sphinx-quickstart on Tue Oct  7 22:49:52 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

.. role:: json(code)
   :language: json
   :class: highlight

.. role:: python(code)
   :language: python
   :class: highlight


Interesting project features
======================================


- Simple, yet powerful API patterns ( each API call can be used as a simple python function, called via json-rpc v2.0, and even as a RESTful URL defined in backend1.urls )

- uses few 3rd party packages/modules. 3rd party means new protocols/languages/documentation/maintenance issues... so weight carefully when to write custom code and when to use a package/service.

- Little magic or implicit behavior... pages are views, api handlers are views, serializers are functions returning dictionaries, parameter validators are manually called functions.

- request parameter validation/parsing is kept very simple (call the param_xxx() functions, and/or write custom code raising ApiExceptions )

- integrated sphinx documentation, including API response samples (thanks to the tests)

- heroku ready

- monitoring and error reporting using New Relic and Sentry.

- multiple environments/pipelines ( development, testing, production )

- whitenoise static file server


General Design/Coding Tips
======================================

- use the shortcuts page (lots of links on a system, and it' useful to have them always handy)

- There are several scripts in the scripts/ directory. Most of them are self-explanatory.

- To generate the documentation locally, run the script and reload the server.

- heroku/environment variables can usually be overriden locally. E.g. `ENVIRONMENT=heroku_development scripts/run-locally.sh` will run the local server with that settings file.


- if it's  not in a test, it's a bug, or it'll be a bug in the future.

- if there was an error, write a test. It will happen again, several times.

- call backend functions using keyword parameters. It greatly helps future compatibility.

- Don't rely on pip dependencies or 3rd party services lightly (the worst downtime of the lot is your best possible downtime, and 3rd party code is hard to understand/debug/maintain/upgrade).

- use a vagrant box to work. It'll run in different computers and/or for several developers.


USEFUL FETURES / PRACTICES:

- modular project layout (if the pieces need to be hosted separately), self-explanatory scripts for common tasks.

- app versioning, api versioning, client versioning... very flexible to adapt to a lot of early project stages.

- local/dev/prod stages and settings (even particular settings for different developers or branches).

- admin (and custom) foreign-key lookups, plus automatically transforming selects to autocompletes (using jquery-select2 http://ivaynberg.github.io/select2/ )

- handsontable spreadsheet-like interface to models, supporting: foreign-keys, choice fields, lookup, datetime/date/time fields, cut and paste. An awesome experiment (*)

- error handling, logging and notification: web, api, periodic processes, etc.

- pretty basic, but useful, unit testing (mostly to catch the worst errors).

- unit testing using the actual database, instead of the django way of always creating a test database (requires care when testing! but the actual db and its data gets tested this way).


(*) Handsontable vs Django Admin:
django admin is good enough sometimes... but it requires too much tweak/coding just to be "good enough", and you usually throw it away for specific CRUD pages after a while.
Handsontable is nicer for many projects: a familiar user-interface, easy to tweak, and can be supplemented nicely with just a "details" form handling the complex fields ( html fields, images, location maps, etc). Horizontal scrolling is a small price to pay.


TIPS FOR PROJECTS:



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
    - scripts/documentation.generator.sh this script re-creates the documentation.
    - scripts/run-locally.sh to run a single development server instance
    - scripts/run-foreman.sh to run 2 server instances ( requires foreman and nginx installed )
    - scripts/upload-heroku.sh to upload to the DEVELOPMENT server
    - scripts/upload-heroku-prod.sh to upload to the PRODUCTION server


RUNTIME CONFIGURATION VARIABLES

    HINT: the ENVIRONMENT shell variable can be set in your shell profile, adding: export ENVIRONMENT=(your name)

    ENVIRONMENT: a shell variable (or heroku config setting for dev/prod) with one of this values:
        - your name
        - heroku_dev
        - heroku_prod
        ... each of those is a django setting file in todoapp1/settings/

    DATABASE_URL: postgres://USERNAME@localhost/DATABASE
        for local development, this is usually set in the local settings.py by adding the lines:
        os.environ.setdefault('DATABASE_URL', 'postgres://USERNAME@localhost/DATABASE')
        DATABASES = postgresify()


Backend interface
======================================

Do not import modules from the backend. Instead, put them in the backend init file. The backend exposes:

.. automodule:: todoapp1.backend1



API INTERNAL FUNCTIONS
======================================

.. automodule:: todoapp1.backend1.api_utils
    :members:

