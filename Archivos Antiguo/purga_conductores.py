import sqlite3

def purgar_conductores():
    # Conectamos a la base de datos real
    conexion = sqlite3.connect("wms_operacion.db")
    cursor = conexion.cursor()

    try:
        # 1. Rescatar paquetes: Desvincular conductores y devolver paquetes a la bodega
        print("[*] Desvinculando paquetes de los conductores actuales...")
        cursor.execute("UPDATE paquetes SET conductor_id = NULL, estado = 'CONFIRMADO' WHERE conductor_id IS NOT NULL")
        
        # 2. Aniquilar la tabla de conductores
        print("[*] Eliminando todos los registros de conductores...")
        cursor.execute("DELETE FROM conductores")
        
        # 3. Reiniciar el auto-numérico (Para que el ID vuelva a empezar en 1)
        print("[*] Reiniciando el contador de IDs...")
        cursor.execute("DELETE FROM sqlite_sequence WHERE name='conductores'")
        
        conexion.commit()
        print("\n[ÉXITO] Purga completada. La tabla de conductores está vacía y los IDs reiniciados.")
        
    except Exception as e:
        print(f"\n[ERROR] Hubo un problema con la purga: {e}")
        conexion.rollback()
        
    finally:
        conexion.close()

if __name__ == "__main__":
    confirmacion = input("⚠️ ATENCIÓN: Esto borrará TODOS los conductores. ¿Estás seguro? (escribe 'si' para continuar): ")
    if confirmacion.lower() == 'si':
        purgar_conductores()
    else:
        print("Operación cancelada.")