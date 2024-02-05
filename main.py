import os
import subprocess

# Ruta al directorio que contiene melody_rnn_generate
ruta_magenta_music = os.path.join(os.path.dirname(__file__), 'magentaMusic')

# Agregar la ruta al directorio a la variable de entorno PATH
os.environ["PATH"] += os.pathsep + ruta_magenta_music

# Define las rutas relativas dentro del proyecto
bundle_file = os.path.join(ruta_magenta_music, 'attention_rnn.mag')
output_dir = os.path.join(ruta_magenta_music, 'output')
primer_midi = os.path.join(ruta_magenta_music, 'archivo.mid')

# Define el comando usando rutas relativas
comando = [
    "melody_rnn_generate",
    "--config=attention_rnn",
    f"--bundle_file={bundle_file}",
    f"--output_dir={output_dir}",
    "--num_outputs=10",
    "--num_steps=128",
    f"--primer_midi={primer_midi}"
]

try:
    # Ejecuta el comando en la línea de comandos
    subprocess.run(comando, check=True)
    print("Generación de melodías completada exitosamente.")
except subprocess.CalledProcessError as e:
    print(f"Error al generar melodías: {e}")