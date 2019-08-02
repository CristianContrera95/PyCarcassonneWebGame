# -*- coding: utf-8 -*-

from django.db import models as md


class Game(md.Model):
    """ class with the data of the game """
    STATUS = [('waiting', 'Waiting'),
              ('started', 'Started'),
              ('finished', 'Finished')]
    BOTS = ((0, 0), (1, 1), (2, 2), (3, 3))
    name = md.CharField(max_length=20, unique=True)
    status = md.CharField(max_length=20, default='waiting', choices=STATUS)
    turn = md.IntegerField(default=-1)
    bots = md.IntegerField(default=0, choices=BOTS)

    def __str__(self):
        return '{} ({})'.format(self.name, self.status)

    def is_turn_of(self, player_name):
        player = Player.objects.get(id=self.turn)
        return player_name == player.name

    def change_turno(self):
        players = Player.objects.filter(game=self).order_by('id')
        new_player = None
        for p in players:
            if p.id > self.turn:
                new_player = p
                break
        if not new_player:
            new_player = players.first()
        self.turn = new_player.id
        self.save()

    class Meta:
        ordering = ('name', 'status')


class Player(md.Model):
    name = md.CharField(max_length=20, unique=True)
    points = md.IntegerField(default=0)
    game = md.ForeignKey(Game, null=True, blank=True, on_delete=md.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['name']
