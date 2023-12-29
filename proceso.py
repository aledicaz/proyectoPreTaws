import os

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
midi_dir = r'C:\Users\Migi\PreTaws\proyectoPreTaws\midi_dir\1703868003'
archivos = obtener_dos_primeros_archivos(midi_dir)

if archivos:
    print("Dos primeros archivos en la subcarpeta más reciente:", archivos)