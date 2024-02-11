import tkinter as tk
from tkinter import ttk
from datetime import datetime
import os
import time
from midiutil import MIDIFile
from pyo import *
from algorithms.genetic import generate_genome, selection_pair, single_point_crossover, mutation

BITS_PER_NOTE = 4
KEYS = ["C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B"]
SCALES = ["major", "minorM", "dorian", "phrygian", "lydian", "mixolydian", "majorBlues", "minorBlues"]

# Variables globales para almacenar los parámetros de entrada del usuario
global num_bars, num_notes, num_steps, pauses, key, scale, root_note, population_size, num_mutations, mutation_probability, bpm

def collect_inputs():
    # Crear una nueva ventana de Tkinter
    root = tk.Tk()
    root.title("Parámetros de Generación de Melodía")

    # Establecer un estilo (opcional)
    style = ttk.Style()
    style.theme_use('clam')  # Puedes probar diferentes temas: 'alt', 'default', 'clam', 'classic', etc.

    # Función para recoger los valores y cerrar la ventana
    def submit():
        global num_bars, num_notes, num_steps, pauses, key, scale, root_note, population_size, num_mutations, mutation_probability, bpm
        num_bars = int(num_bars_entry.get())
        num_notes = int(num_notes_entry.get())
        num_steps = int(num_steps_entry.get())
        pauses = bool(pauses_var.get())
        key = key_entry.get()
        scale = scale_entry.get()
        root_note = int(root_note_entry.get())
        population_size = int(population_size_entry.get())
        num_mutations = int(num_mutations_entry.get())
        mutation_probability = float(mutation_probability_entry.get())
        bpm = int(bpm_entry.get())
        root.destroy()

    # Crear y colocar widgets para recoger los parámetros
    labels = ['Número de barras:', 'Número de notas por barra:', 'Número de pasos:', 'Permitir pausas (1=Sí, 0=No):',
              'Clave musical:', 'Escala musical:', 'Nota raíz (entero):', 'Tamaño de la población:',
              'Número de mutaciones:', 'Probabilidad de mutación (0.0 a 1.0):', 'BPM:']
    entries = []

    for i, label in enumerate(labels):
        ttk.Label(root, text=label).grid(row=i, column=0, padx=10, pady=5, sticky='w')
    
    num_bars_entry = ttk.Entry(root)
    num_bars_entry.grid(row=0, column=1, padx=10, pady=5)

    num_notes_entry = ttk.Entry(root)
    num_notes_entry.grid(row=1, column=1, padx=10, pady=5)

    num_steps_entry = ttk.Entry(root)
    num_steps_entry.grid(row=2, column=1, padx=10, pady=5)

    pauses_var = tk.IntVar()
    pauses_entry = ttk.Checkbutton(root, variable=pauses_var)
    pauses_entry.grid(row=3, column=1, padx=10, pady=5, sticky='w')

    key_entry = ttk.Entry(root)
    key_entry.grid(row=4, column=1, padx=10, pady=5)

    scale_entry = ttk.Entry(root)
    scale_entry.grid(row=5, column=1, padx=10, pady=5)

    root_note_entry = ttk.Entry(root)
    root_note_entry.grid(row=6, column=1, padx=10, pady=5)

    population_size_entry = ttk.Entry(root)
    population_size_entry.grid(row=7, column=1, padx=10, pady=5)

    num_mutations_entry = ttk.Entry(root)
    num_mutations_entry.grid(row=8, column=1, padx=10, pady=5)

    mutation_probability_entry = ttk.Entry(root)
    mutation_probability_entry.grid(row=9, column=1, padx=10, pady=5)

    bpm_entry = ttk.Entry(root)
    bpm_entry.grid(row=10, column=1, padx=10, pady=5)

    submit_button = ttk.Button(root, text="Enviar", command=submit)
    submit_button.grid(row=11, column=0, columnspan=2, pady=10)

    root.mainloop()

def main():
    # Llama a la función para mostrar la ventana de entrada
    collect_inputs()

    # A partir de aquí, puedes continuar con el resto de tu lógica de programa...
    # El resto de tu código sigue aquí, asegurándote de usar las variables globales donde sea necesario

# Si se ejecuta el script directamente, se inicia el programa principal
if __name__ == '__main__':
    main()