# -*- coding: utf-8 -*-


from collections import defaultdict
from django.db.transaction import atomic


@atomic
def bulk_save(items):
    for i in items:
        i.save()


class Graph:

    def __init__(self, vertices):
        self.V = vertices  # No. of vertices
        self.graph = defaultdict(list)
        self.visited = {}
        self.path = []
        self.init = -1

    def add_edge(self, v, w):
        if w not in self.graph[v]:
            self.graph[v].append(w)
        if v not in self.graph[w]:
            self.graph[w].append(v)
        self.visited[v] = False
        self.visited[w] = False

    def is_cyclic_util(self, v, parent):

        self.visited[v] = True
        self.path.append(v)
        for i in self.graph[v]:
            if not self.visited[i]:
                if self.is_cyclic_util(i, v):
                    return True
                else:
                    self.path = self.path[:-1]
            elif parent != i:
                if i == self.init:
                    return True
                return False

        return False

    def is_cyclic(self, init):
        self.init = init
        if self.is_cyclic_util(init, -1):
            return True
        return False
