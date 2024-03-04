from flask import Flask, request, render_template, redirect, url_for, session
import os
import pygame.midi
from time import sleep
from datetime import datetime
from typing import List, Dict
from midiutil import MIDIFile
from pyo import *
import os
import subprocess
from music21 import converter, note, chord
from PIL import Image
from Midi_to_Images import extract_arrays_from_midi_file, create_piano_roll_image
from algorithms.genetic import generate_genome, Genome, selection_pair, single_point_crossover, mutation
import os
import typer
import openai
from dotenv import load_dotenv
import shutil


load_dotenv()

openai.api_key = os.getenv("OPENAI_KEY")
BITS_PER_NOTE = 4
KEYS = ["C", "C#", "Db", "D", "D#", "Eb", "E", "F", "F#", "Gb", "G", "G#", "Ab", "A", "A#", "Bb", "B"]
SCALES = ["major", "minorM", "dorian", "phrygian", "lydian", "mixolydian", "majorBlues", "minorBlues"]
s = Server().boot()
ruta_magenta_music = os.path.join(os.path.dirname(__file__), 'magentaMusic')
bundle_file = os.path.join(ruta_magenta_music, 'chord_pitches_improv.mag')



app = Flask(__name__)
app.secret_key = 'proyectoTaws'  # Necesaria para usar sesiones


def limpiar_directorios():
    directorios = [
        r'C:\Users\Migi\PreTaws\proyectoPreTaws\static\magenta',
        r'C:\Users\Migi\PreTaws\proyectoPreTaws\static\midi_dir\favoritas',
        r'C:\Users\Migi\PreTaws\proyectoPreTaws\static\imgs\imgs_midi'
    ]
    
    for directorio in directorios:
        # Verificar si el directorio existe para evitar errores si la ruta no existe
        if os.path.exists(directorio):
            for archivo in os.listdir(directorio):
                file_path = os.path.join(directorio, archivo)
                try:
                    if os.path.isfile(file_path) or os.path.islink(file_path):
                        os.unlink(file_path)
                    elif os.path.isdir(file_path):
                        shutil.rmtree(file_path)
                except Exception as e:
                    print(f'Error al eliminar {file_path}. Razón: {e}')
        else:
            print(f'El directorio {directorio} no existe y se omitirá.')

def generate_lyrics(mood: str, prompt: str):
    # Puedes ajustar esto según tus necesidades
    # Agregar más parámetros si es necesario
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Estás generando letras de canciones basadas en frases clave y emociones dadas."},
            {"role": "user", "content": f"Genera una letra de canción sobre el tema de {mood} utilizando la frase clave '{prompt}'. La canción debe expresar {mood}."},
        ]
    )
    generated_lyrics = response["choices"][0]["message"]["content"]

    return generated_lyrics

def play_midi_file(filename):
    pygame.midi.init()
    player = pygame.midi.Output(0)
    player.open_midi_file(filename)
    player.play_midi_file()
    player.close_midi_file()
    pygame.midi.quit()

def int_from_bits(bits: List[int]) -> int:
    return int(sum([bit*pow(2, index) for index, bit in enumerate(bits)]))


def genome_to_melody(genome: Genome, num_bars: int, num_notes: int, num_steps: int,
                     pauses: int, key: str, scale: str, root: int) -> Dict[str, list]:
    notes = [genome[i * BITS_PER_NOTE:i * BITS_PER_NOTE + BITS_PER_NOTE] for i in range(num_bars * num_notes)]

    note_length = 4 / float(num_notes)

    scl = EventScale(root=key, scale=scale, first=root)

    melody = {
        "notes": [],
        "velocity": [],
        "beat": []
    }

    for note in notes:
        integer = int_from_bits(note)

        if not pauses:
            integer = int(integer % pow(2, BITS_PER_NOTE - 1))

        if integer >= pow(2, BITS_PER_NOTE - 1):
            melody["notes"] += [0]
            melody["velocity"] += [0]
            melody["beat"] += [note_length]
        else:
            if len(melody["notes"]) > 0 and melody["notes"][-1] == integer:
                melody["beat"][-1] += note_length
            else:
                melody["notes"] += [integer]
                melody["velocity"] += [127]
                melody["beat"] += [note_length]

    steps = []
    for step in range(num_steps):
        steps.append([scl[(note+step*2) % len(scl)] for note in melody["notes"]])

    melody["notes"] = steps
    return melody


def genome_to_events(genome: Genome, num_bars: int, num_notes: int, num_steps: int,
                     pauses: bool, key: str, scale: str, root: int, bpm: int) -> [Events]:
    melody = genome_to_melody(genome, num_bars, num_notes, num_steps, pauses, key, scale, root)

    return [
        Events(
            midinote=EventSeq(step, occurrences=1),
            midivel=EventSeq(melody["velocity"], occurrences=1),
            beat=EventSeq(melody["beat"], occurrences=1),
            attack=0.001,
            decay=0.05,
            sustain=0.5,
            release=0.005,
            bpm=bpm
        ) for step in melody["notes"]
    ]





def metronome(bpm: int):
    met = Metro(time=1 / (bpm / 60.0)).play()
    t = CosTable([(0, 0), (50, 1), (200, .3), (500, 0)])
    amp = TrigEnv(met, table=t, dur=.25, mul=1)
    freq = Iter(met, choice=[660, 440, 440, 440])
    return Sine(freq=freq, mul=amp).mix(2).out()


def save_genome_to_midi(filename: str, genome: Genome, num_bars: int, num_notes: int, num_steps: int,
                        pauses: bool, key: str, scale: str, root: int, bpm: int):
    melody = genome_to_melody(genome, num_bars, num_notes, num_steps, pauses, key, scale, root)

    if len(melody["notes"][0]) != len(melody["beat"]) or len(melody["notes"][0]) != len(melody["velocity"]):
        raise ValueError

    mf = MIDIFile(1)

    track = 0
    channel = 0

    time = 0.0
    mf.addTrackName(track, time, "Sample Track")
    mf.addTempo(track, time, bpm)

    for i, vel in enumerate(melody["velocity"]):
        if vel > 0:
            for step in melody["notes"]:
                mf.addNote(track, channel, step[i], time, melody["beat"][i], vel)

        time += melody["beat"][i]

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, "wb") as f:
        mf.writeFile(f)



@app.route('/')
def index():
    limpiar_directorios()
    session['poblacion_id']=0
    session['population_id']=0
    session['population_fitness'] = []
    return render_template('index.html')

@app.route('/generar', methods=['POST'])
def generar():
    # Captura los valores del formulario
    session["num_bars"] = request.form.get('num_bars', type=int)
    session["num_notes"] = request.form.get('num_notes', type=int)
    session["num_steps"] = request.form.get('num_steps', type=int)
    session["tonica"] = request.form.get('tonica', type=int)
    session["prob_mutacion"] = request.form.get('prob_mutacion', type=float)
    session["incluir_pausas"] = request.form.get('incluir_pausas') == 'true'
    session["tonalidad"] = request.form.get('tonalidad')
    session["escala"] = request.form.get('escala')
    session["tamaño_poblacion"] = request.form.get('tamaño_poblacion', type=int)
    session["num_mutaciones"] = request.form.get('num_mutaciones', type=int)
    return redirect(url_for('procesar_genoma'))
    
@app.route('/pagina1', methods=['POST'])
def pagina1():
    # Captura los valores del formulario
    
    nombre = request.form.get('name')
    session["nombre"] = nombre
    return render_template('pagina1.html', data= nombre)

@app.route('/procesar_genoma')
def procesar_genoma():
    num_bars= session.get('num_bars')
    num_notes= session.get('num_notes')
    # num_steps = session.get('num_steps')
    # incluir_pausas = session.get('incluir_pausas')
    # tonalidad = session.get('tonalidad')
    # escala = session.get('escala')
    # tonica = session.get('tonica')
    tamaño_poblacion = session.get('tamaño_poblacion')
    
    # folder = os.path.join("midi_dir", str(int(datetime.now().timestamp())))

    population = [generate_genome(num_bars * num_notes * BITS_PER_NOTE) for _ in range(tamaño_poblacion)]
    session['population'] = population
    return redirect(url_for('continuar_proceso'))

@app.route('/continuar_proceso')
def continuar_proceso():
    num_bars= session.get('num_bars')
    num_notes= session.get('num_notes')
    num_steps = session.get('num_steps')
    incluir_pausas = session.get('incluir_pausas')
    tonalidad = session.get('tonalidad')
    escala = session.get('escala')
    tonica = session.get('tonica')
    bpm= 128
    id_poblacion = session.get('poblacion_id')
    population = session.get('population')
    if id_poblacion < len(population):
        genome= population[id_poblacion]
        session['genoma_actual']= genome
        
        id_poblacion += 1
        session['poblacion_id']=id_poblacion
        
        return redirect(url_for('ejecutar_sonido'))
        
    else:
        session['poblacion_id'] = 0
        return render_template('pagina3.html')



    
    
@app.route('/calificar', methods=['POST'])
def calificar():
   
    genome = session.get('genoma_actual')
    s.stop()
    # Extrae el valor del slider del formulario
    rating = request.form.get('rating', type=int)
    population_fitness = session.get('population_fitness')
    tuple_gr = (genome,rating)
    population_fitness.append(tuple_gr)
    session['population_fitness'] = population_fitness
    return redirect(url_for('continuar_proceso'))


@app.route('/ejecutar_sonido')
def ejecutar_sonido():
    num_bars= session.get('num_bars')
    num_notes= session.get('num_notes')
    num_steps = session.get('num_steps')
    incluir_pausas = session.get('incluir_pausas')
    tonalidad = session.get('tonalidad')
    escala = session.get('escala')
    tonica = session.get('tonica')
    bpm= 128
    genome = session.get('genoma_actual')
    events= genome_to_events(genome, num_bars, num_notes, num_steps, incluir_pausas, tonalidad, escala, tonica, bpm)
    nombre = session.get('nombre')
    def play_sound():
        s.start()
        for e in events:
            e.play()

        # Wait for all the events to finish playing
        sleep(2*num_bars)

        for e in events:
            e.stop()
        s.stop()
    thread = threading.Thread(target=play_sound)
    thread.start()
    return render_template('pagina2.html', data= nombre)

@app.route('/generar_mas_sonidos', methods=['POST'])
def generar_mas_sonidos():
    population_fitness = session.get('population_fitness')
    population_id = session.get('population_id')
    num_bars= session.get('num_bars')
    num_notes= session.get('num_notes')
    num_steps = session.get('num_steps')
    incluir_pausas = session.get('incluir_pausas')
    tonalidad = session.get('tonalidad')
    escala = session.get('escala')
    tonica = session.get('tonica')
    prob_mutacion = session.get('prob_mutacion')
    num_mutaciones = session.get('num_mutaciones')
    bpm= 128
    folder = os.path.join("static/midi_dir", str(int(datetime.now().timestamp())))
    sorted_population_fitness = sorted(population_fitness, key=lambda e: e[1], reverse=True)
    population = [e[0] for e in sorted_population_fitness]
    next_generation = population[0:2]
    for j in range(int(len(population) / 2) - 1):

        def fitness_lookup(genome):
            for e in population_fitness:
                if e[0] == genome:
                    return e[1]
            return 0
        parents = selection_pair(population, fitness_lookup)
        offspring_a, offspring_b = single_point_crossover(parents[0], parents[1])
        offspring_a = mutation(offspring_a, num=num_mutaciones, probability=prob_mutacion)
        offspring_b = mutation(offspring_b, num=num_mutaciones, probability=prob_mutacion)
        next_generation += [offspring_a, offspring_b]
        print(f"Población {population_id} lista")
        print("Guardando la población midi...")
        for i, genome in enumerate(population):
            save_genome_to_midi(f"{folder}/{population_id}/{escala}-{tonalidad}-{i}.mid", genome, num_bars, num_notes, num_steps, incluir_pausas, tonalidad, escala, tonica, bpm)
        print("Listo!")
        population = next_generation
        population_id += 1
        session['population_id']= population_id
        session['poblacion_id']=0
    return redirect(url_for('continuar_proceso'))

@app.route('/pagina4', methods=['POST'])
def pagina4():
    population_fitness = session.get('population_fitness')
    population_id = session.get('population_id')
    num_bars= session.get('num_bars')
    num_notes= session.get('num_notes')
    num_steps = session.get('num_steps')
    incluir_pausas = session.get('incluir_pausas')
    tonalidad = session.get('tonalidad')
    escala = session.get('escala')
    tonica = session.get('tonica')
    prob_mutacion = session.get('prob_mutacion')
    num_mutaciones = session.get('num_mutaciones')
    bpm= 128
    folder_img  = os.path.join("static/imgs", "imgs_midi")
    folder1  = os.path.join("static/midi_dir", "favoritas")
    folder2  = os.path.join("static/midi_dir", str(int(datetime.now().timestamp())))
    sorted_population_fitness = sorted(population_fitness, key=lambda e: e[1], reverse=True)
    population = [e[0] for e in sorted_population_fitness]
    next_generation = population[0:2]
    for j in range(int(len(population) / 2) - 1):
        def fitness_lookup(genome):
            for e in population_fitness:
                if e[0] == genome:
                    return e[1]
            return 0
        parents = selection_pair(population, fitness_lookup)
        offspring_a, offspring_b = single_point_crossover(parents[0], parents[1])
        offspring_a = mutation(offspring_a, num=num_mutaciones, probability=prob_mutacion)
        offspring_b = mutation(offspring_b, num=num_mutaciones, probability=prob_mutacion)
        next_generation += [offspring_a, offspring_b]
        print(f"Población {population_id} lista")
        print("Guardando la población midi...")
        for i, genome in enumerate(population):
            if i < 2:
                save_genome_to_midi(os.path.join(folder1, f"{i+1}.mid"), genome, num_bars, num_notes, num_steps, incluir_pausas, tonalidad, escala, tonica, bpm)
                midi_file_path = os.path.join(app.root_path, f'static/midi_dir/favoritas/{i+1}.mid')
                pitches, durations, start_times, parts = extract_arrays_from_midi_file(midi_file_path)
                img = create_piano_roll_image(pitches, durations, start_times, parts, midi_file_path)
                save_path = os.path.join(folder_img,f'{i+1}.png')
                img.save(save_path)


            # Save the rest of the MIDI files in the timestamped directory
            save_genome_to_midi(f"{folder2}/{population_id}/{escala}-{tonalidad}-{i}.mid", genome, num_bars, num_notes, num_steps, incluir_pausas, tonalidad, escala, tonica, bpm)

        print("Listo!")
        population = next_generation
        population_id += 1
        session['population_id']= population_id
    return render_template('pagina4.html')


@app.route('/pista_1', methods=['POST'])
def pista_1():
    num_bars= session.get('num_bars')
    pygame.mixer.init()
    pygame.init()
    dir  = os.path.join("static/midi_dir/favoritas", "1.mid")
    # Carga el archivo MIDI
    pygame.mixer.music.load(dir)

    # Reproduce el archivo MIDI
    pygame.mixer.music.play()

    # Espera a que termine la reproducción del archivo MIDI
    while pygame.mixer.music.get_busy():
        time.sleep(2*num_bars)

    return render_template('pagina4.html')

    
@app.route('/pista_2', methods=['POST'])
def pista_2():
    num_bars= session.get('num_bars')
    pygame.mixer.init()
    pygame.init()
    dir  = os.path.join("static/midi_dir/favoritas", "2.mid")
    # Carga el archivo MIDI
    pygame.mixer.music.load(dir)

    # Reproduce el archivo MIDI
    pygame.mixer.music.play()

    # Espera a que termine la reproducción del archivo MIDI
    while pygame.mixer.music.get_busy():
        time.sleep(2*num_bars)

    return render_template('pagina4.html')

@app.route('/generar_musica', methods=['POST'])
def generar_musica():
    session["cantidad"] = request.form.get('cantidad', type=int)
    session["num_pista"] = request.form.get('num_pista')
    return redirect(url_for('generar_musica_magenta'))

@app.route('/generar_musica_magenta')
def generar_musica_magenta():
    cantidad = session.get('cantidad')  # Asume un valor predeterminado si no se encuentra
    pista = session.get('num_pista')
    dir  = os.path.join("static/midi_dir/favoritas", f"{pista}.mid")
    output_dir = os.path.join("static", 'magenta')

    # Asegura que el directorio de salida exista
    os.makedirs(output_dir, exist_ok=True)

    comando = [
        "improv_rnn_generate",
        "--config=chord_pitches_improv",
        f"--bundle_file={bundle_file}",  # Asegúrate de definir `bundle_file` correctamente
        f"--output_dir={output_dir}",
        f"--num_outputs={cantidad}",  # Genera un archivo por ejecución
        "--num_steps=250",
        f"--primer_midi={dir}",
        "--backing_chords=C G Am F C G Am F",
        "--render_chords"
    ]

    try:
        subprocess.run(comando, check=True)
        print(f"Generación de melodía completada exitosamente para {output_dir}.")
    except subprocess.CalledProcessError as e:
        print(f"Error al generar melodía: {e}")

    
    return render_template('pagina5.html')

@app.route('/mis_canciones', methods=['POST'])
def mis_canciones():
    folder1  = r'C:\Users\Migi\PreTaws\proyectoPreTaws\static\magenta'
    try:
        subprocess.run(['explorer', folder1], check=True)
            
    except subprocess.CalledProcessError as e:
        print(f"Error al abrir la carpeta: {e}") 
    print("Carpeta abierta con éxito.") 
    return render_template('pagina5.html')

@app.route('/generate_lyrics_route', methods=['POST'])
def generate_lyrics_route():
    mood = request.form.get('mood')
    prompt = request.form.get('prompt')

    if mood and prompt:  # Asegura que mood y prompt no sean None ni cadenas vacías
        generated_lyrics = generate_lyrics(mood, prompt)
    else:
        generated_lyrics = ""  # O simplemente no definas esta variable si mood o prompt son inválidos
    session['texto_lyrics'] = generated_lyrics

    return render_template('paginaLyrics.html', generated_lyrics=generated_lyrics)

@app.route('/mis_canciones2', methods=['POST'])
def mis_canciones2():
    folder1  = r'C:\Users\Migi\PreTaws\proyectoPreTaws\static\magenta'
    texto_lyrics = session.get('texto_lyrics')
    try:
        subprocess.run(['explorer', folder1], check=True)
            
    except subprocess.CalledProcessError as e:
        print(f"Error al abrir la carpeta: {e}") 
    print("Carpeta abierta con éxito.") 
    return render_template('paginaLyrics.html', generated_lyrics = texto_lyrics)

if __name__ == '__main__':
    app.run(debug=True)

