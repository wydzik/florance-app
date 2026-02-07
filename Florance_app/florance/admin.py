from django.contrib import admin
from .models import Florysta, Pracownia, Realizacja, Pracownicy, Kandydat, StatusKandydata, StatusPrzypisania, \
                    RealizacjaPlik, Powiadomienie

admin.site.register(Florysta)


@admin.register(Florysta)
class FlorystaAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "avatar")


admin.site.register(Pracownia)
admin.site.register(Realizacja)
admin.site.register(Pracownicy)
admin.site.register(Kandydat)
admin.site.register(StatusKandydata)
admin.site.register(StatusPrzypisania)
admin.site.register(RealizacjaPlik)
admin.site.register(Powiadomienie)