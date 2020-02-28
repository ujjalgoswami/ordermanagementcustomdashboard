from django.contrib import admin

# Register your models here.
from suppliers.models import Supplier_Details




@admin.register(Supplier_Details)
class Supplier_Details(admin.ModelAdmin):
    readonly_fields = ["supplier_name","onhold","onhold_date"]