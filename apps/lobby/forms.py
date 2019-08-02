# -*- coding: utf-8 -*-

from django import forms as fm

from .models import Game, Player


class GameForm(fm.ModelForm):

    class Meta:
        model = Game

        fields = ['name', 'bots']
        labels = {
            'name': 'Nombre',
            'bots': 'Bots',
        }
        widgets = {
            'name': fm.TextInput(attrs={'class': 'form-control form-inline'}),
            'bots': fm.Select(attrs={'class': 'form-control form-inline'})
        }


class PlayerForm(fm.ModelForm):

    class Meta:
        model = Player

        fields = '__all__'
