# -*- coding: utf-8 -*-


def city_list(request, page_token=None, search=None, city_id=None, venue_id=None, inventory_id=None):
    pass


def city_create(request, **kwargs):
    pass


def city_update(request, table_id=None, **kwargs):
    pass


def city_delete(request, table_id=None, **kwargs):
    pass


def restaurant_list(request, page_token=None, search=None, city_id=None, venue_id=None, inventory_id=None):
    pass


def restaurant_create(request, **kwargs):
    pass


def restaurant_update(request, table_id=None, **kwargs):
    pass


def restaurant_delete(request, table_id=None, **kwargs):
    pass


def inventory_list(request, page_token=None, search=None, city_id=None, venue_id=None, inventory_id=None):
    pass


def inventory_create(request, **kwargs):
    pass


def inventory_update(request, table_id=None, **kwargs):
    pass


def inventory_delete(request, table_id=None, **kwargs):
    pass


def reservation_list(request, page_token=None, search=None, city_id=None, venue_id=None, reservation_id=None):
    pass


def reservation_create(request, **kwargs):
    pass


def reservation_update(request, reservation_id=None, is_confirmed=None, notes=None):
    pass


def reservation_cancel(request, reservation_id=None, return_table_to_inventory=False):
    pass


def userprofile_list(request, page_token=None, search=None, **kwargs):
    pass


def userprofile_create(request, **kwargs):
    pass


def userprofile_update(request, userprofile_id=None, **kwargs):
    pass


def userprofile_delete(request, userprofile_id=None):
    pass


def userprofile_send_reset_password_email(request, userprofile_id=None):
    pass


def pxcode_list(request, page_token=None, search=None, **kwargs):
    pass


def pxcode_create(request, page_token=None, **kwargs):
    pass


def pxcode_update(request, pxcode_id=None, **kwargs):
    pass


def pxcode_delete(request, pxcode_id=None):
    pass


def pxcode_user_list(request, page_token=None, search=None, **kwargs):
    pass


def pxcode_user_create(request, page_token=None, **kwargs):
    pass


def pxcode_user_update(request, pxcode_id=None, **kwargs):
    pass


def pxcode_user_delete(request, pxcode_id=None):
    pass


def pxcode_promocode_user_list(request, page_token=None, search=None, **kwargs):
    pass


def pxcode_promocode_user_generate(request, page_token=None, **kwargs):
    pass


def pxcode_promocode_user_update(request, pxcode_id=None, **kwargs):
    pass


def pxcode_promocode_user_delete(request, pxcode_id=None):
    pass
