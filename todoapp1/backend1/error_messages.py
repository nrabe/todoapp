# -*- coding: utf-8 -*-
"""
Error codes and messages... the code should be unique (it's there to indicate the client app an action.
"""
from bunch import Bunch

ERRORS = Bunch()

ERRORS.invalid_parameter = (200, 'Missing or invalid parameter: %(field_name)s')
ERRORS.authentication_required = (401, 'Authentication required')
ERRORS.signin_incorrect = (402, 'Invalid email address or password')
ERRORS.signup_email_already_exists = (403, 'Email address already registered')
ERRORS.cannot_access_list = (500, 'You cannot access this TODO list')
