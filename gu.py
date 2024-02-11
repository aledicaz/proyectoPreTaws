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
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

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


def center_window(root, width, height):
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    x_coordinate = (screen_width - width) // 2
    y_coordinate = (screen_height - height) // 2
    root.geometry(f"{width}x{height}+{x_coordinate}+{y_coordinate}")

def start_window():
    start_root = tk.Tk()
    start_root.title("Generador de Melodías")

    # Configura el tamaño de la ventana
    window_width = 800
    window_height = 400
    center_window(start_root, window_width, window_height)

    # Crear un contenedor principal para centrar todo
    main_container = ttk.Frame(start_root)
    main_container.pack(fill=tk.BOTH, expand=True)

    # Cargar la imagen con Pillow, usando una ruta relativa
    image_path = "images/resources/logo.png"  # Ruta relativa a la imagen
    original_image = Image.open(image_path)

    # Ajusta el tamaño de la imagen manteniendo la proporción de aspecto
    aspect_ratio = original_image.width / original_image.height
    new_width = int(window_width * 0.4)  # Ajusta este valor según sea necesario
    new_height = int(new_width / aspect_ratio)
    resized_image = original_image.resize((new_width, new_height), Image.ANTIALIAS)
    
    logo_image = ImageTk.PhotoImage(resized_image)

    # Mostrar la imagen en el contenedor principal
    logo_label = tk.Label(main_container, image=logo_image)
    logo_label.image = logo_image  # Mantén una referencia
    logo_label.pack()

    # Mejora el diseño con un marco para el contenido
    frame = ttk.Frame(main_container, padding="30")
    frame.pack(fill=tk.BOTH, expand=True)

    # Mensaje de bienvenida
    welcome_label = ttk.Label(frame, text="Bienvenido al Generador de Melodías", font=("Arial", 14))
    welcome_label.pack()

    # Instrucciones
    instructions_label = ttk.Label(frame, text="Presiona 'Comenzar' para configurar tu melodía", font=("Arial", 10))
    instructions_label.pack(pady=10)

    # Botón de inicio con un estilo personalizado
    start_button_style = ttk.Style()
    start_button_style.configure("TButton", font=("Arial", 12), padding=10)
    start_button = ttk.Button(frame, text="Comenzar", style="TButton", command=lambda: on_start(start_root))
    start_button.pack(pady=20)

    start_root.mainloop()

def on_start(root):
    root.destroy()  # Cierra la ventana de inicio
    get_user_input()  # Aquí llamas a la función para recoger los parámetros


def get_user_input():
    # Crear una nueva ventana de Tkinter
    root = tk.Tk()
    root.title("Configuración de Generación de Melodía")

    # Diccionario para almacenar los valores de entrada
    inputs = {}

    # Función para recoger los valores y cerrar la ventana
    def submit():
        global num_bars, num_notes, num_steps, pauses, key, scale, root_note, population_size, num_mutations, mutation_probability, bpm
        num_bars = int(num_bars_entry.get())
        num_notes = int(num_notes_entry.get())
        num_steps = int(num_steps_entry.get())
        pauses = pauses_var.get() == 1
        key = key_entry.get()
        scale = scale_entry.get()
        root_note = int(root_note_entry.get())
        population_size = int(population_size_entry.get())
        num_mutations = int(num_mutations_entry.get())
        mutation_probability = float(mutation_probability_entry.get())
        bpm = int(bpm_entry.get())
        root.destroy()

    # Crear y colocar widgets para recoger los parámetros
    ttk.Label(root, text="Número de barras:").grid(row=0, column=0, sticky='w')
    num_bars_entry = ttk.Entry(root)
    num_bars_entry.grid(row=0, column=1)

    ttk.Label(root, text="Número de notas por barra:").grid(row=1, column=0, sticky='w')
    num_notes_entry = ttk.Entry(root)
    num_notes_entry.grid(row=1, column=1)

    ttk.Label(root, text="Número de pasos:").grid(row=2, column=0, sticky='w')
    num_steps_entry = ttk.Entry(root)
    num_steps_entry.grid(row=2, column=1)

    ttk.Label(root, text="Permitir pausas (1=Sí, 0=No):").grid(row=3, column=0, sticky='w')
    pauses_var = tk.IntVar()
    pauses_entry = ttk.Checkbutton(root, variable=pauses_var)
    pauses_entry.grid(row=3, column=1, sticky='w')

    ttk.Label(root, text="Clave musical:").grid(row=4, column=0, sticky='w')
    key_entry = ttk.Entry(root)
    key_entry.grid(row=4, column=1)

    ttk.Label(root, text="Escala musical:").grid(row=5, column=0, sticky='w')
    scale_entry = ttk.Entry(root)
    scale_entry.grid(row=5, column=1)

    ttk.Label(root, text="Nota raíz (entero):").grid(row=6, column=0, sticky='w')
    root_note_entry = ttk.Entry(root)
    root_note_entry.grid(row=6, column=1)

    ttk.Label(root, text="Tamaño de la población:").grid(row=7, column=0, sticky='w')
    population_size_entry = ttk.Entry(root)
    population_size_entry.grid(row=7, column=1)

    ttk.Label(root, text="Número de mutaciones:").grid(row=8, column=0, sticky='w')
    num_mutations_entry = ttk.Entry(root)
    num_mutations_entry.grid(row=8, column=1)

    ttk.Label(root, text="Probabilidad de mutación (0.0 a 1.0):").grid(row=9, column=0, sticky='w')
    mutation_probability_entry = ttk.Entry(root)
    mutation_probability_entry.grid(row=9, column=1)

    ttk.Label(root, text="BPM:").grid(row=10, column=0, sticky='w')
    bpm_entry = ttk.Entry(root)
    bpm_entry.grid(row=10, column=1)

    submit_button = ttk.Button(root, text="Enviar", command=submit)
    submit_button.grid(row=11, column=0, columnspan=2)

    root.mainloop()


    # Devuelve los valores recogidos
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


# Si se ejecuta el script directamente, se inicia el programa principal
if __name__ == '__main__':
    start_window()