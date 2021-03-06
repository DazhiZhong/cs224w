import sys
import json
import snap

with open('chords_dict_jazz.txt', 'r') as file:
     dict = (json.load(file))
     chords_dict_jazz = {v: k for k, v in dict.iteritems()}


with open('chords_dict_rock.txt', 'r') as file:
     dict = (json.load(file))
     chords_dict_rock = {v: k for k, v in dict.iteritems()}

def load_genre_graphs(graph):
    if graph == "rock":
        filename = '../data/genre_graphs/rock_graph/rock_graph.txt'
        dict = chords_dict_rock
    else:
        filename = '../data/genre_graphs/jazz_graph/jazz_graph.txt'
        dict = chords_dict_jazz

    G_Multi = snap.LoadEdgeList(snap.PNEANet, filename, 0, 1)
    G_Directed = snap.LoadEdgeList(snap.PNGraph, filename, 0, 1)
    G_Undirected = snap.LoadEdgeList(snap.PUNGraph, filename, 0, 1)

    #return G_Multi, G_Directed, G_Undirected, dict
    return snap.GetKCore(G_Multi, 3), snap.GetKCore(G_Directed, 3), snap.GetKCore(G_Undirected, 3), dict
