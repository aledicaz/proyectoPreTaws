import subprocess
import os

# Ruta al directorio que contiene melody_rnn_generate
ruta_magenta_music = r"C:\Users\Migi\magentaMusic"

# Agregar la ruta al directorio a la variable de entorno PATH
os.environ["PATH"] += os.pathsep + ruta_magenta_music

# Define la ruta al ejecutable y los argumentos del comando
comando = [
    "melody_rnn_generate",
    "--config=attention_rnn",
    "--bundle_file=C:/Users/Migi/magentaMusic/attention_rnn.mag",
    "--output_dir=C:/Users/Migi/magentaMusic/output",
    "--num_outputs=10",
    "--num_steps=128",
    "--primer_midi=archivo.mid"
]

try:
    # Ejecuta el comando en la línea de comandos
    subprocess.run(comando, check=True)
    print("Generación de melodías completada exitosamente.")
except subprocess.CalledProcessError as e:
    print(f"Error al generar melodías: {e}")