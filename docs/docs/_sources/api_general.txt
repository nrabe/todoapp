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


General API
======================================

- JSON-RPC 2.0 protocol, with named parameters only http://www.jsonrpc.org/specification
- ISO 8601 date, time and datetime formats: YYYY-MM-DD, YYYY-MM-DDTHH:MM:SS+HH:MM, and HH:MM:SS
- every parameter is required unless marked as (optional)
- every String parameter and response is up to 255 characters long, unless otherwise specified
- UTF-8 as preferred request/response encoding


.. automodule:: todoapp1.backend1.api
   :members:
   :undoc-members:
