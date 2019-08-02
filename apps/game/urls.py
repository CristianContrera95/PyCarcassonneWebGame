# -*- coding: utf-8 -*-

from django.conf.urls import url

from .views import (
    init_game, get_score, get_piece, get_turn, get_amount_pieces,
    set_piece, set_piece_rotation, get_amount_followers,
    set_follower_to_piece, get_follower, step, update_pieces
)

app_name = 'game'

urlpatterns = [
    url('init_game/(?P<game_id>[0-9]+)/', init_game, name='init_game'),
    url('ajax/get_score/(?P<game_id>[0-9]+)/', get_score, name='get_score'),
    url('ajax/get_piece/(?P<game_id>[0-9]+)/', get_piece, name='get_piece'),
    url('ajax/get_turn/(?P<game_id>[0-9]+)/', get_turn, name='get_turn'),
    url('ajax/get_amount_pieces/(?P<game_id>[0-9]+)/', get_amount_pieces, name='get_amount_pieces'),
    url('ajax/set_piece/(?P<game_id>[0-9]+)/', set_piece, name='set_piece'),
    url('ajax/set_piece_rotation/(?P<game_id>[0-9]+)/', set_piece_rotation, name='set_piece_rotation'),
    url('ajax/get_amount_followers/(?P<game_id>[0-9]+)/', get_amount_followers, name='get_amount_followers'),
    url('ajax/get_follower/(?P<game_id>[0-9]+)/', get_follower, name='get_follower'),
    url('ajax/set_follower_to_piece/(?P<game_id>[0-9]+)/', set_follower_to_piece, name='set_follower_to_piece'),
    url('ajax/step/(?P<game_id>[0-9]+)/', step, name='step'),
    url('ajax/update_pieces/(?P<game_id>[0-9]+)/', update_pieces, name='update_pieces'),
]