import subprocess
import os

#ruta_magenta_music = os.path.join(os.path.dirname(__file__), 'magentaMusic')


# Añade la ruta de magentaMusic al PATH
#os.environ["PATH"] += os.pathsep + ruta_magenta_music

# Define las rutas relativas dentro del proyecto
#bundle_file = os.path.join(ruta_magenta_music, 'attention_rnn.mag')
#output_dir = os.path.join(os.path.dirname(__file__), 'magentaMusic', 'output')
#primer_midi = os.path.join(os.path.dirname(__file__), 'magentaMusic', 'archivo.mid')

#comando = [
#    "melody_rnn_generate",
 #   "--config=attention_rnn",
  #  f"--bundle_file={bundle_file}",
   # f"--output_dir={output_dir}",
    #"--num_outputs=10",
    #"--num_steps=128",
    #f"--primer_midi={primer_midi}"
#]

#try:
 #   subprocess.run(comando, check=True)
  #  print("Generación de melodías completada exitosamente.")
#except subprocess.CalledProcessError as e:
 #   print(f"Error al generar melodías: {e}")


# Ruta al directorio que contiene melody_rnn_generate
ruta_magenta_music = r"C:\Users\Migi\PreTaws\proyectoPreTaws\magentaMusic"

# Agregar la ruta al directorio a la variable de entorno PATH
os.environ["PATH"] += os.pathsep + ruta_magenta_music

# Define la ruta al ejecutable y los argumentos del comando
comando = [
    "melody_rnn_generate",
    "--config=attention_rnn",
    "--bundle_file=C:/Users/Migi/PreTaws/proyectoPreTaws/magentaMusic/attention_rnn.mag",
    "--output_dir=C:/Users/Migi/PreTaws/proyectoPreTaws/magentaMusic/output",
    "--num_outputs=10",
    "--num_steps=128",
    "--primer_midi=C:/Users/Migi/PreTaws/proyectoPreTaws/magentaMusic/archivo.mid"
]

try:
    # Ejecuta el comando en la línea de comandos
    subprocess.run(comando, check=True)
    print("Generación de melodías completada exitosamente.")
except subprocess.CalledProcessError as e:
    print(f"Error al generar melodías: {e}")