import os
import re

def get_recent_subfolder(midi_dir):
    subfolder_pattern = '^\d+$'  # Patrón para seleccionar carpetas numeradas
    subfolders = [f for f in os.listdir(midi_dir) if os.path.isdir(os.path.join(midi_dir, f)) and re.match(subfolder_pattern, f)]
    subfolders.sort(key=lambda x: int(x))  # Ordenar carpetas numéricamente
    if subfolders:
        recent_subfolder = os.path.join(midi_dir, subfolders[-1])  # Tomar la carpeta más reciente
        return recent_subfolder
    else:
        return None

# Uso de la función
midi_dir = r'C:\Users\Migi\PreTaws\proyectoPreTaws\midi_dir'
recent_subfolder = get_recent_subfolder(midi_dir)

def obtener_dos_primeros_archivos(carpeta_principal):
    # Obtener subcarpetas numeradas
    subfolders = [f for f in os.listdir(carpeta_principal) if os.path.isdir(os.path.join(carpeta_principal, f)) and f.isdigit()]

    if not subfolders:
        print("No se encontraron subcarpetas numeradas.")
        return None

    # Ordenar las subcarpetas numéricamente y obtener la última
    latest_subfolder = max(subfolders, key=int)

    # Obtener la lista de archivos en la subcarpeta más reciente
    subfolder_path = os.path.join(carpeta_principal, latest_subfolder)
    files_in_subfolder = [f for f in os.listdir(subfolder_path) if os.path.isfile(os.path.join(subfolder_path, f))]

    if len(files_in_subfolder) < 2:
        print(f"No hay suficientes archivos en la subcarpeta {latest_subfolder}.")
        return None

    # Tomar los dos primeros archivos
    first_two_files = files_in_subfolder[:2]

    # Ruta completa de los archivos
    full_paths = [os.path.join(subfolder_path, file) for file in first_two_files]

    return full_paths

# Uso de la función
archivos = obtener_dos_primeros_archivos(recent_subfolder)

if archivos:
    print("Dos primeros archivos en la subcarpeta más reciente:", archivos)