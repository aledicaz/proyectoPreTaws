import os
import re
from music21 import *
from PIL import Image
from Midi_to_Images import extract_arrays_from_midi_file
from Midi_to_Images import create_piano_roll_image
from datetime import datetime  


def get_recent_subfolder(midi_dir):
    subfolder_pattern = '^\d+$'  # Patrón para seleccionar carpetas numeradas
    subfolders = [f for f in os.listdir(midi_dir) if os.path.isdir(os.path.join(midi_dir, f)) and re.match(subfolder_pattern, f)]
    subfolders.sort(key=lambda x: int(x))  # Ordenar carpetas numéricamente
    if subfolders:
        recent_subfolder = os.path.join(midi_dir, subfolders[-1])  # Tomar la carpeta más reciente
        return recent_subfolder
    else:
        return None

def obtener_dos_primeros_archivos(carpeta_principal):
    # Obtener subcarpetas numeradas
    subfolders = [f for f in os.listdir(carpeta_principal) if os.path.isdir(os.path.join(carpeta_principal, f)) and f.isdigit()]

    if not subfolders:
        print("No se encontraron subcarpetas numeradas.")
        return None, None

    # Ordenar las subcarpetas numéricamente y obtener la última
    latest_subfolder = max(subfolders, key=int)

    # Obtener la lista de archivos en la subcarpeta más reciente
    subfolder_path = os.path.join(carpeta_principal, latest_subfolder)
    files_in_subfolder = [f for f in os.listdir(subfolder_path) if os.path.isfile(os.path.join(subfolder_path, f))]

    if len(files_in_subfolder) < 2:
        print(f"No hay suficientes archivos en la subcarpeta {latest_subfolder}.")
        return None, None

    # Tomar los dos primeros archivos
    first_two_files = files_in_subfolder[:2]

    # Ruta completa de los archivos
    full_paths = [os.path.join(subfolder_path, file) for file in first_two_files]

    return full_paths, latest_subfolder

def main():
    # Ruta del directorio principal
    midi_dir = r'C:\Users\Migi\PreTaws\proyectoPreTaws\midi_dir'
    image_dir = r'C:\Users\Migi\PreTaws\proyectoPreTaws\images'

    # Obtener la carpeta más reciente y su nombre
    recent_subfolder = get_recent_subfolder(midi_dir)

    if recent_subfolder:
        # Obtener los dos primeros archivos de la carpeta más reciente y el nombre de la subcarpeta
        midi_files, subfolder_name = obtener_dos_primeros_archivos(recent_subfolder)

        if midi_files:
            # Iterar sobre los archivos MIDI y generar imágenes
            for midi_file in midi_files:
                # Extraer arreglos del archivo MIDI
                pitches, durations, start_times, parts = extract_arrays_from_midi_file(midi_file)

                # Crear la imagen de rollo de piano
                piano_roll_image = create_piano_roll_image(pitches, durations, start_times, parts, midi_file)

                # Construir la ruta de la carpeta de imágenes
                subfolder_image_dir = os.path.join(image_dir, os.path.basename(recent_subfolder))

                # Crear la carpeta de imágenes si no existe
                os.makedirs(subfolder_image_dir, exist_ok=True)

                # Guardar la imagen en la carpeta de imágenes
                image_name = os.path.splitext(os.path.basename(midi_file))[0] + '_visual.png'
                image_path = os.path.join(subfolder_image_dir, image_name)
                piano_roll_image.save(image_path)

if __name__ == "__main__":
    main()

