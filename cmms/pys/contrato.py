#!/usr/bin/env python3
import os
import glob
import requests
import json
import PyPDF2

import os
print("Directorio de trabajo:", os.getcwd())


def cargar_conocimientos():
    """
    Carga el contenido de todos los archivos en la carpeta 'conocimientos'
    que tengan extensión .txt, .md y .pdf, y los concatena en un único string.
    """
    # Especifica la ruta absoluta de la carpeta de conocimientos
    carpeta = r"c:\Django\SoftCoMJuda\Softcom\cmms\conocimientos"
    conocimiento_total = ""

    # Procesar archivos de texto (.txt y .md)
    for extension in ['*.txt', '*.md']:
        for ruta_archivo in glob.glob(os.path.join(carpeta, extension)):
            try:
                with open(ruta_archivo, 'r', encoding='utf-8') as f:
                    contenido = f.read()
                    conocimiento_total += f"\n--- Contenido de {ruta_archivo} ---\n{contenido}\n"
            except Exception as e:
                print(f"Error al leer {ruta_archivo}: {e}")

    # Procesar archivos PDF
    for ruta_archivo in glob.glob(os.path.join(carpeta, '*.pdf')):
        try:
            with open(ruta_archivo, 'rb') as f:
                lector_pdf = PyPDF2.PdfReader(f)
                contenido_pdf = ""
                for pagina in lector_pdf.pages:
                    texto_pagina = pagina.extract_text()
                    if texto_pagina:
                        contenido_pdf += texto_pagina + "\n"
                conocimiento_total += f"\n--- Contenido de {ruta_archivo} ---\n{contenido_pdf}\n"
        except Exception as e:
            print(f"Error al leer {ruta_archivo}: {e}")

    return conocimiento_total

def generate_content(prompt_text):
    """
    Envía una solicitud POST a la API de Gemini para generar contenido
    basado en el prompt_text (que incluye conocimientos y la pregunta).
    """
    # Recuperar la API key desde la variable de entorno
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("No se encontró la variable de entorno GEMINI_API_KEY")

    # Construir la URL del endpoint (la API key se envía como parámetro)
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
    
    # Encabezados de la solicitud
    headers = {
        "Content-Type": "application/json"
    }
    
    # Definir el cuerpo de la solicitud en formato JSON
    data = {
        "contents": [
            {
                "parts": [
                    {"text": prompt_text}
                ]
            }
        ]
    }
    
    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            return response.json()
        else:
            print("Error en la consulta a la API de Gemini:", response.status_code, response.text)
            return None
    except Exception as e:
        print("Excepción al consultar la API de Gemini:", e)
        return None

def main():
    print("Cargando conocimientos desde la carpeta 'conocimientos'...")
    conocimientos = cargar_conocimientos()
    if not conocimientos.strip():
        print("No se pudo cargar ningún conocimiento. Verifica que existan archivos en la carpeta 'conocimientos'.")
        return
    print("Conocimientos cargados correctamente.\n")
    
    print("Bot listo. Escribe 'salir' para terminar.\n")
    while True:
        pregunta = input("Usuario: ")
        if pregunta.lower().strip() == "salir":
            break

        # Combinar los conocimientos cargados con la pregunta del usuario
        prompt = (
            "Utiliza la siguiente información de base de conocimientos para responder la pregunta de forma clara y precisa:\n\n"
            f"{conocimientos}\n"
            "Pregunta: " + pregunta
        )

        resultado = generate_content(prompt)
        if resultado:
            # Se asume que la respuesta contiene una lista en 'choices'
            if "choices" in resultado and len(resultado["choices"]) > 0:
                respuesta = resultado["choices"][0].get("text", "")
                print("Bot:", respuesta.strip())
            else:
                print("Bot: La respuesta no tiene el formato esperado.")
        else:
            print("Bot: No pude obtener una respuesta.")

if __name__ == "__main__":
    main()
