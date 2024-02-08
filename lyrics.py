import os
import typer
import openai
from dotenv import load_dotenv

load_dotenv()

openai.api_key = os.getenv("OPENAI_KEY")

app = typer.Typer()

@app.command()
def interactive_chat():
    typer.echo("Bienvenido al generador de letras de canciones. Escribe 'exit' para salir.")
    
    # Preguntar al usuario por el ambiente de la canción
    mood = typer.prompt("Describe el ambiente de la canción (alegría, tristeza, amor, enojo, etc.):")
    
    # Inicializar la sesión de chat
    chat_log = []

    while True:
        prompt = typer.prompt("Escribe una frase clave para la letra (o escribe 'exit' para finalizar):")
        
        if prompt.lower() == "exit":
            typer.echo("Generación de letras finalizada. ¡Espero que te guste!")
            break

        # Agregar el prompt del usuario al chat log
        chat_log.append({"role": "user", "content": prompt})

        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "Estás generando letras de canciones basadas en frases clave y emociones dadas."},
                {"role": "user", "content": f"Genera una letra de canción sobre el tema de {mood} utilizando la frase clave '{prompt}'. La canción debe expresar {mood}."},
            ]
        )
        # Extraer y mostrar la respuesta generada
        generated_lyrics = response["choices"][0]["message"]["content"]
        typer.echo(f'Letra Generada:\n{generated_lyrics}')
        
        # Agregar la respuesta generada al chat log
        chat_log.append({"role": "assistant", "content": generated_lyrics})


if __name__ == "__main__":
    app()