import sqlite3
import pandas as pd

# Nombre de tu base de datos
db_name = 'db.sqlite3'

# Conexión a SQLite
conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# Obtiene todas las tablas
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tablas = cursor.fetchall()

# Exporta cada tabla a un archivo CSV
for tabla in tablas:
    nombre_tabla = tabla[0]
    print(f"Exportando {nombre_tabla}...")
    df = pd.read_sql_query(f"SELECT * FROM {nombre_tabla}", conn)
    df.to_csv(f"{nombre_tabla}.csv", index=False)

# Cierra la conexión
conn.close()

print("Exportación completada.")
