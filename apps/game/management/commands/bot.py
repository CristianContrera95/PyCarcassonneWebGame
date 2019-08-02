# -*- coding: utf-8 -*-

from django.core.management.base import BaseCommand

from apps.game.bot import Bot


class Command(BaseCommand):

    def add_arguments(self, parser):
        parser.add_argument('-s', help="url_server:port")
        parser.add_argument('-g', help="game_id")
        parser.add_argument('-n', help="bot_name")

    def handle(self, *args, **kwargs):
        url_server = kwargs['s']
        game_id = kwargs['g']
        bot_name = kwargs['n']

        bot = Bot(url_server=url_server, game_id=game_id, bot_name=bot_name)

        bot.start()
