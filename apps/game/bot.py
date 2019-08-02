# -*- coding: utf-8 -*-

from random import randint
from time import sleep
from apps.lobby.models import Game, Player
from .models import GameMap, Piece, Cell, Follower
from .constants import FOLLOWER_TYPE, FOLLOWER_FOR_PLAYER


ROTATIONS = [0, 90, 180, 270]


class Bot:
    def __init__(self, url_server, game_id, bot_name='bot'):
        self.bot_name = '{}_({})'.format(bot_name, game_id)
        self.url = url_server
        self.game_id = int(game_id)
        self.player = None

    def start(self):
        self.save_session()
        self.join_game()
        self.player = Player.objects.get(name=self.bot_name, game_id=self.game_id)
        self.create_followerfor_bot()
        while True:
            if self.my_turn():
                self.set_piece()
                if self.game_is_finished():
                    break
            sleep(10)

    def save_session(self):
        player = Player.objects.create(name=self.bot_name, points=0, game_id=self.game_id)
        player.save()

    def join_game(self):
        game = Game.objects.get(id=self.game_id)
        player = Player.objects.get(name=self.bot_name)
        player.game = game
        player.save()
        game.save()

    def create_followerfor_bot(self):
        for i in range(FOLLOWER_FOR_PLAYER):
            f = Follower(player_id=self.player.pk)
            f.save()

    def set_piece(self):
        game_map = GameMap.objects.get(game_id=self.game_id)
        piece = Piece.objects.filter(game_id=self.game_id, cell__isnull=True).order_by('?').first()
        cells_used = []
        found_rotation = False
        while not found_rotation:
            cell = self.__get_free_cell(cells_used)
            if cell is None:
                Game.objects.get(id=self.game_id).change_turno()
                return
            cells_used.append(cell)
            for i in ROTATIONS:
                piece.rotation = i
                piece.save()
                if game_map.check_continuos_side(piece, cell):
                    found_rotation = True
                    break
        if randint(0, 100) % 6 == 0:
            self.set_follower(piece)
        piece.cell = cell
        piece.save()
        cell.save()
        game_map.check_completed(piece)
        Game.objects.get(id=self.game_id).change_turno()

    def __get_free_cell(self, cells_used=[]):
        cells = Cell.objects.filter(game_map__game_id=self.game_id)
        for cell in cells:
            if cell not in cells_used and cell.is_enabled() and not cell.has_piece():
                return cell

        return None

    def game_is_finished(self):
        return Game.objects.filter(id=self.game_id, status='finished').exists()

    def set_follower(self, piece):
        follower = Follower.objects.filter(piece__isnull=True,
                                           player__name=self.bot_name).first()
        follower.type = FOLLOWER_TYPE[piece.picture]
        follower.piece = piece
        follower.save()

    def my_turn(self):
        return Game.objects.get(id=self.game_id).turn == self.player.id
