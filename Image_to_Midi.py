from PIL import Image
import midiutil
import os
from datetime import datetime  # Importa la clase datetime

# Path to the directory containing images
image_dir = 'C:/Users/Migi/PreTaws/proyectoPreTaws/images'

# Directorio donde se guardarán los archivos MIDI
output_dir = 'C:/Users/Migi/PreTaws/proyectoPreTaws/output_files'

# Crea la carpeta de salida si no existe
os.makedirs(output_dir, exist_ok=True)

# Obtén la fecha y hora actual
current_time = datetime.now()

# Formato de la fecha y hora actual como cadena
timestamp = current_time.strftime("%Y%m%d%H%M%S")

# Nombre del archivo MIDI con el timestamp
midi_file_name = f'output_remidi_{timestamp}.mid'

# Ruta completa al archivo MIDI en la carpeta de salida
midi_file_path = os.path.join(output_dir, midi_file_name)

# Create MIDI file with one track
midi_file = midiutil.MIDIFile(1)

# Add tempo and time signature to track
tempo = 60
time_signature = (4, 4)
midi_file.addTempo(track=0, time=0, tempo=tempo)
midi_file.addTimeSignature(track=0, time=0, numerator=time_signature[0], denominator=time_signature[1], clocks_per_tick=24)

# Loop through each image file in the directory
for filename in os.listdir(image_dir):
    if filename.endswith('.png') or filename.endswith('.jpg') or filename.endswith('.jpeg') or filename.endswith('.gif'):
        # Create the full path to the image file
        image_path = os.path.join(image_dir, filename)

        # Load image
        image = Image.open(image_path)

        # Get dimensions of image
        width, height = image.size

        # Set tempo and time signature
        time_adjustment = 0.03  # seconds per pixel in the image

        # Loop through each row of the image
        for y in range(height):
            # Initialize variables for the current note
            note_pitch = None
            note_start_time = None

            # Loop through each pixel in the row
            for x in range(width):
                # Get the color value of the pixel
                color = image.getpixel((x, y))

                # Check if the pixel is white
                if color[0] == 255 or color[1] == 255 or color[2] == 255:
                    # If this is the first white pixel in the row, start a new note
                    if note_pitch is None:
                        note_pitch = y
                        note_start_time = x
                # If the pixel is not white and a note is currently playing, end the note
                elif note_pitch is not None:
                    note_duration = x - note_start_time
                    note_velocity = 70
                    midi_file.addNote(track=0, channel=0, pitch=note_pitch, time=(note_start_time * time_adjustment),
                                      duration=(note_duration * time_adjustment), volume=note_velocity)
                    note_pitch = None
                    note_start_time = None

            # If a note is still playing at the end of the row, end the note
            if note_pitch is not None:
                note_duration = width - note_start_time
                note_velocity = 70
                midi_file.addNote(track=0, channel=0, pitch=note_pitch,
                                  time=(note_start_time * time_adjustment),
                                  duration=(note_duration * time_adjustment), volume=note_velocity)

# Save the MIDI file with the timestamped name in the output folder
with open(midi_file_path, "wb") as file:
    midi_file.writeFile(file)