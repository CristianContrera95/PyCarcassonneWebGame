# -*- coding: utf-8 -*-

from django.conf.urls import url

from apps.lobby.views import GameList, GameCreate, GameWaiting, GameDelete, save_session

app_name = 'lobby'

urlpatterns = [
    url('^$', GameList.as_view(), name='index'),
    url('save_session/', save_session, name='save_session'),
    url('game_create/', GameCreate.as_view(), name='game_create'),
    url('game_waiting/(?P<game_id>[0-9]+)/', GameWaiting.as_view(), name='game_waiting'),
    url('game_delete/(?P<pk>[0-9]+)/', GameDelete.as_view(), name='game_delete'),
]
