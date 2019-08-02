# -*- coding: utf-8 -*-
from django import forms as fm

from .models import GameMap, Cell, Piece


class GameMapFm(fm.ModelForm):

    class Meta:
        model = GameMap
        fields = '__all__'


class CellFm(fm.ModelForm):

    class Meta:
        model = Cell
        fields = '__all__'


class PieceFm(fm.ModelForm):

    class Meta:
        model = Piece
        fields = '__all__'
