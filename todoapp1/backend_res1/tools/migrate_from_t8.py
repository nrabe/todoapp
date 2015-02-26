# -*- coding: utf-8 -*-
import logging
import os
import sys

from bunch import Bunch

sys.path.append(os.path.abspath('./'))
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "todoapp1.settings." + os.environ.get("ENVIRONMENT", "MUST-SET-ENVIRONMENT-VARIABLE-SEE-README"))
import django
django.setup()

from django.utils import timezone
from django.conf import settings
from django.db.utils import IntegrityError


import todoapp1.backend_res1.models as models

import psycopg2
import psycopg2.extensions
psycopg2.extensions.register_type(psycopg2.extensions.UNICODE)
psycopg2.extensions.register_type(psycopg2.extensions.UNICODEARRAY)

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse
urlparse.uses_netloc.append('postgres')
urlparse.uses_netloc.append('postgresql')
urlparse.uses_netloc.append('pgsql')


def bunchfetchall(cursor):
    "Returns all rows from a cursor as a dict"
    desc = cursor.description
    return [
        Bunch(zip([col[0] for col in desc], row))
        for row in cursor.fetchall()
    ]

url = 'postgres://tablenow@localhost/tablenow'
url = urlparse.urlparse(url)

connection = psycopg2.connect(database=url.path[1:].split('?', 2)[0],
                        user=url.username,
                        password=url.password,
                        host=url.hostname,
                        port=url.port)

cursor = connection.cursor()
cursor.execute("SELECT * FROM venues_city WHERE rec_status=0 ORDER BY creation_date")
items = bunchfetchall(cursor)
for r in items:
    models.Region.upsert_if_changed(conds=dict(t8id=r.id),
                         t8id=r.id,
                         date_created=r.creation_date.astimezone(timezone.utc),
                         name=r.title,
                         is_active=r.is_active,
                         latitude=r.latitude,
                         longitude=r.longitude)
cursor.close()


cursor = connection.cursor()
cursor.execute("SELECT * FROM venues_venue WHERE rec_status=0 ORDER BY creation_date")
items = bunchfetchall(cursor)
for r in items:
    region = models.Region.objects.get(t8id=r.city_id)
    models.Restaurant.upsert_if_changed(conds=dict(t8id=r.id),
                         t8id=r.id,
                         date_created=r.creation_date.astimezone(timezone.utc),
                         name=r.title,
                         region=region,
                         short_description=r.excerpt[:254],
                         address=r.address,
                         opentable_id=r.opentable_id,
                         latitude=r.latitude,
                         longitude=r.longitude,
                         is_active=r.is_active)
cursor.close()

#
# customers
#
cursor = connection.cursor()
cursor.execute("SELECT * FROM reserv_userprofile WHERE rec_status=0 AND user_type=50 ORDER BY creation_date")
items = bunchfetchall(cursor)
for r in items:
    models.Customer.upsert_if_changed(conds=dict(t8id=r.id),
                         t8id=r.id,
                         date_created=r.creation_date.astimezone(timezone.utc),
                         name='%s %s' % (r.first_name, r.last_name),
                         email=r.email,
                         is_active=r.is_active)
cursor.close()

#
# customers ( from reservations directly, and only if they do not exist already)
#
cursor = connection.cursor()
cursor.execute("SELECT r.*, a.creation_date FROM reserv_reservation r JOIN reserv_availability a ON (r.availability_ptr_id=a.id) ORDER BY email")
items = bunchfetchall(cursor)
for r in items:
    try:
        assert r.email, r
        models.Customer.upsert_if_changed(conds=dict(email=r.email),
                             date_created=r.creation_date.astimezone(timezone.utc),
                             name='%s %s' % (r.first_name, r.last_name),
                             email=r.email,
                             is_active=True)
    except IntegrityError, e:
        logging.error(e)
cursor.close()

#
# concierges
#
cursor = connection.cursor()
cursor.execute("SELECT * FROM reserv_userprofile WHERE rec_status=0 AND user_type=40 ORDER BY creation_date")
items = bunchfetchall(cursor)
for r in items:
    models.Concierge.upsert_if_changed(conds=dict(t8id=r.id),
                         t8id=r.id,
                         date_created=r.creation_date.astimezone(timezone.utc),
                         name='%s %s' % (r.first_name, r.last_name),
                         email=r.email,
                         is_active=r.is_active)
cursor.close()

#
# staff
#
cursor = connection.cursor()
cursor.execute("SELECT * FROM reserv_userprofile WHERE rec_status=0 AND user_type in (10,20,21,22,23,24) ORDER BY creation_date")
items = bunchfetchall(cursor)
for r in items:
    models.Staff.upsert_if_changed(conds=dict(t8id=r.id),
                         t8id=r.id,
                         date_created=r.creation_date.astimezone(timezone.utc),
                         name='%s %s' % (r.first_name, r.last_name),
                         email=r.email,
                         is_active=r.is_active)
cursor.close()


cursor = connection.cursor()
cursor.execute("SELECT * FROM reserv_reservation r JOIN reserv_availability a ON (r.availability_ptr_id=a.id) WHERE rec_status = 0 ORDER BY creation_date")
items = bunchfetchall(cursor)
for r in items:

    customer = None
    try:
        customer = models.Customer.objects.get(email=r.email)
    except:
        try:
            customer = models.Customer.objects.get(t8id=r.reserved_by_id)
        except Exception, e:
            logging.warn([e, r.email, r.reserved_by_id])

    concierge = None
    try:
        concierge = models.Concierge.objects.get(t8id=r.reserved_by_id)
    except Exception, e:
        # naturally, most of the reservations were made by the customer... or other users (staff)
        pass

    restaurant = models.Restaurant.objects.get(t8id=r.venue_id)
    models.Reservation.upsert_if_changed(conds=dict(t8id=r.id),
                         t8id=r.id,
                         date_created=r.creation_date.astimezone(timezone.utc),
                         order_no=r.order_no,
                         restaurant=restaurant,
                         concierge=concierge,
                         customer=customer,
                         purchase_date=r.reserved_date,
                         res_date=r.rdate,
                         res_time=r.rtime,
                         res_partysize=r.max_seats
                         )
cursor.close()
