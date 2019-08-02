# -*- coding: utf-8 -*-

from django.http import JsonResponse
from django.shortcuts import render

import sys
from random import randint
from subprocess import Popen

from apps.lobby.models import Game, Player
from apps.lobby.forms import GameForm, PlayerForm
from .models import GameMap, Cell, Piece, Follower
from .forms import GameMapFm, CellFm, PieceFm
from .constants import PIECE_TYPE_LIST, PIECE_FILES, GAMEMAP_SIZE, AMOUNT_PIECES, FOLLOWER_FOR_PLAYER
from .utils import bulk_save


def init_game(request, game_id):
    game = Game.objects.get(id=game_id)
    if GameMap.objects.filter(game=game).exists():
        game_map = GameMap.objects.get(game=game)
        players = Player.objects.filter(game_id=game.pk)

        # Add followers
        if not Player.objects.filter(name=request.session['player_name'], game_id=game_id).exists():
            new_player = Player.objects.get(name=request.session['player_name'], gameid=game_id)
            followers = []
            for i in range(FOLLOWER_FOR_PLAYER):
                followers.append(Follower(player_id=new_player.pk))
            bulk_save(followers)

        context = {
            'game': game,
            'game_map': game_map,
            'cells': Cell.objects.filter(game_map_id=game_map.pk),
            'pieces': Piece.objects.filter(game_id=game.pk),
            'players': players,
            'piece_init': Piece.objects.filter(game_id=game.pk,
                                               cell=Cell.objects.get(x=GAMEMAP_SIZE // 2,
                                                                     y=GAMEMAP_SIZE // 2,
                                                                     game_map_id=game_map.pk)),
            'amount_followers': FOLLOWER_FOR_PLAYER,
        }
    else:
        # create map
        game.status = 'started'
        game.turn = Player.objects.filter(game_id=game.pk).first().id
        game.save()
        game_map = GameMap(game=game)
        game_map.save()

        # create cells of map
        cells = []
        for y in range(GAMEMAP_SIZE):
            for x in range(GAMEMAP_SIZE):
                cells.append(Cell(x=x, y=y, game_map_id=game_map.pk))
        bulk_save(cells)

        # create pieces
        type = lambda: PIECE_TYPE_LIST[randint(0, 5)]
        pieces = []
        for _ in range(AMOUNT_PIECES):
            type_piece = type()
            pieces.append(Piece(picture=type_piece, game_id=game.pk, src=PIECE_FILES[type_piece]))
        bulk_save(pieces)

        type_piece = type()
        piece_init = Piece(picture=type_piece, game_id=game.pk, src=PIECE_FILES[type_piece])
        piece_init.cell = Cell.objects.get(x=GAMEMAP_SIZE // 2, y=GAMEMAP_SIZE // 2, game_map_id=game_map.pk)
        piece_init.save()

        # create followers
        players = Player.objects.filter(game=game.pk)
        amount_players = len(players)
        followers = []
        for i in range(FOLLOWER_FOR_PLAYER * amount_players):
            player = players[i % amount_players]
            followers.append(Follower(player_id=player.pk))
        bulk_save(followers)

        for i in range(1, game.bots+1):
            Popen(['python', 'manage.py', 'bot',
                   '-n bot_{}'.format(i),
                   '-g {}'.format(game_id),
                   '-s {}:{}'.format('http://127.0.0.1', sys.argv[-1])
                   ])

        context = {
            'game': game,
            'game_map': game_map,
            'cells': cells,
            'pieces': pieces,
            'piece_init': piece_init,
            'players': players,
            'amount_followers': FOLLOWER_FOR_PLAYER,
        }
    return render(request, 'game/game.html', context=context)


def __is_your_turn(player_name, game_id):
    game = Game.objects.get(id=game_id)
    return game.is_turn_of(player_name)


def __change_turn(request, game_id):
    game = Game.objects.get(id=game_id)
    game.change_turno()


def get_turn(request, game_id):
    if __is_your_turn(request.session['player_name'], game_id):
        return JsonResponse({}, safe=False)
    return JsonResponse({}, status=404, safe=False)


def get_piece(request, game_id):
    if __is_your_turn(request.session['player_name'], game_id):
        piece = Piece.objects.filter(game_id=game_id, cell__isnull=True).order_by('?').first()
        return JsonResponse({'piece_id': piece.id, 'piece_src': str(piece.src)})
    return JsonResponse({}, status=404, safe=False)


def get_amount_pieces(request, game_id):
    amount_pieces = Piece.objects.filter(game_id=game_id, cell__isnull=True).count()
    return JsonResponse({'amount_pieces': str(amount_pieces)})


def get_score(request, game_id):
    players = Player.objects.filter(game_id=game_id)
    return JsonResponse({'players': list(players.values())})


def set_piece(request, game_id):
    if __is_your_turn(request.session['player_name'], game_id):
        game_finished = False
        y, x = request.POST['cell'].split(',')
        cell = Cell.objects.get(x=int(x), y=int(y), game_map__game_id=game_id)
        if not cell.is_enabled():
            return JsonResponse({'fail_msg': 'Celda aun no disponible'}, safe=False)
        piece = Piece.objects.get(id=request.POST['piece_id'], game_id=game_id)
        if piece.cell is not None:
            return JsonResponse({'fail_msg': 'Pieza ya colocada en una celda'}, safe=False)
        __set_rotation(piece, request.POST['rotation'])
        game_map = GameMap.objects.get(game_id=game_id)
        if cell.has_piece():
            return JsonResponse({'fail_msg': 'Celda ya ocupada'}, safe=False)
        if not game_map.check_continuos_side(piece, cell):
            return JsonResponse({'fail_msg': 'Los lados de la pieza no son continuos'}, safe=False)
        piece.cell = cell
        cell.save()
        piece.save()
        if not Piece.objects.filter(cell__isnull=True).exists():
            game = Game.objects.get(game_id=game_id)
            game.status = 'finished'
            game.save()
            game_finished = True
        game_map.check_completed(piece)
        if game_finished:
            player_winner = Player.objects.filter(game_id=game_id).order_by('points').first()
            return JsonResponse({'success': True,
                                 'game_finished': True,
                                 'player': (player_winner.name, str(player_winner.points))}, safe=False)
        __change_turn(request, game_id)
        return JsonResponse({'success': True}, safe=False)
    return JsonResponse({}, status=404, safe=False)


def set_piece_rotation(request, game_id):
    if __is_your_turn(request.session['player_name'], game_id):
        piece = Piece.objects.get(id=request.POST['piece_id'], game_id=game_id)
        __set_rotation(piece, request.POST['rotation'])
        return JsonResponse({}, safe=False)
    return JsonResponse({}, status=404, safe=False)


def __set_rotation(piece, rotation):
    if not isinstance(rotation, int):
        rotation = int(rotation.replace('position: relative; transform: rotate(', '').replace('deg); z-index: 1;', ''))
    piece.rotation = rotation
    piece.save()


def get_amount_followers(request, game_id):
    amount_followers = Follower.objects.filter(piece__isnull=True,
                                               player__name=request.session['player_name']).count()
    return JsonResponse({'amount_followers': str(amount_followers)})


def get_follower(request, game_id):
    if __is_your_turn(request.session['player_name'], game_id):
        follower = Follower.objects.filter(piece__isnull=True,
                                           player__name=request.session['player_name']).first()
        return JsonResponse({'follower_id': follower.id,
                             'follower_src': follower.src})
    return JsonResponse({}, status=404, safe=False)


def set_follower_to_piece(request, game_id):
    if __is_your_turn(request.session['player_name'], game_id):
        follower = Follower.objects.get(id=request.POST['follower_id'])
        if follower.piece is None:
            piece = Piece.objects.get(id=request.POST['piece_id'], game_id=game_id)
            follower.type = request.POST['follower_type']
            follower.piece = piece
            follower.save()
            piece.save()
            return JsonResponse({}, safe=False)
    return JsonResponse({}, status=404, safe=False)


def step(request, game_id):
    __change_turn(request, game_id)
    return JsonResponse({}, safe=False)


def update_pieces(request, game_id):
    pieces = Piece.objects.filter(cell__isnull=False, game_id=game_id)
    update_pieces = []
    for piece in pieces:
        update_pieces.append((piece.src,
                              '{},{}'.format(piece.cell.y, piece.cell.x),
                              str(piece.rotation)))
    return JsonResponse({'pieces': update_pieces}, safe=False)
