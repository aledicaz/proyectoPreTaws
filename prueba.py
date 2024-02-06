import subprocess
import os

ruta_magenta_music = os.path.join(os.path.dirname(__file__), 'magentaMusic')
midi_dir = os.path.join(os.path.dirname(__file__), 'midi_dir')


# Añade la ruta de magentaMusic al PATH
os.environ["PATH"] += os.pathsep + ruta_magenta_music

# Define las rutas relativas dentro del proyecto
bundle_file = os.path.join(ruta_magenta_music, 'attention_rnn.mag')
output_dir = os.path.join(os.path.dirname(__file__), 'magentaMusic', 'output')

# Obtener la última subcarpeta en midi_dir
subfolders = sorted([f.path for f in os.scandir(midi_dir) if f.is_dir()], key=os.path.getmtime, reverse=True)
if subfolders:
    last_subfolder = subfolders[0]
else:
    print("No hay subcarpetas en midi_dir.")
    exit()
  

# Obtener la última subcarpeta en la última subcarpeta
subsubfolders = sorted([f.path for f in os.scandir(last_subfolder) if f.is_dir()], key=os.path.getmtime, reverse=True)

if subsubfolders:
    last_subsubfolder = subsubfolders[0]
    print(f"Archivos en la subcarpeta {last_subsubfolder}:")
    midi_files = [entry.path for entry in os.scandir(last_subsubfolder) if entry.is_file() and entry.name.endswith('.mid')][:2]

    for midi_file in midi_files:
        # Construir la ruta para la subcarpeta en output_dir
        subfolder_name = os.path.relpath(midi_file, midi_dir)  # Obtener la ruta relativa al midi_dir
        output_subdir = os.path.join(output_dir, subfolder_name)

        print(f"Creando subcarpeta {output_subdir} para {midi_file}")

        # Crear directorio para cada archivo .mid en output_dir
        os.makedirs(output_subdir, exist_ok=True)

        # Resto del código para ejecutar el comando y guardar las generaciones en output_subdir
        comando = [
            "melody_rnn_generate",
            "--config=attention_rnn",
            f"--bundle_file={bundle_file}",
            f"--output_dir={output_subdir}",
            "--num_outputs=10",
            "--num_steps=128",
            f"--primer_midi={midi_file}"
        ]

        try:
            subprocess.run(comando, check=True)
            print(f"Generación de melodías completada exitosamente para {midi_file} en {output_subdir}.")
        except subprocess.CalledProcessError as e:
            print(f"Error al generar melodías para {midi_file}: {e}")
        
else:
    print(f"No hay subcarpetas en {last_subfolder}.")
    exit()


"""
# Procesar los dos primeros archivos .mid en la última subcarpeta
midi_files = [f.name for f in os.scandir(last_subsubfolder) if f.is_file() and f.name.endswith('.mid')][:2]

# Crear subcarpeta para cada archivo .mid en output_dir
for midi_file in midi_files:
    # Crear directorio para cada archivo .mid en output_dir
    output_subdir = os.path.join(output_dir, os.path.basename(last_subfolder), os.path.basename(last_subsubfolder), os.path.splitext(midi_file)[0])
    os.makedirs(output_subdir, exist_ok=True)

    # Ruta completa al archivo .mid de entrada
    input_midi = os.path.join(last_subsubfolder, midi_file)

    # Ruta completa al primer archivo .mid de entrada
    primer_midi = os.path.join(output_subdir, midi_file)

    # Comando para generar melodías
    comando = [
        "melody_rnn_generate",
        "--config=attention_rnn",
        f"--bundle_file={bundle_file}",
        f"--output_dir={output_subdir}",
        "--num_outputs=10",
        "--num_steps=128",
        f"--primer_midi={primer_midi}"
    ]

    try:
        subprocess.run(comando, check=True)
        print(f"Generación de melodías completada exitosamente para {midi_file} en {output_subdir}.")
    except subprocess.CalledProcessError as e:
        print(f"Error al generar melodías para {midi_file}: {e}")
        
"""