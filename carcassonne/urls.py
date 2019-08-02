# -*- coding: utf-8 -*-

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.lobby.urls'),),
    path('game/', include('apps.game.urls')),
]
