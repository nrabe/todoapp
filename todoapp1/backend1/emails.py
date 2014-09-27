# -*- coding: utf-8 -*-
from __future__ import absolute_import
import os
import logging

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
from django.template import Context
from django.conf import settings
from pq.decorators import job


@job('default')
def send_multipart_email_task(
                              from_email=None,
                              to_email=None,
                              subject_content=None,
                              text_content=None,
                              html_content=None,
                              template_subject=None,
                              template_txt=None,
                              template_html=None,
                              context=None,
                              cc=None,
                              ):
    """
    sends an html/text multipart email
    """
    # subject, from_email, to = 'hello', 'from@example.com', 'to@example.com'
    context = context or {}
    context.update({'WEBSITE_URL': settings.WEBSITE_URL, 'SITE_TITLE': settings.SITE_TITLE, })
    context = Context(context)

    subject_content = subject_content or get_template(template_subject).render(context)
    subject_content = subject_content.replace('\n', ' ').strip()
    text_content = text_content or get_template(template_txt).render(context)  # 'This is an important message.'
    html_content = html_content or get_template(template_html).render(context)  # '<p>This is an <strong>important</strong> message.</p>'
    if not isinstance(to_email, list):
        to_email = [to_email]

    msg = EmailMultiAlternatives(subject_content, text_content, from_email, to_email)
    msg.attach_alternative(html_content, "text/html")

    # NOTE: in local/dev environments (any DEBUG=True) skip sending ANY email that's outside the company
    if settings.DEBUG and not (to_email[0].endswith('@table8.com') or to_email[0].endswith('@daemoniclabs.com')):
        logging.debug('SKIP.send_multipart_email_task (non-company email) %r %r' % (subject_content, to_email))
        return True  # always return a positive value

    # NOTE: Skip certain emails. It makes unit testing way faster.
    if settings.SKIP_EMAILS or (not os.environ.get('SEND_UNITTEST_EMAILS') and to_email[0].startswith('nahuel+test')):
        logging.debug('SKIP.send_multipart_email_task %r %r' % (subject_content, to_email))
        return True  # always return a positive value

    logging.debug('SEND.send_multipart_email_task %r %r' % (subject_content, to_email))
    msg.send()
    return True  # always return a positive value


def send_multipart_email(*args, **kwargs):
    """ wrapper """
    if settings.USE_TASK_QUEUE:
        send_multipart_email_task.delay(*args, **kwargs)
    else:
        # directly call the function
        send_multipart_email_task(*args, **kwargs)


def send_welcome_email(user, override_email_to=None):
    """
    sends welcome email, for a user that just signed up WITHOUT booking a reservation
    """
    context = {
        'user': user,
    }
    from_email = '%s <nrabe2+notification@gmail.com>' % settings.EMAIL_SUBJECT_PREFIX
    send_multipart_email(
        subject_content='Welcome to TO-DO App!',
        text_content='Welcome to TO-DO App!',
        html_content='Welcome to TO-DO App!',
        from_email=from_email,
        to_email=user.email,
        context=context,
        )

