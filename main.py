import tkinter as tk
from tkinter import ttk
import base_datos as bd  # <--- ESTA ES LA LÍNEA QUE TE FALTA

# Importación estricta de los módulos visuales
from vistas.recogidas import TabRecogidas
from vistas.registro import TabRegistro
from vistas.rutas import TabRutas
from vistas.conductores import TabConductores
from vistas.auditoria import TabAuditoria

# Importación estricta de los módulos visuales
from vistas.recogidas import TabRecogidas
from vistas.registro import TabRegistro
from vistas.rutas import TabRutas
from vistas.auditoria import TabAuditoria
from vistas.conductores import TabConductores

COMUNAS_OFICIALES = [
    'QUILICURA', 'RENCA', 'CERRO NAVIA', 'INDEPENDENCIA', 'CONCHALI', 
    'HUECHURABA', 'RECOLETA', 'VITACURA', 'LO BARNECHEA', 'PUDAHUEL', 'LO PRADO', 
    'QUINTA NORMAL', 'ESTACION CENTRAL', 'CERRILLOS', 'PAC', 'SAN MIGUEL', 'PROVIDENCIA', 
    'LA REINA', 'PEÑALOLEN', 'MACUL', 'ÑUÑOA', 'LAS CONDES', 'MAIPU', 
    'SAN BERNARDO', 'EL BOSQUE', 'LO ESPEJO', 'LA CISTERNA', 'SAN RAMON', 
    'LA GRANJA', 'SAN JOAQUIN', 'LA FLORIDA', 'COLINA', 'LAMPA', 'PUENTE ALTO', 'SANTIAGO'
]

def configurar_estilos(ventana):
    # Estilo sobrio, claro y legible. Cero distractores visuales.
    ventana.option_add("*Font", ("Arial", 11))
    ventana.configure(bg="#f0f0f0")
    
    estilo = ttk.Style()
    estilo.theme_use('clam')
    estilo.configure(".", background="#f0f0f0", foreground="black", font=("Arial", 11))
    estilo.configure("TNotebook.Tab", padding=[15, 5], font=("Arial", 11, "bold"))
    estilo.map("TNotebook.Tab", background=[("selected", "#e0e0e0")])
    estilo.configure("TCombobox", background="white", fieldbackground="white")

def main():
    # Inicializa el motor, crea tablas si no existen y purga lo viejo automáticamente.
    bd.inicializar_db()

    ventana = tk.Tk()
    ventana.title("WMS Bodega - Centro de Mando V5.0")
    ventana.geometry("1200x800")
    
    configurar_estilos(ventana)

    # ==========================================
    # BARRA DE BÚSQUEDA GLOBAL
    # ==========================================
    frame_busqueda = tk.Frame(ventana, bg="#e0e0e0", pady=10, padx=15, relief=tk.SOLID, bd=1)
    frame_busqueda.pack(fill=tk.X)

    tk.Label(frame_busqueda, text="Consulta Rápida (F3):", bg="#e0e0e0", font=("Arial", 11, "bold")).pack(side=tk.LEFT)
    entry_buscador = ttk.Entry(frame_busqueda, width=30)
    entry_buscador.pack(side=tk.LEFT, padx=10)

    lbl_resultado_busqueda = tk.Label(frame_busqueda, text="", bg="#e0e0e0", font=("Arial", 11, "bold"))
    lbl_resultado_busqueda.pack(side=tk.LEFT, padx=15)

    def buscar_paquete_global(event=None):
        codigo = entry_buscador.get().strip().upper()
        if not codigo: return
        
        info = bd.consultar_estado_paquete(codigo)
        if info:
            texto = f"✅ {codigo} -> Comuna: {info['comuna']} | Estado actual: {info['estado']}"
            lbl_resultado_busqueda.config(text=texto, fg="#27ae60")
        else:
            lbl_resultado_busqueda.config(text=f"❌ {codigo} -> FANTASMA. NO EXISTE EN SISTEMA.", fg="#c0392b")
        
        entry_buscador.delete(0, tk.END)

    entry_buscador.bind("<Return>", buscar_paquete_global)
    
    # Atajo de teclado para ir rápido al buscador desde cualquier lado
    ventana.bind("<F3>", lambda e: entry_buscador.focus())

    # ==========================================
    # SISTEMA MODULAR DE PESTAÑAS
    # ==========================================
    notebook = ttk.Notebook(ventana)
    notebook.pack(expand=True, fill=tk.BOTH, padx=10, pady=10)

    # Instanciamos los 4 módulos operativos
    tab_recogidas = TabRecogidas(notebook) 
    tab_registro = TabRegistro(notebook, COMUNAS_OFICIALES)
    tab_rutas = TabRutas(notebook)
    tab_auditoria = TabAuditoria(notebook)
    tab_conductores = TabConductores(notebook)

    # ==========================================
    # CONTROL DE ENFOQUE Y VISIBILIDAD
    # ==========================================
    def al_cambiar_pestana(event):
        pestaña_actual = notebook.index(notebook.select())
        
        # Ocultar el buscador global si estamos en la pestaña de Conductores (índice 3)
        if pestaña_actual == 3:
            frame_busqueda.pack_forget()
        else:
            # Volver a anclarlo arriba si salimos de Conductores
            frame_busqueda.pack(fill=tk.X, before=notebook) 

        # Redirigir el foco de la pistola al módulo correspondiente
        try:
            if pestaña_actual == 0:
                tab_recogidas.enfocar_pistola()
            elif pestaña_actual == 1:
                tab_registro.enfocar_pistola()
            elif pestaña_actual == 2:
                tab_rutas.enfocar_pistola()
        except AttributeError:
            pass
            
    notebook.bind("<<NotebookTabChanged>>", al_cambiar_pestana)

    ventana.mainloop()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n[!] Cierre forzado. Apagando el Centro de Mando WMS de forma segura...")