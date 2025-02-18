import requests
import json
import os
from docx import Document
import PyPDF2

# API Key de Gemini - ¡REEMPLAZA CON TU API KEY REAL!
GEMINI_API_KEY = "AIzaSyAV2WWPOOdq2GBEWwteo9TR9lRxRqa2rZ0" # <-- ¡REEMPLAZA CON TU API KEY REAL!


def generate_content(prompt):
    """Genera contenido utilizando el modelo de Gemini."""
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"

    headers = {
        'Content-Type': 'application/json',
    }

    data = {
        "contents": [{
            "parts": [{
                "text": prompt
            }]
        }]
    }

    response = requests.post(url, headers=headers, data=json.dumps(data))

    if response.status_code == 200:
        result = response.json()

        try:
            text = result['candidates'][0]['content']['parts'][0]['text']
            return text
        except KeyError:
            return 'No content generated'
    else:
        return f"Error: {response.status_code}, {response.text}"

def load_file(file_path):
    """Carga y procesa un archivo, dependiendo de su tipo."""
    file_extension = file_path.split('.')[-1].lower()
    content = ""

    if file_extension == 'txt':
        with open(file_path, 'r', encoding='utf-8') as file: # Especificar encoding UTF-8
            content = file.read()
    elif file_extension == 'docx':
        doc = Document(file_path)
        content = "\n".join([para.text for para in doc.paragraphs])
    elif file_extension == 'pdf':
        try:
            with open(file_path, 'rb') as file:
                reader = PyPDF2.PdfReader(file)
                content = "\n".join([page.extract_text() for page in reader.pages])
        except Exception as e:
            return f"Error al leer PDF: {e}" # Manejo de errores al leer PDF
    else:
        content = "Formato de archivo no soportado."

    return content

def save_to_knowledge_base(content, knowledge_base_file="conocimientos.txt"):
    """Guarda el contenido cargado en un archivo de texto en la raíz del script como base de conocimientos."""
    script_dir = os.path.dirname(os.path.abspath(__file__)) # Obtiene el directorio del script
    knowledge_base_path = os.path.join(script_dir, knowledge_base_file) # Construye la ruta completa

    try:
        with open(knowledge_base_path, 'a', encoding='utf-8') as file: # Especificar encoding UTF-8
            file.write(content + "\n\n")
    except Exception as e:
        print(f"Error al guardar en la base de conocimientos: {e}") # Manejo de errores al guardar

def load_knowledge_base(knowledge_base_file="conocimientos.txt"):
    """Carga todo el contenido de la base de conocimiento desde el archivo en la raíz del script."""
    script_dir = os.path.dirname(os.path.abspath(__file__)) # Obtiene el directorio del script
    knowledge_base_path = os.path.join(script_dir, knowledge_base_file) # Construye la ruta completa

    if os.path.exists(knowledge_base_path):
        try:
            with open(knowledge_base_path, 'r', encoding='utf-8') as file: # Especificar encoding UTF-8
                return file.read()
        except Exception as e:
            print(f"Error al cargar la base de conocimientos: {e}") # Manejo de errores al cargar
            return "Error al cargar la base de conocimientos."
    else:
        return "No hay base de conocimientos cargada."

def summarize_content(content):
    """Genera un resumen del contenido utilizando Gemini."""
    prompt_summarization = f"Por favor, proporciona un resumen conciso del siguiente texto:\n\n{content}\n\nResumen:"
    summary = generate_content(prompt_summarization)
    if "Error" in summary: # Detectar si hubo un error en la generación del resumen
        return "No se pudo generar un resumen debido a un error con la API."
    return summary

def interact():
    """Interacción principal con el bot."""
    print("¡Hola! Soy un bot de preguntas y respuestas. Escribe 'salir' para terminar la conversación.")
    print("Escribe 'cargar archivo' para cargar un archivo a la base de conocimientos.")

    while True:
        question = input("¿Cuál es tu pregunta? ")

        if question.lower() == 'salir':
            print("¡Hasta luego!")
            break

        if question.lower() == 'cargar archivo':
            file_path = input("Por favor, ingresa la ruta del archivo que deseas cargar: ")
            content = load_file(file_path)
            if "Error" in content: # Detectar si load_file devolvió un mensaje de error
                print(content) # Imprimir el mensaje de error de load_file
            else:
                save_to_knowledge_base(content)
                print("¡Archivo cargado exitosamente en la base de conocimientos!")
                # Generar y mostrar el resumen del contenido cargado
                summary = summarize_content(content)
                if "Error" in summary:
                    print(summary) # Imprimir mensaje de error si la summarización falló
                else:
                    print("\nResumen del archivo cargado:")
                    print(summary)

            continue

        # Consultar la base de conocimientos antes de generar una respuesta
        knowledge_base_content = load_knowledge_base()
        if "Error" in knowledge_base_content: # Detectar si load_knowledge_base devolvió un error
            print("Error con la base de conocimientos:", knowledge_base_content) # Imprimir el error de carga
            response = "No puedo acceder a la base de conocimientos en este momento."
        else:
            response = generate_content(f"{question}\n\nConoce lo siguiente:\n{knowledge_base_content}")

        print("Respuesta del bot:", response)

if __name__ == "__main__":
    # Verificar si la API Key ha sido reemplazada
    if GEMINI_API_KEY == "YOUR_API_KEY":
        print("\n\n**¡IMPORTANTE!** Debes reemplazar 'YOUR_API_KEY' con tu API Key real de Gemini para que la conexión funcione.")
        print("Puedes obtener una API Key en: https://makersuite.google.com/app/apikey")
    else:
        interact()