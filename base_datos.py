import sqlite3
from datetime import datetime, timedelta

DB_NAME = 'historial_bodega.db'

def conectar():
    return sqlite3.connect(DB_NAME)

def inicializar_db():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS paquetes (
            guia_id TEXT PRIMARY KEY, comuna TEXT, proveedor TEXT, 
            estado TEXT, fecha_manifiesto TEXT, fecha_recepcion TEXT
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conductores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            vehiculo TEXT NOT NULL
        )
    ''')
    # Limpieza de 25 días
    fecha_limite = (datetime.now() - timedelta(days=25)).strftime("%Y-%m-%d %H:%M:%S")
    cursor.execute("DELETE FROM paquetes WHERE fecha_manifiesto < ?", (fecha_limite,))
    conexion.commit()
    conexion.close()

def insertar_o_actualizar_paquete(guia_id, comuna, proveedor, estado):
    conexion = conectar()
    cursor = conexion.cursor()
    fecha_hoy = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Verifica si existe
    cursor.execute("SELECT guia_id FROM paquetes WHERE guia_id = ?", (guia_id,))
    existe = cursor.fetchone()
    
    if existe:
        cursor.execute("UPDATE paquetes SET comuna=?, proveedor=?, estado=?, fecha_recepcion=? WHERE guia_id=?", 
                       (comuna, proveedor, estado, fecha_hoy, guia_id))
        resultado = "ACTUALIZADO"
    else:
        cursor.execute("INSERT INTO paquetes VALUES (?, ?, ?, ?, ?, ?)", 
                       (guia_id, comuna, proveedor, estado, fecha_hoy, fecha_hoy))
        resultado = "NUEVO"
        
    conexion.commit()
    conexion.close()
    return resultado

def buscar_paquete(guia_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT * FROM paquetes WHERE guia_id = ?", (guia_id,))
    datos = cursor.fetchone()
    conexion.close()
    return datos

def eliminar_paquete(guia_id):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM paquetes WHERE guia_id = ?", (guia_id,))
    conexion.commit()
    conexion.close()

# Funciones CRUD para Conductores

def insertar_conductor(nombre, vehiculo):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO conductores (nombre, vehiculo) VALUES (?, ?)", (nombre, vehiculo))
    conexion.commit()
    conexion.close()

def obtener_conductores():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre, vehiculo FROM conductores ORDER BY nombre")
    filas = cursor.fetchall()
    conexion.close()
    return filas

def eliminar_conductor(id_conductor):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM conductores WHERE id = ?", (id_conductor,))
    conexion.commit()
    conexion.close()

def actualizar_conductor(id_conductor, nombre, vehiculo):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("UPDATE conductores SET nombre = ?, vehiculo = ? WHERE id = ?", (nombre, vehiculo, id_conductor))
    conexion.commit()
    conexion.close()