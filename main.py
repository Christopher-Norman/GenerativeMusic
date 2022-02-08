from music21 import *
import os
from MarkovChain import *


def generate_music():
    directory_name = "musicInput"
    # directory_name = input("Input data directory location:\n")

    xml_data = import_music_xml(directory_name)
    # chord_stream = get_chord_data(xml_data)

    number_notes = int(input("Number of notes to generate:"))

    print("Choose generation method:\n\t1. Combined rhythm and melody model\n\t2. Independent rhythm and melody\n\t3. "
          "Uniform random melody")
    generation_method = int(input())

    output_stream = stream.Stream()

    if generation_method == 1:  # Combined rhythm and melody model
        order = int(input("Order of Markov chain (>0): "))
        melody_rhythm_data = get_joint_melody_rhythm_data(xml_data)
        melody_sequence, rhythm_sequence = generate_music_melody_rhythm(melody_rhythm_data, order, number_notes)

    elif generation_method == 2:  # Independent rhythm and melody model
        print("Choose method of rhythm generation:\n\tMARKOV\n\tORIGINAL\n\tCONSTANT")
        rhythm_generation_method = input()
        order = int(input("Order of melody Markov Chain (>0): "))

        rhythm_order = 1  # Default rhythm Markov chain order
        if rhythm_generation_method == "MARKOV":
            rhythm_order = int(input("Order of rhythm Markov chain (>0): "))

        rhythm_data = get_rhythm_data(xml_data)
        rhythm_sequence = generate_rhythm(rhythm_generation_method, rhythm_data, rhythm_order, number_notes)
        melody_data = get_melody_data(xml_data)
        melody_sequence = generate_melody(melody_data, order, number_notes)

    elif generation_method == 3:  # Uniform random sample
        melody_rhythm_data = get_joint_melody_rhythm_data(xml_data)
        melody_sequence, rhythm_sequence = generate_music_uniform(melody_rhythm_data, 1, number_notes)

    note_count = 0
    for note_name in melody_sequence:
        if note_name == "R":
            n = note.Rest()
        else:
            n = note.Note(note_name)

        if str(rhythm_sequence[note_count]) == "complex":
            n.duration = duration.Duration("16th")
        else:
            n.duration = duration.Duration(rhythm_sequence[note_count])

        n.duration = duration.Duration(rhythm_sequence[note_count])
        note_count += 1
        output_stream.append(n)

    output_stream.timeSignature = meter.TimeSignature('4/4')
    # output_stream.keySignature = key.Key('e-')

    output_stream.show()
    # s = stream.Score(id='mainScore')
    # mm1 = tempo.MetronomeMark(number=40)
    # s.append(mm1)

    p0 = output_stream
    # p1 = chord_stream

    # s.insert(0, output_stream)
    # s.insert(0, p1)
    # s.show()


def import_music_xml(directory_name: str) -> list:
    """
    Retrieves all MusicXML documents from specified directory and places them in a list
    """
    xml_data = []
    for file in os.listdir(directory_name):
        if file.endswith(".xml") or file.endswith(".mxl") or file.endswith(".mid") or file.endswith(".abc"):
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
    """

    :param xml_data: data from XML or other supported formats
    :return: rhythm_data: a list containing types of note duration eg "Quarter", "16th"
    """
    rhythm_data = []

    for file in xml_data:
        for n in file.parts[0].recurse().notesAndRests:  # Recurse through each note in each file
            n.duration.linked = False
            rhythm_data.append(n.duration.type)  # Gets the duration type of each note

    return rhythm_data


def get_joint_melody_rhythm_data(xml_data: list) -> list:
    """
    Creates a list containing data about the note pitch and duration concatenated with a comma
    """
    melody_data = []
    rhythm_data = []

    for file in xml_data:
        for n in file.parts[0].recurse().notesAndRests:
            n.duration.linked = False
            rhythm_data.append(n.duration)
            if type(n) is note.Note:
                melody_data.append(str(n.pitch) + "," + str(n.duration.type))
            if type(n) is note.Rest:
                melody_data.append("R" + "," + str(n.duration.type))  # R for rest
            if type(n) is chord.Chord:
                melody_data.append(str(n.root()) + "," + str(n.duration.type))

    return melody_data


def generate_music_melody_rhythm(melody_data: list, order: int, number_notes: int):
    """
    Generates melody and its rhythm in a single Markov chain
    :param melody_data:
    :param order: Markov chain order
    :param number_notes: Number of notes to be generated in the sequence
    :return: Returns two lists, one containing pitch data and the second containing note duration data
    """
    melody_markov_chain = MarkovChain(order, melody_data)
    melody_markov_chain.create_transition_matrix()

    melody_note_sequence = melody_markov_chain.generate_sequence(number_notes)

    melody_note_sequence_reduced = [x.split("|") for x in melody_note_sequence]

    melody_note_sequence_main = [x[order - 1] for x in melody_note_sequence_reduced]
    melody_note_sequence_start = melody_note_sequence_reduced[0][0:order - 1]
    melody_sequence = melody_note_sequence_start + melody_note_sequence_main
    melody_sequence = [x.split(",") for x in melody_sequence]

    return [x[0] for x in melody_sequence], [x[1] for x in melody_sequence]


def generate_melody(melody_data: list, order: int, number_notes: int) -> list:
    """
    Generates melody pitches using a Markov chain independent of the rhythm
    """
    melody_markov_chain = MarkovChain(order, melody_data)
    melody_markov_chain.create_transition_matrix()

    melody_note_sequence = melody_markov_chain.generate_sequence(number_notes)

    melody_note_sequence_reduced = [x.split("|") for x in melody_note_sequence]
    melody_note_sequence_main = [x[order - 1] for x in melody_note_sequence_reduced]
    melody_note_sequence_start = melody_note_sequence_reduced[0][0:order - 1]
    melody_sequence = melody_note_sequence_start + melody_note_sequence_main

    return melody_sequence


def generate_rhythm(mode: str, rhythm_data: list, order: int, number_notes: int) -> list:
    """"
    Generates rhythm based on specified mode, independent of melody/pitch data.

    :param mode: String specifying which mode the rhythm will be generated using
    :param rhythm_data:
    :param order:
    :param number_notes: Number of notes to be generated
    :return:
    """
    if mode == "MARKOV":  # Rhythm generated by Markov chain independent of melody
        rhythm_markov_chain = MarkovChain(order, rhythm_data)
        rhythm_markov_chain.create_transition_matrix()

        # Add 20 extra notes to compensate for difference in Markov chain length
        rhythm_sequence = rhythm_markov_chain.generate_sequence(number_notes + 20)

        rhythm_sequence_reduced = [x.split("|") for x in rhythm_sequence]
        rhythm_sequence_main = [x[order - 1] for x in rhythm_sequence_reduced]

        rhythm_sequence_start = rhythm_sequence_reduced[0][0:order - 1]
        rhythm_sequence = rhythm_sequence_start + rhythm_sequence_main

        return rhythm_sequence
    elif mode == "ORIGINAL":  # Uses original rhythm data, cannot produce sequence longer than original piece for now.
        return rhythm_data
    elif mode == "CONSTANT":  # Uses a constant Eighth note
        print("Choose note length:\n\t1. quarter note\n\t2. half note\n\t3. 16th note")
        rhythm_generation_method = int(input())
        rhythm_sequence = ['eighth'] * (number_notes + 20)
        return rhythm_sequence


def generate_music_uniform(melody_data: list, order: int, number_notes: int):
    """
    Generates melody and its rhythm in a single Markov chain using uniform random sample
    :param melody_data: list of notes and their duration
    :param order: Markov chain order
    :param number_notes: Number of notes to be generated in the sequence
    :return: Returns two lists, one containing pitch data and the second containing note duration data
    """
    melody_markov_chain = MarkovChain(order, melody_data)
    melody_markov_chain.create_transition_matrix()

    #  This time do not use Markov transition matrix and instead uniform random
    melody_note_sequence = melody_markov_chain.generate_uniform_random_sequence(number_notes)

    melody_note_sequence_reduced = [x.split("|") for x in melody_note_sequence]

    melody_note_sequence_main = [x[order - 1] for x in melody_note_sequence_reduced]
    melody_note_sequence_start = melody_note_sequence_reduced[0][0:order - 1]
    melody_sequence = melody_note_sequence_start + melody_note_sequence_main
    melody_sequence = [x.split(",") for x in melody_sequence]

    return [x[0] for x in melody_sequence], [x[1] for x in melody_sequence]


if __name__ == '__main__':
    print("MARKOV CHAIN MUSIC GENERATOR\n")
    generate_music()
