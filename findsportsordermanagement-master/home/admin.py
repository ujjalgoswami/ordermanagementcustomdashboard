from django.contrib import admin

# Register your models here.

# # Register your models here.
from home.models import PendingDispatchOrderIDExceptions, PendingRefundsOrderIDExceptions

admin.site.register(PendingDispatchOrderIDExceptions)
admin.site.register(PendingRefundsOrderIDExceptions)