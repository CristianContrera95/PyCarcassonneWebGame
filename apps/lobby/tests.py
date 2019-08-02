from django.test import TestCase, Client
from .models import Game, Player


class PlayerTest(TestCase):

    def setUp(self):
        self.client = Client()

    def test_CreatePlayer(self):
        self.client.post('/save_session/', {'player_name': 'john'})
        if Player.objects.filter(name='john').exists():
            return True
        return False

    def test_DeletePlayer(self):
        self.client.post('/save_session/', {'player_name': 'john'})
        self.client.get('/save_session/')
        if Player.objects.filter(name='john').exists():
            return False
        return True


class LobbyTempletesTest(TestCase):

    def setUp(self):
        self.client = Client()
        self.client.post('/save_session/', {'player_name': 'john'})

    def test_IndexTemplate(self):
        response = self.client.get('/')
        self.assertTemplateUsed(response, "lobby/game_list.html")

    def test_CreateGameTemplate(self):
        response = self.client.get('/game_create/')
        self.assertTemplateUsed(response, "lobby/game_create.html")


class GameModelTest(TestCase):

    def setUp(self):
        Game.objects.create(name='game name').save()

    def test_name_content(self):
        game = Game.objects.get(id=1)
        expected_game_name = game.name
        self.assertEquals(expected_game_name, 'game name')

    def test_status_content(self):
        game = Game.objects.get(id=1)
        expected_game_status = game.status
        self.assertEquals(expected_game_status, 'waiting')
