import tkinter as tk
from tkinter import ttk

# Importar Base de Datos
import base_datos as bd

# Importar Vistas
from vistas.recepcion import TabRecepcion
from vistas.enrutamiento import TabEnrutamiento
from vistas.contingencia import TabContingencia
from vistas.conductores import TabConductores

# Lista de Comunas
COMUNAS_OFICIALES = [
    'QUILICURA', 'RENCA', 'CERRO NAVIA', 'INDEPENDENCIA', 'CONCHALI', 
    'HUECHURABA', 'RECOLETA', 'VITACURA', 'LO BARNECHEA', 'PUDAHUEL', 'LO PRADO', 
    'QUINTA NORMAL', 'ESTACION CENTRAL', 'CERRILLOS', 'PAC', 'SAN MIGUEL', 'PROVIDENCIA', 
    'LA REINA', 'PEÑALOLEN', 'MACUL', 'ÑUÑOA', 'LAS CONDES', 'MAIPU', 
    'SAN BERNARDO', 'EL BOSQUE', 'LO ESPEJO', 'LA CISTERNA', 'SAN RAMON', 
    'LA GRANJA', 'SAN JOAQUIN', 'LA FLORIDA', 'COLINA', 'LAMPA', 'PUENTE ALTO', 'SANTIAGO'
]

def main():
    bd.inicializar_db()

    # Configuración de la Ventana Principal
    ventana = tk.Tk()
    ventana.title("WMS Bodega - V5.0 Modular")
    ventana.geometry("1100x750")
    ventana.configure(bg="#f4f6f9")

    # Gestor de Pestañas
    notebook = ttk.Notebook(ventana)
    notebook.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    

    # Inyección de Dependencias
    tab_rec = TabRecepcion(notebook)
    tab_con = TabContingencia(notebook, COMUNAS_OFICIALES)
    tab_rut = TabEnrutamiento(notebook, COMUNAS_OFICIALES)
    tab_con = TabConductores(notebook)

    # Foco Automático
    def al_cambiar_pestana(event):
        pestaña_actual = notebook.index(notebook.select())
        
        try:
            if pestaña_actual == 0:
                tab_rec.enfocar_pistola()
            elif pestaña_actual == 1:
                tab_con.enfocar_pistola()
            elif pestaña_actual == 2:
                tab_rut.enfocar_pistola()
            elif pestaña_actual == 3:
                tab_con.enfocar_pistola()
        except AttributeError:
            pass
    
    notebook.bind("<<NotebookTabChanged>>", al_cambiar_pestana)

    # Bucle Principal
    ventana.mainloop()

if __name__ == "__main__":
    main()