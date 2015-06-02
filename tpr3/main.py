# -*- coding: utf-8 -*-

import math
import numpy as np
import matplotlib
from mpl_toolkits.mplot3d import Axes3D
from numpy.ctypeslib import prep_simple
from dbscan import *


#Данные - Ирисы Фишера
def read_fisher_data(file_name):
    f = open(file_name, 'r')
    input_data = [line.split('\t') for line in f.read().split('\n')]
    data = [((float(line[0]), float(line[1]), float(line[2])), line[4]) for line in input_data]
    data = list(set(data))
    return data


if __name__ == '__main__':

    import matplotlib.pyplot as mpl
    import matplotlib.patches as mpatches

    data = read_fisher_data("input.txt")

    scan = clusterization(0.2, 3)

    scan.dbscan(data)

    clusters = [[scan.data[index].coord for index in cluster] for cluster in scan.clusters]
    clusters.append([scan.data[index].coord for index in scan.noise])

    # Цвета
    colors = mpl.cm.Spectral(np.linspace(0, 1, len(clusters)))

    fig = mpl.figure()
    axis = fig.add_subplot(111, projection='3d')

    negatives = set()
    negatives_count = {}
    clusters_type = {}
    cluster_count = {}

    for i in range(len(clusters)-1):
        negatives = set()
        negatives_count = {}

        for index in scan.clusters[i]:
            dot = scan.data[index]
            if dot.type in negatives_count:
                negatives_count[dot.type] += 1
            else:
                negatives_count[dot.type] = 0


        clusters_type[i] = list(negatives_count.keys())[list(negatives_count.values()).index(max(negatives_count.values()))]
        cluster_count[i] = max(negatives_count.values())

    negatives = set()
    negatives_count = {}

    cluster_colors = {}

    legend_colors = []
    legend_names = []

    for dot in scan.data:
        if dot.cluster_id == -1:
            col = 'k'
            mar = '.'
            size = 10
        else:
            col = colors[dot.cluster_id]
            cluster_colors[dot.cluster_id] = col
            mar = 'o'
            size = 25

        negatives.add(dot.type)
        if dot.type in negatives_count:
            negatives_count[dot.type] += 1
        else:
            negatives_count[dot.type] = 0

        axis.scatter(dot.coord[0], dot.coord[1], dot.coord[2], c=col, marker=mar, s=size)

    for i in range(len(scan.clusters)):
        legend_colors.append(matplotlib.lines.Line2D([0],[0], linestyle="none", c=cluster_colors[i], marker = 'o'))

        presicion = cluster_count[i] / len(scan.clusters[i])

        recall = cluster_count[i] / negatives_count[clusters_type[i]]

        f = 2 * ((presicion * recall) / (presicion + recall))

        print("№%d Cluster:" % (i+1))
        print("Presicion: %f" % presicion)
        print("Recall: %f" % recall)
        print("F1: %f" % f)


    axis.legend(legend_colors, [str(i+1) for i in range(len(scan.clusters))], numpoints = 1)
    mpl.show()

