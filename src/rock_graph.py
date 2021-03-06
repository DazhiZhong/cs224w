import re
import os
import snap
import json

keys = ['C','Db','D','Eb','E','F','Gb','G','Ab','A','Bb','B']

sharps_to_flats = {
    'C#': 'Db',
    'D#': 'Eb',
    'F#': 'Gb',
    'G#': 'Ab',
    'A#': 'Bb',
}

fixings = {
    'o': 'dim',
    'M7': 'maj7',
    'sus': 'sus4',
    '5+': 'aug',
    'maj': '',
    '2': 'sus2',
    'm7add4': 'm11',
    'add13': '6',
    '7-9': '9',
    '7sus': '7sus4',
    '+': 'aug',
    'm7b5': 'm7.5-'
}

# convert minor keys to relative major
def parse_key(key):
    matches = re.search('(.)([#b]?)(m?)', key)
    tonic = matches.group(1)
    accidental = matches.group(2)
    minor = matches.group(3)
    if accidental == '#':
        tonic = sharps_to_flats[tonic + accidental]
    elif accidental == 'b':
        tonic += accidental
    key = tonic
    if minor == 'm':
        major_tonic = keys[(keys.index(tonic) + 3) % 12]
        key = major_tonic
    return key

def parse_chord(chord, key, capo):
    matches = re.search('(.)([#b]?)(.*)', chord)
    root_note = matches.group(1)
    accidental = matches.group(2)
    everything_else = matches.group(3)
    if accidental == '#':
        root_note = sharps_to_flats[root_note + accidental]
    elif accidental == 'b':
        root_note += accidental
    if '/' in everything_else:
        everything_else = everything_else[:everything_else.index('/')] # leave off bass notes

    if capo == 'None':
        capo = 0
    else:
        capo = int(capo)

    key = keys[(keys.index(root_note) + capo - keys.index(key) + 12) % 12]

    return key + (fixings[everything_else] if everything_else in fixings else everything_else)

def read_data():
    chord_set = set()
    edges = []
    edges_by_song = []
    chord_set_by_song = []

    datadir = '../data/song_chords/Rock/'
    for file in os.listdir(datadir):
        song_edges = []
        song_chords = set()

        if file == ".DS_Store":
            continue
        key = None
        capo = None
        for line in open(datadir+file):
            tokens = line.split()
            #print tokens
            if 'Key' in tokens[0]:
                key = parse_key(tokens[0][4:])
                continue
            if 'Capo' in tokens[0]:
                capo = tokens[0][5:]
                continue

            assert(key != None and capo != None)


            chord1 = parse_chord(tokens[0], key, capo)
            chord2 = parse_chord(tokens[1], key, capo)

            chord_set.add(chord1)
            chord_set.add(chord2)
            song_chords.add(chord1)
            song_chords.add(chord2)


            if chord1 != chord2:
                edges.append((chord1, chord2))
                song_edges.append((chord1, chord2))

        edges_by_song.append(song_edges)
        chord_set_by_song.append(song_chords)


    return sorted(chord_set), edges, edges_by_song, chord_set_by_song

if __name__=='__main__':

    chord_set, edges, edges_by_song, chord_set_by_song = read_data()

    G = snap.PNEANet.New()

    chords_dict = {}
    labels = snap.TIntStrH()
    for i, c in enumerate(chord_set):
        labels[i] = c
        chords_dict[c] = i
        G.AddNode(i)

    for edge in edges:
        G.AddEdge(chords_dict[edge[0]], chords_dict[edge[1]])

    print 'num chords', G.GetNodes()
    print 'num edges', len(edges)

    with open('chords_dict_rock.txt', 'w') as file:
        file.write(json.dumps(chords_dict))
    snap.SaveEdgeList(G, "../data/genre_graphs/rock_graph/rock_graph.txt", "Save as tab-separated list of edges")

    # save graphs by song
    for i in range(len(chord_set_by_song)):
        G = snap.PNEANet.New()
        chords = chords_dict #chord_set_by_song[i]
        edges = edges_by_song[i]
        for id,c in enumerate(chord_set):
            G.AddNode(id)
        for edge in edges:
            G.AddEdge(chords_dict[edge[0]], chords_dict[edge[1]])
        snap.SaveEdgeList(G, "../data/song_graphs/rock_graphs/" + str(i) + ".txt", "Save as tab-separated list of edges")
