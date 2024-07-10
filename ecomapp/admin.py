from django.contrib import admin
from ecomapp.models import product,Contactenquiry

# Register your models here.


class ProductAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'age', 'cat', 'pdetail', 'is_active']
    list_filter = ['cat', 'is_active']


admin.site.register(product, ProductAdmin)


class ContactAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'message']


admin.site.register(Contactenquiry, ContactAdmin)




