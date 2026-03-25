import sqlite3
from datetime import datetime
from datetime import datetime, timedelta

# ==========================================
# CONEXIÓN Y CONFIGURACIÓN ESTRICTA
# ==========================================
def conectar():
    conexion = sqlite3.connect("wms_operacion.db")
    # Obliga a SQLite a respetar las relaciones entre tablas (Llaves Foráneas)
    conexion.execute("PRAGMA foreign_keys = ON;") 
    return conexion

def inicializar_db():
    conexion = conectar()
    cursor = conexion.cursor()
    # (Tus tablas existentes se mantienen igual)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS conductores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            vehiculo TEXT NOT NULL
        )
    ''')
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS paquetes (
            codigo_barras TEXT PRIMARY KEY,
            comuna TEXT NOT NULL,
            estado TEXT NOT NULL DEFAULT 'PREVIO',
            fecha_ingreso DATE DEFAULT CURRENT_DATE,
            conductor_id INTEGER,
            FOREIGN KEY (conductor_id) REFERENCES conductores(id)
        )
    ''')
    
    # ACTUALIZACIÓN: Agregamos las nuevas columnas sin romper la tabla
    try: cursor.execute("ALTER TABLE paquetes ADD COLUMN proveedor TEXT DEFAULT 'NO REGISTRA'")
    except sqlite3.OperationalError: pass
    
    try: cursor.execute("ALTER TABLE paquetes ADD COLUMN tanda TEXT DEFAULT 'PM'")
    except sqlite3.OperationalError: pass
    
    try: cursor.execute("ALTER TABLE paquetes ADD COLUMN fecha_hora DATETIME")
    except sqlite3.OperationalError: pass
        
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS canasto_rutas (
            codigo_barras TEXT PRIMARY KEY,
            comuna TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

    cursor.execute("DELETE FROM canasto_rutas WHERE timestamp <= datetime('now', '-72 hours')")

    conexion.commit()
    conexion.close()
    ejecutar_purga_28_dias()

# ==========================================
# REGLA INQUEBRANTABLE: PURGA AUTOMÁTICA
# ==========================================
def ejecutar_purga_28_dias():
    conexion = conectar()
    cursor = conexion.cursor()
    # Elimina cualquier registro que tenga más de 28 días desde su ingreso
    cursor.execute("DELETE FROM paquetes WHERE fecha_ingreso <= date('now', '-28 days')")
    conexion.commit()
    conexion.close()

# ==========================================
# MÓDULO: CONDUCTORES (CRUD)
# ==========================================
def obtener_conductores():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT id, nombre, vehiculo FROM conductores ORDER BY nombre")
    filas = cursor.fetchall()
    conexion.close()
    return filas

def insertar_conductor(nombre, vehiculo):
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("INSERT INTO conductores (nombre, vehiculo) VALUES (?, ?)", (nombre, vehiculo))
    conexion.commit()
    conexion.close()

# ==========================================
# MÓDULO: PAQUETERÍA Y RUTAS
# ==========================================
def procesar_excel_masivo(lista_paquetes, tanda_seleccionada):
    """
    Recibe: (codigo, comuna, proveedor) y le inyecta la tanda y la hora exacta.
    """
    conexion = conectar()
    cursor = conexion.cursor()
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Preparamos la lista inyectando los datos faltantes
    datos_finales = [(p[0], p[1], p[2], tanda_seleccionada, ahora) for p in lista_paquetes]
    
    cursor.executemany('''
        INSERT OR IGNORE INTO paquetes (codigo_barras, comuna, proveedor, estado, tanda, fecha_hora) 
        VALUES (?, ?, ?, 'PREVIO', ?, ?)
    ''', datos_finales)
    conexion.commit()
    conexion.close()

def pistolear_paquete(codigo_escaneado, comuna_nueva, tanda_seleccionada="PM"):
    conexion = conectar()
    cursor = conexion.cursor()
    ahora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    cursor.execute("SELECT comuna FROM paquetes WHERE codigo_barras = ?", (codigo_escaneado,))
    resultado = cursor.fetchone()

    if resultado:
        if comuna_nueva and comuna_nueva != resultado[0]:
            comuna_final = comuna_nueva
            estado_texto = "REASIGNADO"
        else:
            comuna_final = resultado[0]
            estado_texto = "ACTUALIZADO"

        cursor.execute("UPDATE paquetes SET estado = 'CONFIRMADO', comuna = ?, tanda = ?, fecha_hora = ? WHERE codigo_barras = ?", 
                       (comuna_final, tanda_seleccionada, ahora, codigo_escaneado))
        conexion.commit()
        conexion.close()
        return comuna_final, estado_texto
        
    elif comuna_nueva:
        cursor.execute("INSERT INTO paquetes (codigo_barras, comuna, estado, tanda, fecha_hora) VALUES (?, ?, 'NUEVO', ?, ?)", 
                       (codigo_escaneado, comuna_nueva, tanda_seleccionada, ahora))
        conexion.commit()
        conexion.close()
        return comuna_nueva, "NUEVO"
    
    conexion.close()
    return None, "ERROR"

def consultar_estado_paquete(codigo_escaneado):
    """
    Retorna un diccionario con la comuna y el estado actual del paquete.
    Retorna None si el paquete no existe.
    """
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT comuna, estado FROM paquetes WHERE codigo_barras = ?", (codigo_escaneado,))
    resultado = cursor.fetchone()
    conexion.close()
    
    if resultado:
        return {"comuna": resultado[0], "estado": resultado[1]}
    return None

def agregar_al_canasto_db(codigo, comuna):
    conexion = conectar()
    cursor = conexion.cursor()
    try:
        cursor.execute("INSERT OR REPLACE INTO canasto_rutas (codigo_barras, comuna) VALUES (?, ?)", (codigo, comuna))
        conexion.commit()
    except sqlite3.Error as e:
        print(f"Error al guardar en canasto: {e}")
    finally:
        conexion.close()

def obtener_canasto_db():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("SELECT comuna, codigo_barras FROM canasto_rutas")
    filas = cursor.fetchall()
    conexion.close()
    
    canasto = {}
    for comuna, codigo in filas:
        if comuna not in canasto:
            canasto[comuna] = []
        canasto[comuna].append(codigo)
    return canasto

def vaciar_canasto_db():
    conexion = conectar()
    cursor = conexion.cursor()
    cursor.execute("DELETE FROM canasto_rutas")
    conexion.commit()
    conexion.close()