# -*- coding: utf-8 -*-

from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.db.models import Count, Q
from django.views.generic import ListView, CreateView, TemplateView, DeleteView
from django.urls import reverse_lazy, reverse

from .models import Game, Player
from .forms import GameForm, PlayerForm


def save_session(request):
    if request.method == 'GET':
        try:
            Player.objects.get(name=request.session['player_name']).delete()
            del request.session['player_name']
        except KeyError:
            pass
    else:
        player_name = request.POST['player_name']
        request.session['player_name'] = player_name
        if Player.objects.filter(name=player_name).exists():
            context = {'conflic_name': True}
            return render(request, 'lobby/game_list.html', context=context)
        playerfm = PlayerForm({'name': player_name, 'points': 0})
        if playerfm.is_valid():
            playerfm.save()
    return render(request, 'lobby/game_list.html')


class GameList(ListView):
    model = Game
    template_name = 'lobby/game_list.html'
    form_class = GameForm


class GameCreate(CreateView):
    model = Game
    form_class = GameForm
    template_name = 'lobby/game_create.html'

    def get_success_url(self):
        return reverse('lobby:game_waiting', args=(self.object.id,))


class GameWaiting(TemplateView):
    model = Game
    template_name = 'lobby/game_waiting.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data()
        players_in_game = Player.objects.filter(game_id=kwargs['game_id'])
        context['players_name'] = players_in_game
        context['game'] = Game.objects.get(id=kwargs['game_id'])
        if 'creador' in kwargs:
            context['creador'] = True
        return context

    def get(self, request, *args, **kwargs):
        player_name = request.session['player_name']
        player = Player.objects.get(name=player_name)
        game = Game.objects.get(id=kwargs['game_id'])
        player.game = game
        player.save()
        return super().get(request, *args, **kwargs)


class GameDelete(DeleteView):
    pass
#     model = Game
#     template_name = 'lobby/game_list.html'
#     success_url = reverse_lazy('lobby:index')

