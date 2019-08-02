# -*- coding: utf-8 -*-

from django.db import models as md
from django.db.models import Q

from apps.lobby.models import Game, Player
from .constants import (
    TYPES_PIECE, TYPES_FOLLOWER, GAMEMAP_SIZE, FOLLOWER_SRC,
    POINTS_ROAD_COMPLETED, POINTS_CITY_COMPLETED,
    POINTS_FARM_COMPLETED, POINTS_CLOISTER_COMPLETED
)
from .utils import Graph


class GameMap(md.Model):
    game = md.OneToOneField(Game, on_delete=md.CASCADE)

    def __str__(self):
        return 'Map in ' + self.game.__str__()

    def check_continuos_side(self, new_piece, to_cell):
        cells_around = Cell.objects.filter(piece__isnull=False,
                                           x__in=[to_cell.x-1, to_cell.x, to_cell.x+1],
                                           y__in=[to_cell.y-1, to_cell.y, to_cell.y+1],
                                           game_map=self).exclude(x=to_cell.x, y=to_cell.y)
        result = True
        for cell in cells_around:
            if not result:
                break
            shared_side = cell.shared_side(to_cell)  # posicion de cell, respecto de to_cell
            if shared_side:
                if cell.piece.picture == 'cloister' or new_piece.picture == 'cloister':
                    continue
                #  new_piece tiene el lado shared_side igual al cell.piece
                result = result and new_piece.is_same_side(shared_side, cell.piece)
        return result

    def check_completed(self, piece):
        cells_with_pictures = Cell.objects.filter(Q(piece__isnull=False), game_map=self)

        self.check_cloister_completed(piece.cell, cells_with_pictures)

        if self.game.status == 'finished':
            self.check_farm_completed(piece.cell, cells_with_pictures)

        if piece.picture in ['city_adjacent', 'city_parallel']:
            self.check_city_completed(piece.cell, cells_with_pictures)

        if piece.picture in ['roads_adjacent', 'roads_parallel', 'crossroad']:
            self.check_road_completed(piece.cell, cells_with_pictures)

    def __add_point(self, cells, cells_in_path, points, follower_type):
        cells_in_path = cells.filter(Q(id__in=cells_in_path) &
                                     Q(piece__follower__isnull=False) &
                                     Q(piece__follower__type=follower_type))
        for cell in cells_in_path:
            player = Player.objects.get(follower=cell.piece.follower)
            player.points += points * cells_in_path.count()
            player.save()
            cell.piece.follower.free_follower()

    def check_farm_completed(self, new_cell, cells_with_pictures):
        graph = Graph(cells_with_pictures.count())
        for cell in cells_with_pictures:
            for side in cell.piece.get_sides():
                side_cell = cell.get_cell_in_side(reverse_side(side), queryset=cells_with_pictures)
                if side_cell:
                    graph.add_edge(cell.id, side_cell.id)

        path = graph.is_cyclic(new_cell.id)
        if path:
            self.__add_point(cells_with_pictures, graph.path, POINTS_FARM_COMPLETED, 'farmer')

    def check_city_completed(self, new_cell, cells_with_pictures):
        cells_with_city = cells_with_pictures.filter(Q(piece__picture__in=['city_adjacent', 'city_parallel']))

        graph = Graph(cells_with_city.count())
        for cell in cells_with_city:
            for side in cell.piece.get_sides():
                side_cell = cell.get_cell_in_side(side, queryset=cells_with_city)
                if side_cell:
                    graph.add_edge(cell.id, side_cell.id)

        path = graph.is_cyclic(new_cell.id)
        if path:
            self.__add_point(cells_with_city, graph.visited, POINTS_CITY_COMPLETED, 'gentleman')

    def check_road_completed(self, new_cell, cells_with_pictures):
        cells_with_roads = cells_with_pictures.filter(Q(piece__picture__in=['roads_adjacent',
                                                                            'roads_parallel',
                                                                            'crossroad']))
        graph = Graph(cells_with_roads.count())
        for cell in cells_with_roads:
            for side in cell.piece.get_sides():
                side_cell = cell.get_cell_in_side(side, queryset=cells_with_roads)
                if side_cell:
                    graph.add_edge(cell.id, side_cell.id)

        path = graph.is_cyclic(new_cell.id)
        if path:
            self.__add_point(cells_with_roads, graph.path, POINTS_ROAD_COMPLETED, 'robber')

    def check_cloister_completed(self, new_cell, cells_with_pictures):
        cells_around = cells_with_pictures.filter(x__in=[new_cell.x - 1, new_cell.x, new_cell.x + 1],
                                                  y__in=[new_cell.y - 1, new_cell.y, new_cell.y + 1],
                                                  game_map=self).exclude(x=new_cell.x, y=new_cell.y)
        if cells_around.filter(piece__picture='cloister').exists():
            cells_with_cloister = cells_around.filter(piece__picture='cloister')
            for cell in cells_with_cloister:

                if hasattr(cell.piece, 'follower') and cell.piece.follower.type == 'monk' and self.__is_cloister_completed(cell, cells_with_pictures):
                    player = Player.objects.filter(follower=cell.piece.follower)
                    player.points += POINTS_CLOISTER_COMPLETED
                    player.save()
                    cell.piece.follower.free_follower()

    def __is_cloister_completed(self, cell, cells_with_pictures):
        cells_around = cells_with_pictures.filter(x__in=[cell.x - 1, cell.x, cell.x + 1],
                                                  y__in=[cell.y - 1, cell.y, cell.y + 1],
                                                  game_map=self).exclude(x=cell.x, y=cell.y)
        return cells_around.count() == 9


class Cell(md.Model):
    x = md.IntegerField()
    y = md.IntegerField()
    game_map = md.ForeignKey(GameMap, on_delete=md.CASCADE)

    def __str__(self):
        return '({},{})'.format(self.x, self.y)

    def has_piece(self):
        return hasattr(self, 'piece')

    def shared_side(self, cell):
        """ posicion de self, respecto de cell"""
        if self.x == cell.x:
            if self.y > cell.y:
                return 'bottom'
            elif self.y < cell.y:
                return 'top'
        if self.y == cell.y:
            if self.x > cell.x:
                return 'right'
            elif self.x < cell.x:
                return 'left'
        return None

    def is_border(self):
        if self.x == 0 or self.x == GAMEMAP_SIZE or self.y == 0 or self.y == GAMEMAP_SIZE:
            return True
        return False

    def get_cell_in_side(self, side, queryset=None):
        if queryset is None:
            queryset = Cell.objects.all()
        try:
            if side == 'left':
                return queryset.get(x=self.x-1, y=self.y)

            if side == 'right':
                return queryset.get(x=self.x+1, y=self.y)

            if side == 'top':
                return queryset.get(x=self.x, y=self.y-1)

            if side == 'bottom':
                return queryset.get(x=self.x, y=self.y+1)
        except Cell.DoesNotExist:
            return None

    def is_enabled(self):
        cells = Cell.objects.filter(Q(piece__isnull=False) & (
                                    Q(x=self.x, y__in=[self.y-1, self.y+1]) |
                                    Q(x__in=[self.x - 1, self.x + 1], y=self.y)) &
                                    Q(game_map=self.game_map)).count()
        return cells != 0


def reverse_side(side):
    if side == 'left':
        return 'right'

    elif side == 'right':
        return 'left'

    elif side == 'top':
        return 'bottom'

    elif side == 'bottom':
        return 'top'


class Piece(md.Model):
    picture = md.CharField(max_length=6, choices=TYPES_PIECE)
    rotation = md.IntegerField(default=0)
    src = md.CharField(max_length=30)
    game = md.ForeignKey(Game, on_delete=md.CASCADE)
    cell = md.OneToOneField(Cell, null=True, blank=True, on_delete=md.CASCADE)

    def __str__(self):
        return self.picture

    def get_sides(self):
        """ retorna los lados donde la pieza debe ser continua"""
        if self.picture == 'cloister' or self.picture == 'crossroad':
            return 'left', 'right', 'top', 'bottom'

        elif self.picture == 'roads_adjacent' or self.picture == 'city_adjacent':
            if self.rotation == 0:
                return 'left', 'bottom'
            elif self.rotation == 90:
                return 'left', 'top'
            elif self.rotation == 180:
                return 'right', 'top'
            elif self.rotation == 270:
                return 'right', 'bottom'

        elif self.picture == 'roads_parallel':
            if self.rotation == 0 or self.rotation == 180:
                return 'top', 'bottom'
            elif self.rotation == 90 or self.rotation == 270:
                return 'left', 'right'

        elif self.picture == 'city_parallel':
            if self.rotation == 0:
                return 'top', 'bottom', 'left'
            elif self.rotation == 90:
                return 'left', 'right', 'top'
            elif self.rotation == 180:
                return 'top', 'bottom', 'right'
            elif self.rotation == 270:
                return 'left', 'right', 'bottom'

    def get_picture_in_side(self, side):
        """ retorna el tipo de lado de la pieza: (cloister, crossroad, roads, city) """
        if self.picture == 'cloister':
            return self.picture
        elif self.picture == 'crossroad':
            return 'roads'

        elif self.picture == 'roads_adjacent' or self.picture == 'city_adjacent':
            if self.rotation == 0:
                if side in ['left', 'bottom']:
                    return self.picture.split('_')[0]
            elif self.rotation == 90:
                if side in ['left', 'top']:
                    return self.picture.split('_')[0]
            elif self.rotation == 180:
                if side in ['right', 'top']:
                    return self.picture.split('_')[0]
            elif self.rotation == 270:
                if side in ['right', 'bottom']:
                    return self.picture.split('_')[0]

        elif self.picture == 'roads_parallel':
            if self.rotation == 0 or self.rotation == 180:
                if side in ['top', 'bottom']:
                    return self.picture.split('_')[0]
            elif self.rotation == 90 or self.rotation == 270:
                if side in ['left', 'right']:
                    return self.picture.split('_')[0]

        elif self.picture == 'city_parallel':
            if self.rotation == 0:
                if side in ['top', 'bottom', 'left']:
                    return self.picture.split('_')[0]
            elif self.rotation == 90:
                if side in ['left', 'right', 'top']:
                    return self.picture.split('_')[0]
            elif self.rotation == 180:
                if side in ['top', 'bottom', 'right']:
                    return self.picture.split('_')[0]
            elif self.rotation == 270:
                if side in ['left', 'right', 'bottom']:
                    return self.picture.split('_')[0]
        return 'farm'

    def is_same_side(self, side, other_piece):
        #  self tiene el lado side igual al other_piece
        if self.get_picture_in_side(side) == other_piece.get_picture_in_side(reverse_side(side)):
            return True
        return False


def check_same_side(old_piece, side, new_piece, other_side):
    """ comprueba que la el lado 'side' de la pieza en el mapa y la nueva sean continuos """
    if side in old_piece.get_sides() or other_side in new_piece.get_sides():
        if old_piece.picture != 'cloister' or new_piece.picture != 'cloister':
            if old_piece.picture in ['roads', 'crossroad'] and new_piece.picture == 'city':
                return False
            if new_piece.picture in ['roads', 'crossroad'] and old_piece.picture == 'city':
                return False
            if side in old_piece.get_sides() and other_side not in new_piece.get_sides():
                return False
            if side not in old_piece.get_sides() and other_side in new_piece.get_sides():
                return False
    return True


class Follower(md.Model):

    type = md.CharField(max_length=10, default='robber', choices=TYPES_FOLLOWER)
    src = md.CharField(max_length=30, default=FOLLOWER_SRC)
    piece = md.OneToOneField(Piece, null=True, blank=True, on_delete=md.CASCADE)
    player = md.ForeignKey(Player, on_delete=md.CASCADE)

    def free_follower(self):
        self.piece = None
        self.save()
