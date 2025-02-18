import os
import pandas as pd
import psycopg2

# Datos de conexión a PostgreSQL
DB_NAME = "softcom"
DB_USER = "postgres"
DB_PASS = "lindaly"
DB_HOST = "localhost"
DB_PORT = "5432"

# Conectar a PostgreSQL
conn = psycopg2.connect(
    dbname=DB_NAME, 
    user=DB_USER, 
    password=DB_PASS, 
    host=DB_HOST, 
    port=DB_PORT
)
cursor = conn.cursor()

# Iterar sobre cada archivo CSV en el directorio actual
for archivo in os.listdir():
    if archivo.endswith('.csv'):
        # Obtener el nombre de la tabla quitando la extensión
        nombre_tabla = archivo[:-4]
        print(f"Importando {archivo} a la tabla {nombre_tabla}...")

        # Leer el archivo CSV con pandas
        df = pd.read_csv(archivo)

        # Convertir el DataFrame a una lista de tuplas para insertar
        registros = df.values.tolist()
        columnas = ','.join(df.columns)

        # Crear consulta SQL para insertar datos
        valores = ','.join(['%s'] * len(df.columns))
        consulta = f"INSERT INTO {nombre_tabla} ({columnas}) VALUES ({valores})"
        
        # Ejecutar la inserción en PostgreSQL
        cursor.executemany(consulta, registros)
        conn.commit()

print("¡Importación completada!")

# Cerrar la conexión
cursor.close()
conn.close()
