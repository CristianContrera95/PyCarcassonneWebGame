# -*- coding: utf-8 -*-
from os import path

from carcassonne.settings import STATIC_URL


GAMEMAP_SIZE = 14
AMOUNT_PIECES = 71
POINTS_ROAD_COMPLETED = 1
POINTS_CITY_COMPLETED = 2
POINTS_FARM_COMPLETED = 3
POINTS_CLOISTER_COMPLETED = 9
FOLLOWER_SRC = path.join(STATIC_URL, 'img', 'follower.png')
FOLLOWER_FOR_PLAYER = 8
PIECE_TYPE_LIST = ['roads_adjacent', 'roads_parallel', 'crossroad', 'cloister', 'city_adjacent', 'city_parallel']
PIECE_FILES = {
    'roads_adjacent': path.join(STATIC_URL, 'img', 'roads_adjacent.jpeg'),
    'roads_parallel': path.join(STATIC_URL, 'img', 'roads_parallel.jpeg'),
    'crossroad': path.join(STATIC_URL, 'img', 'crossroad.jpeg'),
    'cloister': path.join(STATIC_URL, 'img', 'cloister.jpeg'),
    'city_adjacent': path.join(STATIC_URL, 'img', 'city_adjacent.jpeg'),
    'city_parallel': path.join(STATIC_URL, 'img', 'city_parallel.jpeg'),
}
TYPES_PIECE = (
    ('roads_adjacent', 'Roads Adjacent'),
    ('roads_parallel', 'Roads Parallel'),
    ('crossroad', 'Crossroad'),
    ('cloister', 'Cloister'),
    ('city_adjacent', 'City Adjacent'),
    ('city_parallel', 'City Parallel'),
)
TYPES_FOLLOWER = (
    ('farmer', 'Farmer'),
    ('robber', 'Robber'),
    ('gentleman', 'Gentleman'),
    ('monk', 'Monk'),
)
FOLLOWER_TYPE = {
    'roads_adjacent': 'farmer',
    'roads_parallel': 'robber',
    'crossroad': 'robber',
    'cloister': 'monk',
    'city_adjacent': 'gentleman',
    'city_parallel': 'farmer',
}