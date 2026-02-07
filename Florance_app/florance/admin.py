from django.contrib import admin
from .models import Florysta, Pracownia, Realizacja, Pracownicy, Kandydat, StatusKandydata, StatusPrzypisania, \
                    RealizacjaPlik, Powiadomienie

admin.site.register(Florysta)
admin.site.register(Pracownia)
admin.site.register(Realizacja)
admin.site.register(Pracownicy)
admin.site.register(Kandydat)
