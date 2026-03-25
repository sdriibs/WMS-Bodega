import sqlite3

def unificar_comunas():
    conexion = sqlite3.connect("wms_operacion.db")
    cursor = conexion.cursor()

    try:
        # 1. Cambiamos el nombre en el inventario histórico
        cursor.execute("UPDATE paquetes SET comuna = 'PEDRO AGUIRRE CERDA' WHERE comuna = 'PAC'")
        paquetes_modificados = cursor.rowcount
        
        # 2. Cambiamos el nombre en el canasto de rutas (por si tienes algo ahí ahora mismo)
        cursor.execute("UPDATE canasto_rutas SET comuna = 'PEDRO AGUIRRE CERDA' WHERE comuna = 'PAC'")
        canasto_modificados = cursor.rowcount
        
        conexion.commit()
        print(f"[ÉXITO] Limpieza completada.")
        print(f" -> Se corrigieron {paquetes_modificados} paquetes en la bodega.")
        print(f" -> Se corrigieron {canasto_modificados} paquetes en el canasto de rutas.")
        
    except Exception as e:
        print(f"[ERROR] Hubo un problema: {e}")
        conexion.rollback()
        
    finally:
        conexion.close()

if __name__ == "__main__":
    unificar_comunas()