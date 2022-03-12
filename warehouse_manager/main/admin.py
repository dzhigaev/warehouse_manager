from django.contrib import admin
from .models import *

class WarehousesAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'location')
    list_display_links = ('id', 'name', 'location')
    search_fields = ('name', )
    prepopulated_fields = {'slug': ('name', )}


admin.site.register(Tickets)
admin.site.register(Trucks)
admin.site.register(Trailers)
admin.site.register(Warehouses, WarehousesAdmin)
admin.site.register(WarehouseReply)
admin.site.register(TicketImage)
admin.site.register(RRToken)
