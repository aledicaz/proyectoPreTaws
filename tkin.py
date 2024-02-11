import click
import tkinter as tk
from tkinter import simpledialog
from datetime import datetime
from typing import List, Dict
from midiutil import MIDIFile
from pyo import *
from algorithms.genetic import generate_genome, Genome, selection_pair, single_point_crossover, mutation
import random
import os
import time

BITS_PER_NOTE = 4
KEYS = ["C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B"]
SCALES = ["major", "minorM", "dorian", "phrygian", "lydian", "mixolydian", "majorBlues", "minorBlues"]


def int_from_bits(bits: List[int]) -> int:
    return int(sum([bit * pow(2, index) for index, bit in enumerate(bits)]))


def genome_to_melody(genome: Genome, num_bars: int, num_notes: int, num_steps: int,
                     pauses: int, key: str, scale: str, root: int) -> Dict[str, list]:
    notes = [genome[i * BITS_PER_NOTE:i * BITS_PER_NOTE + BITS_PER_NOTE] for i in range(num_bars * num_notes)]

    note_length = 4 / float(num_notes)

    scl = EventScale(root=key, scale=scale, first=root)

    melody = {
        "notes": [],
        "velocity": [],
        "beat": []
    }

    for note in notes:
        integer = int_from_bits(note)

        if not pauses:
            integer = int(integer % pow(2, BITS_PER_NOTE - 1))

        if integer >= pow(2, BITS_PER_NOTE - 1):
            melody["notes"] += [0]
            melody["velocity"] += [0]
            melody["beat"] += [note_length]
        else:
            if len(melody["notes"]) > 0 and melody["notes"][-1] == integer:
                melody["beat"][-1] += note_length
            else:
                melody["notes"] += [integer]
                melody["velocity"] += [127]
                melody["beat"] += [note_length]

    steps = []
    for step in range(num_steps):
        steps.append([scl[(note + step * 2) % len(scl)] for note in melody["notes"]])

    melody["notes"] = steps
    return melody


def genome_to_events(genome: Genome, num_bars: int, num_notes: int, num_steps: int,
                     pauses: bool, key: str, scale: str, root: int, bpm: int) -> [Events]:
    melody = genome_to_melody(genome, num_bars, num_notes, num_steps, pauses, key, scale, root)

    return [
        Events(
            midinote=EventSeq(step, occurrences=1),
            midivel=EventSeq(melody["velocity"], occurrences=1),
            beat=EventSeq(melody["beat"], occurrences=1),
            attack=0.001,
            decay=0.05,
            sustain=0.5,
            release=0.005,
            bpm=bpm
        ) for step in melody["notes"]
    ]


def fitness(genome: Genome, s: Server, num_bars: int, num_notes: int, num_steps: int,
            pauses: bool, key: str, scale: str, root: int, bpm: int) -> int:
    m = metronome(bpm)

    events = genome_to_events(genome, num_bars, num_notes, num_steps, pauses, key, scale, root, bpm)
    for e in events:
        e.play()
    s.start()

    # Crear una ventana principal de Tkinter
    root = tk.Tk()
    root.withdraw()

    # Utilizar simpledialog en la ventana principal
    rating = simpledialog.askinteger("Rating", "Rating (0-5): ")

    for e in events:
        e.stop()
    s.stop()
    time.sleep(1)

    try:
        rating = int(rating)
    except ValueError:
        rating = 0

    return rating


def metronome(bpm: int):
    met = Metro(time=1 / (bpm / 60.0)).play()
    t = CosTable([(0, 0), (50, 1), (200, .3), (500, 0)])
    amp = TrigEnv(met, table=t, dur=.25, mul=1)
    freq = Iter(met, choice=[660, 440, 440, 440])
    return Sine(freq=freq, mul=amp).mix(2).out()


def save_genome_to_midi(filename: str, genome: Genome, num_bars: int, num_notes: int, num_steps: int,
                        pauses: bool, key: str, scale: str, root: int, bpm: int):
    melody = genome_to_melody(genome, num_bars, num_notes, num_steps, pauses, key, scale, root)

    if len(melody["notes"][0]) != len(melody["beat"]) or len(melody["notes"][0]) != len(melody["velocity"]):
        raise ValueError

    mf = MIDIFile(1)

    track = 0
    channel = 0

    time = 0.0
    mf.addTrackName(track, time, "Sample Track")
    mf.addTempo(track, time, bpm)

    for i, vel in enumerate(melody["velocity"]):
        if vel > 0:
            for step in melody["notes"]:
                mf.addNote(track, channel, step[i], time, melody["beat"][i], vel)

        time += melody["beat"][i]

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "wb") as f:
        mf.writeFile(f)


def get_user_input():
    root = tk.Tk()
    root.withdraw()

    num_bars = simpledialog.askinteger("Parámetro", "Número de barras:", minvalue=1)
    num_notes = simpledialog.askinteger("Parámetro", "Número de notas por barra:", minvalue=1)
    num_steps = simpledialog.askinteger("Parámetro", "Número de pasos:", minvalue=1)
    pauses = simpledialog.askinteger("Parámetro", "¿Permitir pausas? (0 para no, 1 para sí):", minvalue=0, maxvalue=1)
    key = simpledialog.askstring("Parámetro", "Clave musical:", initialvalue="C")
    scale = simpledialog.askstring("Parámetro", "Escala musical:", initialvalue="major")
    root_note = simpledialog.askinteger("Parámetro", "Nota raíz (entero):")
    population_size = simpledialog.askinteger("Parámetro", "Tamaño de la población:", minvalue=1)
    num_mutations = simpledialog.askinteger("Parámetro", "Número de mutaciones:", minvalue=0)
    mutation_probability = simpledialog.askfloat("Parámetro", "Probabilidad de mutación (0.0 a 1.0):", minvalue=0.0, maxvalue=1.0)
    bpm = simpledialog.askinteger("Parámetro", "BPM:", minvalue=1)

    return num_bars, num_notes, num_steps, pauses, key, scale, root_note, population_size, num_mutations, mutation_probability, bpm


def main():
    num_bars, num_notes, num_steps, pauses, key, scale, root_note, population_size, num_mutations, mutation_probability, bpm = get_user_input()

    folder = os.path.join("midi_dir", str(int(datetime.now().timestamp())))

    population = [generate_genome(num_bars * num_notes * BITS_PER_NOTE) for _ in range(population_size)]

    s = Server().boot()

    population_id = 0

    running = True
    while running:
        random.shuffle(population)

        population_fitness = [(genome, fitness(genome, s, num_bars, num_notes, num_steps, pauses, key, scale, root_note, bpm))
                              for genome in population]

        sorted_population_fitness = sorted(population_fitness, key=lambda e: e[1], reverse=True)

        population = [e[0] for e in sorted_population_fitness]

        next_generation = population[0:2]

        for j in range(int(len(population) / 2) - 1):

            def fitness_lookup(genome):
                for e in population_fitness:
                    if e[0] == genome:
                        return e[1]
                return 0

            parents = selection_pair(population, fitness_lookup)
            offspring_a, offspring_b = single_point_crossover(parents[0], parents[1])
            offspring_a = mutation(offspring_a, num=num_mutations, probability=mutation_probability)
            offspring_b = mutation(offspring_b, num=num_mutations, probability=mutation_probability)
            next_generation += [offspring_a, offspring_b]

        print(f"Población {population_id} lista")

        events = genome_to_events(population[0], num_bars, num_notes, num_steps, pauses, key, scale, root_note, bpm)
        for e in events:
            e.play()
        s.start()
        simpledialog.messagebox.showinfo("Primera mejor melodía generada", "Esta es la primera mejor melodía generada")
        s.stop()
        for e in events:
            e.stop()

        time.sleep(1)

        events = genome_to_events(population[1], num_bars, num_notes, num_steps, pauses, key, scale, root_note, bpm)
        for e in events:
            e.play()
        s.start()
        simpledialog.messagebox.showinfo("Segunda mejor melodía generada", "Esta es la segunda mejor melodía generada")
        s.stop()
        for e in events:
            e.stop()

        time.sleep(1)

        print("Guardando la población midi...")
        for i, genome in enumerate(population):
            save_genome_to_midi(f"{folder}/{population_id}/{scale}-{key}-{i}.mid", genome, num_bars, num_notes,
                                num_steps, pauses, key, scale, root_note, bpm)
        print("¡Listo!")

        running = simpledialog.askstring("Continuar", "¿Deseas continuar? [Y/n]: ") != "n"
        population = next_generation
        population_id += 1


# Si se ejecuta el script directamente, se inicia el comando de línea de comandos de Click
if __name__ == '__main__':
    main()