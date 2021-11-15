from music21 import *
import os
from MarkovChain import *


def generate_music():
    directory_name = "musicInput"

    order = 2
    number_notes = 1000
    xml_data = import_music_xml(directory_name)
    melody_data = get_melody_data(xml_data)
    rhythm_data = get_rhythm_data(xml_data)
    #chord_stream = get_chord_data(xml_data)

    test_melody_rhythm_data = get_joint_melody_rhythm_data(xml_data)
    melody_sequence, rhythm_sequence = generate_music_melody_rhythm(test_melody_rhythm_data, order, number_notes)

    stream2 = stream.Stream()
    test_count = 0
    for note_name in melody_sequence:
        if note_name == "R":
            n = note.Rest()
        else:
            n = note.Note(note_name)

        if str(rhythm_sequence[test_count]) == "complex":
            n.duration = duration.Duration("quarter")
        else:
            n.duration = duration.Duration(rhythm_sequence[test_count])
        test_count += 1
        stream2.append(n)

    stream2.timeSignature = meter.TimeSignature('4/4')
    # stream2.keySignature = key.Key('e-')
    # stream2.show()

    s2 = stream.Score(id='mainScore')
    s2.insert(0, stream2)
    #s2.insert(chord_stream)
    s2.show()

    melody_sequence = generate_melody(melody_data, order, number_notes)
    rhythm_sequence = generate_rhythm("MARKOV", rhythm_data, order, number_notes)

    stream1 = stream.Stream()
    test_count = 0
    for note_name in melody_sequence:
        if note_name == "R":
            n = note.Rest()
        else:
            n = note.Note(note_name)

        n.duration = duration.Duration(rhythm_sequence[test_count])
        test_count += 1
        stream1.append(n)

    stream1.timeSignature = meter.TimeSignature('12/8')
    stream1.keySignature = key.Key('e-')

    s = stream.Score(id='mainScore')

    p0 = stream1
    # p1 = chord_stream

    s.insert(0, p0)
    # s.insert(0, p1)
    s.show()


def import_music_xml(directory_name: str) -> list:
    """
    Retrieves all MusicXML documents from specified directory and places them in a list
    """
    xml_data = []
    for file in os.listdir(directory_name):
        if file.endswith(".xml") or file.endswith(".mxl") or file.endswith(".mid"):
            xml_data.append(converter.parse(directory_name + '/' + file))  # Converts MusicXML to a music21 stream

    return xml_data


def get_melody_data(xml_data: list) -> list:
    """
    Creates a list containing data about each note from a stream which will be used in markov chain generation
    xml_data is a list of music21 streams created from imported MusicXML data
    """
    melody_data = []
    rhythm_data = []

    for file in xml_data:
        p = file.parts[0].getElementsByClass(
            stream.Measure)
        # Take the treble clef only from each file (should be melody)
        for n in file.parts[0].recurse().notesAndRests:
            rhythm_data.append(n.duration)
            if type(n) is note.Note:
                melody_data.append(n.pitch)
            if type(n) is note.Rest:
                melody_data.append("R")  # R for rest
            if type(n) is chord.Chord:
                melody_data.append(n.root())

    return melody_data


def get_chord_data(xml_data: list):
    """
    Creates a list containing data about each note from a stream which will be used in markov chain generation
    xml_data is a list of music21 streams created from imported MusicXML data
    """
    melody_data = []
    rhythm_data = []

    for file in xml_data:
        for n in file.parts[1].recurse().notesAndRests:
            rhythm_data.append(n.duration)
            if type(n) is note.Note:
                melody_data.append(n)
            if type(n) is note.Rest:
                melody_data.append("R")  # R for rest
            if type(n) is chord.Chord:
                melody_data.append(n)

    stream1 = stream.Stream()
    test_count = 0
    for note_name in melody_data:
        if note_name == "R":
            n = note.Rest()
        else:
            n = note_name
        n.duration = rhythm_data[test_count]
        test_count += 1
        stream1.append(n)

    stream1.timeSignature = meter.TimeSignature('12/8')
    stream1.keySignature = key.Key('e-')

    # stream1chords = stream1.chordify()
    # stream1chords.show()
    return stream1


def get_rhythm_data(xml_data: list) -> list:
    rhythm_data = []

    for file in xml_data:
        for n in file.parts[0].recurse().notesAndRests:
            rhythm_data.append(n.duration.type)

    return rhythm_data


def get_joint_melody_rhythm_data(xml_data: list) -> list:
    """
    Creates a list containing data about the note pitch and duration concatenated with a comma
    """
    melody_data = []
    rhythm_data = []

    for file in xml_data:
        for n in file.parts[0].recurse().notesAndRests:
            rhythm_data.append(n.duration)
            if type(n) is note.Note:
                melody_data.append(str(n.pitch) + "," + str(n.duration.type))
            if type(n) is note.Rest:
                melody_data.append("R" + "," + str(n.duration.type))  # R for rest
            if type(n) is chord.Chord:
                melody_data.append(str(n.root()) + "," + str(n.duration.type))

    return melody_data


def generate_music_melody_rhythm(melody_data: list, order: int, number_notes: int):
    melody_markov_chain = MarkovChain(order, melody_data)
    melody_markov_chain.create_transition_matrix()

    melody_note_sequence = melody_markov_chain.generate_sequence("", number_notes)

    melody_note_sequence_reduced = [x.split("|") for x in melody_note_sequence]

    melody_note_sequence_main = [x[order - 1] for x in melody_note_sequence_reduced]
    melody_note_sequence_start = melody_note_sequence_reduced[0][0:order - 1]
    melody_sequence = melody_note_sequence_start + melody_note_sequence_main
    melody_sequence = [x.split(",") for x in melody_sequence]

    return [x[0] for x in melody_sequence], [x[1] for x in melody_sequence]


def generate_melody(melody_data: list, order: int, number_notes: int) -> list:
    """
    Generates melody pitches using a Markov chain
    """
    melody_markov_chain = MarkovChain(order, melody_data)
    melody_markov_chain.create_transition_matrix()

    melody_note_sequence = melody_markov_chain.generate_sequence("", number_notes)

    melody_note_sequence_reduced = [x.split("|") for x in melody_note_sequence]
    melody_note_sequence_main = [x[order - 1] for x in melody_note_sequence_reduced]
    melody_note_sequence_start = melody_note_sequence_reduced[0][0:order - 1]
    melody_sequence = melody_note_sequence_start + melody_note_sequence_main

    return melody_sequence


def generate_rhythm(mode: str, rhythm_data: list, order: int, number_notes: int):
    """
    Generates rhythm based on specified mode
    """
    if mode == "MARKOV":  # Rhythm generated by Markov chain independent of melody
        rhythm_markov_chain = MarkovChain(order, rhythm_data)
        rhythm_markov_chain.create_transition_matrix()

        rhythm_sequence = rhythm_markov_chain.generate_sequence("", number_notes)

        rhythm_sequence_reduced = [x.split("|") for x in rhythm_sequence]
        rhythm_sequence_main = [x[order - 1] for x in rhythm_sequence_reduced]

        rhythm_sequence_start = rhythm_sequence_reduced[0][0:order - 1]
        rhythm_sequence = rhythm_sequence_start + rhythm_sequence_main

        return rhythm_sequence
    elif mode == "ORIGINAL":  # Uses original rhythm data, cannot produce sequence longer than original piece for now.
        return rhythm_data
    print()


if __name__ == '__main__':
    generate_music()
