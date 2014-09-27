# -*- coding: utf-8 -*-
from django.contrib import admin

from todoapp1.backend1.models import UserProfile, TODOList, TODOListItem, TODOListSharing, HandsontableDemo


class BaseAdmin(admin.ModelAdmin):
    pass


class TODOListAdmin(BaseAdmin):
    raw_id_fields = ('created_by',)


class TODOListItemAdmin(BaseAdmin):
    raw_id_fields = ('todolist', 'created_by', 'last_updated_by')


class TODOListSharingAdmin(BaseAdmin):
    raw_id_fields = ('todolist', 'shared_by', 'shared_with')


admin.site.register(UserProfile)
admin.site.register(TODOList, TODOListAdmin)
admin.site.register(TODOListItem, TODOListItemAdmin)
admin.site.register(TODOListSharing, TODOListSharingAdmin)
admin.site.register(HandsontableDemo)
