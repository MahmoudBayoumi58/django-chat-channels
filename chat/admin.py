from django.contrib import admin
from chat.models import *


# Register your models here.
class RoomAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name", )}


admin.site.register(Room, RoomAdmin)
