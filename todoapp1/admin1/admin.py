# -*- coding: utf-8 -*-
import logging

from django.contrib import admin
from django.conf.urls import url

from todoapp1.backend1 import models


class BaseAdmin(admin.ModelAdmin):
    pass


class TODOListAdmin(BaseAdmin):
    raw_id_fields = ('created_by',)


class TODOListItemAdmin(BaseAdmin):
    raw_id_fields = ('todolist', 'created_by', 'last_updated_by')


class TODOListSharingAdmin(BaseAdmin):
    raw_id_fields = ('todolist', 'shared_by', 'shared_with')


class HandsontableDemoAdmin(BaseAdmin):
    raw_id_fields = ('test_foreign_key', 'test_foreign_key_null')


admin.site.register(models.UserProfile)
admin.site.register(models.TODOList, TODOListAdmin)
admin.site.register(models.TODOListItem, TODOListItemAdmin)
admin.site.register(models.TODOListSharing, TODOListSharingAdmin)
admin.site.register(models.HandsontableDemo, HandsontableDemoAdmin)
