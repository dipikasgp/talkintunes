import datetime

from talkintunes.messages.note_mapping import punctuation_rest_mapping, musical_notes_mapping
from music21 import *
import os
from pydub import AudioSegment


def midi_to_mp3(midi_file, soundfont, mp3_file):
    wav_file = mp3_file.replace('.mp3', '.wav')
    os.system(f'fluidsynth -ni {soundfont} {midi_file} -F {wav_file} -r 44100')

    audio = AudioSegment.from_wav(wav_file)
    audio.export(mp3_file, format='mp3')

    os.remove(wav_file)
    os.remove(midi_file)


def text_to_note(text, user):
    notes = []

    for letter in text:
        if letter in punctuation_rest_mapping:
            punc_note = note.Note(punctuation_rest_mapping[letter])
            # punc_note.duration = Duration('16th')
            notes.append(punc_note)
        else:
            note_name = musical_notes_mapping.get(letter, None)
            notes.append(note.Note(note_name))

    melody_stream = stream.Stream()
    melody_stream.append(instrument.Sitar())  # Add a piano instrument

    for n in notes:
        melody_stream.append(n)

    cwd = os.getcwd()
    folder_path = os.path.join(cwd, 'talkintunes\\temp')
    os.makedirs(folder_path, exist_ok=True)
    midi_filename = f"{user.id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.mid"
    midi_filepath = os.path.join(cwd, 'talkintunes\\temp', midi_filename)
    melody_stream.write('midi', fp=midi_filepath)
    soundfont = os.path.join(cwd, 'default_sound_font.sf2')
    mp3_file_name = f"{user.id}_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}.mp3"
    mp3_file_path = os.path.join(cwd, 'talkintunes\\static', mp3_file_name)
    midi_to_mp3(midi_filepath, soundfont, mp3_file_path)
    return mp3_file_name
