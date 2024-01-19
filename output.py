import os
import re
import midiutil
from music21 import *
from PIL import Image
from Midi_to_Images import extract_arrays_from_midi_file, create_piano_roll_image
from datetime import datetime

script_dir = os.path.dirname(os.path.abspath(__file__))

def get_recent_subfolder(images_dir):
    subfolder_pattern = '^\d+$'
    subfolders = [f for f in os.listdir(images_dir) if os.path.isdir(os.path.join(images_dir, f)) and re.match(subfolder_pattern, f)]
    subfolders.sort(key=lambda x: int(x), reverse=True)
    if subfolders:
        return os.path.join(images_dir, subfolders[0])
    else:
        return None

def main():
    # Rutas de directorios
    images_dir = os.path.join(script_dir, 'images')
    output_dir = os.path.join(script_dir, 'output_files')

    # Obtener la subcarpeta más reciente
    recent_subfolder = get_recent_subfolder(images_dir)

    if recent_subfolder:
        # Ruta completa de la subcarpeta más reciente
        recent_subfolder_path = os.path.join(images_dir, recent_subfolder)

        # Crear la carpeta de salida si no existe
        os.makedirs(output_dir, exist_ok=True)

        # Crear una subcarpeta en output_files con el mismo nombre que la carpeta de imágenes
        output_subfolder = os.path.join(output_dir, recent_subfolder)
        os.makedirs(output_subfolder, exist_ok=True)

        # Obtener la fecha y hora actual
        current_time = datetime.now()
        timestamp = current_time.strftime("%Y%m%d%H%M%S")

        # Obtener el nombre de la subcarpeta actual (correspondiente a la generación de imágenes)
        subfolder_name = os.path.basename(recent_subfolder)

        # Crear una subcarpeta dentro de output_files con el nombre de la subcarpeta actual
        output_subfolder = os.path.join(output_dir, subfolder_name)

        # Crear la carpeta de salida si no existe
        os.makedirs(output_subfolder, exist_ok=True)

        # Nombre del archivo MIDI con el timestamp
        midi_file_name = f'output_remidi_{timestamp}.mid'

        # Ruta completa al archivo MIDI en la subcarpeta de salida
        midi_file_path = os.path.join(output_subfolder, midi_file_name)


        # Crear el archivo MIDI con un track
        midi_file = midiutil.MIDIFile(1)
        tempo = 60
        time_signature = (4, 4)
        midi_file.addTempo(track=0, time=0, tempo=tempo)
        midi_file.addTimeSignature(track=0, time=0, numerator=time_signature[0], denominator=time_signature[1], clocks_per_tick=24)

        # Loop a través de cada archivo de imagen en la subcarpeta más reciente
        for filename in os.listdir(recent_subfolder_path):
            if filename.endswith('.png') or filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.gif'):
                # Crear la ruta completa al archivo de imagen
                image_path = os.path.join(recent_subfolder_path, filename)

                # Cargar la imagen
                image = Image.open(image_path)

                # Obtener dimensiones de la imagen
                width, height = image.size

                # Ajuste de tiempo
                time_adjustment = 0.04

                # Loop a través de cada fila de la imagen
                for y in range(height):
                    note_pitch = None
                    note_start_time = None

                    # Loop a través de cada píxel en la fila
                    for x in range(width):
                        color = image.getpixel((x, y))

                        if color[0] == 255 or color[1] == 255 or color[2] == 255:
                            if note_pitch is None:
                                note_pitch = y
                                note_start_time = x
                        elif note_pitch is not None:
                            note_duration = x - note_start_time
                            note_velocity = 70
                            midi_file.addNote(track=0, channel=0, pitch=note_pitch, time=(note_start_time * time_adjustment),
                                              duration=(note_duration * time_adjustment), volume=note_velocity)
                            note_pitch = None
                            note_start_time = None

                    # Si hay una nota aún sonando al final de la fila, finaliza la nota
                    if note_pitch is not None:
                        note_duration = width - note_start_time
                        note_velocity = 70
                        midi_file.addNote(track=0, channel=0, pitch=note_pitch,
                                          time=(note_start_time * time_adjustment),
                                          duration=(note_duration * time_adjustment), volume=note_velocity)

        # Guardar el archivo MIDI en la carpeta de salida
        with open(midi_file_path, "wb") as file:
            midi_file.writeFile(file)

if __name__ == "__main__":
    main()