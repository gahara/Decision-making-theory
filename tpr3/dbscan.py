import math
import numpy as np

class my_dot:
    def __init__(self, coords, type):
        self.id = None
        self.coord = coords
        self.neighbours = set()
        self.overlooked = False
        self.cluster_id = None
        self.type = type

    def calc_3d_dist(self, dot):
        
        return math.pow(sum(map(lambda x, y: (x-y)**2, dot.coord, self.coord)), 0.5)

class clusterization:
    def __init__(self, eps, min_pts):
        self.eps = eps
        self.min_pts = min_pts
        self.data = []
        self.clusters = []
        self.noise = []

        self.clusters_numb = 0

#ищем непосредственно-достижимые точки
    def find_neighbours(self):
        for dot_searcher in self.data:
            for dot in self.data:
                if dot_searcher.id != dot.id and dot_searcher.calc_3d_dist(dot) <= self.eps:
                    dot_searcher.neighbours.add(dot.id)

    def dbscan(self, data):
        for i in range(len(data)):
            dot = my_dot(data[i][0], data[i][1])
            dot.id = i
            self.data.append(dot)
        
        self.find_neighbours()

        for dot in self.data:
            if not dot.overlooked:
                dot.overlooked = True
                if len(dot.neighbours) < self.min_pts:
                    dot.cluster_id = -1
                else:
                    #создаем кластер
                    self.clusters.append([])
                    self.clusters_numb += 1
                    #расщиряем кластер
                    self.expand_cluster(dot)

    def expand_cluster(self, dot):
        self.clusters[-1].append(dot.id)
        dot.cluster_id = self.clusters_numb - 1

        flag = False

        i = 0
        while (i < len(dot.neighbours)):
            i = 0
            for index in dot.neighbours:

                neighbored_dot = self.data[index]

                if not neighbored_dot.overlooked:
                    neighbored_dot.overlooked = True
                    if len(neighbored_dot.neighbours) >= self.min_pts:
                        dot.neighbours = dot.neighbours.union(neighbored_dot.neighbours)
                        flag = True

                if neighbored_dot.cluster_id == None or neighbored_dot.cluster_id == -1:
                    self.clusters[-1].append(neighbored_dot.id)
                    neighbored_dot.cluster_id = self.clusters_numb-1

                if flag:
                    flag = False
                    break

                i += 1