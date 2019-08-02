from django.test import TestCase, Client

from os import path
from random import randint

from .models import GameMap, Cell, Piece, Follower
from .constants import PIECE_FILES, FOLLOWER_SRC, GAMEMAP_SIZE, AMOUNT_PIECES, PIECE_TYPE_LIST, FOLLOWER_FOR_PLAYER
from .utils import bulk_save

from apps.lobby.models import Game, Player
from carcassonne.settings import STATIC_URL


class PieceModelTest(TestCase):

    def setUp(self):
        Game.objects.create(name='game1').save()
        Piece.objects.create(picture='crossroad', game_id=1, src=PIECE_FILES['crossroad'])

    def test_CreatePiecesRotation(self):
        piece = Piece.objects.get(id=1)
        self.assertEquals(piece.rotation, 0)

    def test_CreatePiecesSrc(self):
        piece = Piece.objects.get(id=1)
        self.assertEquals(piece.src, path.join(STATIC_URL, 'img', 'crossroad.jpeg'))

    def test_CreatePiecesCell(self):
        piece = Piece.objects.get(id=1)
        self.assertNotIsInstance(piece.cell, Cell)

    def test_PiecesGetSides(self):
        piece = Piece.objects.get(id=1)
        self.assertEquals(piece.get_sides(), ('left', 'right', 'top', 'bottom'))


class MapModelTest(TestCase):

    def setUp(self):
        Game.objects.create(name='game1').save()
        GameMap.objects.create(game_id=1).save()

    def test_CreateMap(self):
        if GameMap.objects.filter(game_id=1).exists():
            return
        assert False


class CellModelTest(TestCase):

    def setUp(self):
        Game.objects.create(name='game1').save()
        GameMap.objects.create(game_id=1).save()
        Cell.objects.create(game_map_id=1, x=1, y=1).save()

    def test_CreateCell(self):
        cell = Cell.objects.get(id=1)
        self.assertEqual(cell.x, 1)
        self.assertEqual(cell.y, 1)

    def test_HasPiece(self):
        cell = Cell.objects.get(id=1)
        if not cell.has_piece():
            return
        assert False

    def test_get_cell_in_side(self):
        cell = Cell.objects.get(id=1)
        if not cell.get_cell_in_side('left'):
            if not cell.get_cell_in_side('top'):
                if not cell.get_cell_in_side('bottom'):
                    if not cell.get_cell_in_side('right'):
                        return
        assert False


class FollowerModelTest(TestCase):

    def setUp(self):
        Player.objects.create(name='player').save()
        Follower.objects.create(player_id=1).save()

    def test_CreateFollower(self):
        if Follower.objects.filter(id=1).exists():
            return
        assert False

    def test_srcFollower(self):
        follower = Follower.objects.get(id=1)
        self.assertEqual(follower.src, FOLLOWER_SRC)

    def test_PieceFollower(self):
        follower = Follower.objects.get(id=1)
        self.assertNotIsInstance(follower.piece, Piece)


class GameInitObjectTest(TestCase):

    def setUp(self):
        self.client = Client()
        game = Game.objects.create(name='game name')
        player = Player.objects.create(name='player', game_id=game.pk)
        game.save()
        game.status = 'started'
        game.turn = player.id
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

    def test_game_init_gamemap_created(self):
        if GameMap.objects.filter(id=1).exists():
            return
        assert False

    def test_game_init_cells_created(self):
        if Cell.objects.filter(id=1).exists():
            return
        assert False

    def test_game_init_pieces_created(self):
        if Piece.objects.filter(id=1).exists():
            return
        assert False

    def test_game_init_followers_created(self):
        if Follower.objects.filter(id=1).exists():
            return
        assert False

    def test_game_turn(self):
        game = Game.objects.get(id=1)
        player = Player.objects.get(id=1)
        self.assertEqual(game.turn, player.id)

    def test_amount_cells(self):
        amount_cells = Cell.objects.filter(game_map_id=1).count()
        self.assertEqual(amount_cells, GAMEMAP_SIZE**2)

    def test_amount_pieces(self):
        m = Game.objects.all()
        amount_pieces = Piece.objects.filter(game_id=1).count()
        self.assertEqual(amount_pieces, AMOUNT_PIECES+1)

    def test_piece_city_parallel_exist(self):
        if Piece.objects.filter(picture='city_parallel').exists():
            return
        assert False

    def test_piece_city_adjacent_exist(self):
        if Piece.objects.filter(picture='city_adjacent').exists():
            return
        assert False

    def test_piece_crossroad_exist(self):
        if Piece.objects.filter(picture='crossroad').exists():
            return
        assert False

    def test_piece_roads_parallel_exist(self):
        if Piece.objects.filter(picture='roads_parallel').exists():
            return
        assert False

    def test_piece_roads_adjacent_exist(self):
        if Piece.objects.filter(picture='roads_adjacent').exists():
            return
        assert False

    def test_piece_cloister_exist(self):
        if Piece.objects.filter(picture='cloister').exists():
            return
        assert False


class GameViewsObjectTest(TestCase):

    def setUp(self):
        self.client = Client()
        session = self.client.session
        session['player_name'] = 'player'
        session.save()
        game = Game.objects.create(name='game name')
        player = Player.objects.create(name='player', game_id=game.pk)
        game.save()
        game.status = 'started'
        game.turn = player.id
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

    def test_get_score(self):
        game = Game.objects.get(id=1)
        response = self.client.get('/game/ajax/get_score/{}/'.format(game.id))
        for p in response.json()['players']:
            self.assertEqual(p['points'], 0)

    def test_get_piece(self):
        game = Game.objects.get(id=1)
        response = self.client.get('/game/ajax/get_piece/{}/'.format(game.id))
        if Piece.objects.filter(id=response.json()['piece_id']).exists():
            return
        assert False

    def test_get_turn(self):
        game = Game.objects.get(id=1)
        response = self.client.get('/game/ajax/get_turn/{}/'.format(game.id))
        self.assertEqual(response.status_code, 200)

    def test_get_amount_pieces(self):
        game = Game.objects.get(id=1)
        response = self.client.post('/game/ajax/get_amount_pieces/{}/'.format(game.id))
        self.assertJSONEqual(
            str(response.content, encoding='utf8'),
            {'amount_pieces': str(Piece.objects.filter(game_id=game.id)
                                  .exclude(cell__x=GAMEMAP_SIZE // 2, cell__y=GAMEMAP_SIZE // 2)
                                  .count())}
        )

    def test_set_piece(self):
        game = Game.objects.get(id=1)
        piece = Piece.objects.filter(cell__isnull=True).first()

        response = self.client.post('/game/ajax/set_piece/{}/'.format(game.id),
                                    {'piece_id': piece.id,
                                     'rotation': 90,
                                     'cell': '{},{}'.format(GAMEMAP_SIZE // 2 + 1, GAMEMAP_SIZE // 2)})
        self.assertEqual(Piece.objects.get(id=piece.id).cell.id,
                         Cell.objects.get(y=GAMEMAP_SIZE // 2 + 1, x=GAMEMAP_SIZE // 2).id)

    def test_set_piece_rotation(self):
        game = Game.objects.get(id=1)
        self.client.post('/game/ajax/set_piece_rotation/{}/'.format(game.id),
                         {'piece_id': 1,
                          'rotation': 90})
        piece = Piece.objects.get(id=1)
        self.assertEqual(piece.rotation, 90)

    def test_get_amount_followers(self):
        game = Game.objects.get(id=1)
        response = self.client.get('/game/ajax/get_amount_followers/{}/'.format(game.id))
        self.assertEqual(response.json()['amount_followers'], str(FOLLOWER_FOR_PLAYER))

    def test_get_follower(self):
        game = Game.objects.get(id=1)
        response = self.client.post('/game/ajax/get_follower/{}/'.format(game.id))
        if response.status_code == 200:
            self.assertEqual(response.json()['follower_src'], FOLLOWER_SRC)
            return
        assert False

    def test_set_follower_to_piece(self):
        game = Game.objects.get(id=1)
        follower = Follower.objects.filter(piece__isnull=True).first()
        piece = Piece.objects.filter(cell__isnull=True).first()
        self.client.post('/game/ajax/set_follower_to_piece/{}/'.format(game.id),
                         {'follower_id': follower.id,
                          'piece_id': piece.id,
                          'follower_type': 'farmer'})
        follower = Follower.objects.filter(id=follower.id).first()
        self.assertEqual(follower.piece, piece)
        self.assertEqual(follower.type, 'farmer')

    def test_step(self):
        game = Game.objects.get(id=1)
        player = Player.objects.create(name='player2', game_id=game.id)
        player.save()
        self.client.post('/game/ajax/step/{}/'.format(game.id))
        game = Game.objects.get(id=1)
        self.assertEqual(game.turn, player.id)
