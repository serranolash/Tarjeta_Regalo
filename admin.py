from django.contrib import admin
from .models import Voucher, Etiqueta, Tipo, Local, CustomUser


# Register your models here.
admin.site.register(Voucher)
admin.site.register(Etiqueta)
admin.site.register(Tipo)
admin.site.register(Local)
admin.site.register(CustomUser)
