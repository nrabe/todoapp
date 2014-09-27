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

    # NOTE: Skip certain emails. It makes unit testing way faster.
    if settings.SKIP_EMAILS:
        logging.debug('SKIP.send_multipart_email_task %r %r' % (subject_content, to_email))
        return

    logging.debug('SEND.send_multipart_email_task %r %r' % (subject_content, to_email))
    msg.send()


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

