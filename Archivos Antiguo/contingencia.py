import tkinter as tk
from tkinter import ttk, messagebox
import base_datos as bd

class TabContingencia:
    def __init__(self, notebook, lista_comunas):
        self.frame = tk.Frame(notebook)
        notebook.add(self.frame, text="Ingreso de Reintentos")
        self.lista_comunas = lista_comunas
        
        # Escaneo Masivo

        frame_masivo = tk.LabelFrame(self.frame, text="Ingreso Masivo Rápido (Sin Excel)", font=("Arial", 12, "bold"), pady=10, padx=10)
        frame_masivo.pack(fill=tk.X, padx=10, pady=10)
        
        tk.Label(frame_masivo, text="1. Fijar Comuna:").grid(row=0, column=0, padx=5)
        self.combo_comuna = ttk.Combobox(frame_masivo, values=self.lista_comunas, state="readonly", width=20)
        self.combo_comuna.grid(row=0, column=1, padx=5)
        
        tk.Label(frame_masivo, text="2. Pistolear:").grid(row=0, column=2, padx=5)
        self.entrada_masiva = tk.Entry(frame_masivo, font=("Arial", 16), width=20)
        self.entrada_masiva.grid(row=0, column=3, padx=5)
        self.entrada_masiva.bind('<Return>', self.procesar_masivo)
        
        self.lbl_feedback = tk.Label(frame_masivo, text="Esperando...", font=("Arial", 10, "bold"), width=15)
        self.lbl_feedback.grid(row=0, column=4, padx=10)

        # Tabla de sesión actual

        self.tree_sesion = ttk.Treeview(frame_masivo, columns=("Guia", "Comuna", "Accion"), show="headings", height=5)
        self.tree_sesion.heading("Guia", text="N° Guía"); self.tree_sesion.heading("Comuna", text="Comuna"); self.tree_sesion.heading("Accion", text="Estado")
        self.tree_sesion.grid(row=1, column=0, columnspan=5, pady=10, sticky="ew")
        
        tk.Button(frame_masivo, text="Deshacer Seleccionado", bg="#dc3545", fg="white", command=self.deshacer_escaneo).grid(row=2, column=0, columnspan=5, pady=5)

        # Buscador de Paquetes
        frame_buscar = tk.LabelFrame(self.frame, text="Buscador de Paquetes", font=("Arial", 12, "bold"), pady=10, padx=10)
        frame_buscar.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        tk.Label(frame_buscar, text="N° de Guía:").pack(pady=5)
        self.entrada_buscar = tk.Entry(frame_buscar, font=("Arial", 16), justify="center")
        self.entrada_buscar.pack(pady=5)
        self.entrada_buscar.bind('<Return>', self.buscar_codigo)
        
        self.lbl_resultado_busqueda = tk.Label(frame_buscar, text="", font=("Arial", 12), justify="left", bg="#f8f9fa", relief="solid", bd=1, width=50, height=6)
        self.lbl_resultado_busqueda.pack(pady=10)

    def enfocar_pistola(self):
        self.entrada_masiva.focus()
        
    # Lógica de Escaneo Masivo
    def procesar_masivo(self, event):
        codigo = self.entrada_masiva.get().strip().upper()
        comuna = self.combo_comuna.get()
        self.entrada_masiva.delete(0, tk.END)
        
        if not codigo or not comuna:
            self.lbl_feedback.config(text="Falta Comuna/Código", fg="red")
            return
            
        # Inyectar directamente a la base de datos con estado "EMERGENCIA" y ubicación "En Rack"
        estado_bd = bd.insertar_o_actualizar_paquete(codigo, comuna, "EMERGENCIA", "En Rack")
        
        color = "green" if estado_bd == "NUEVO" else "blue"
        self.lbl_feedback.config(text=f"{estado_bd} OK", fg=color)
        
        # Tabla de sesión: mostrar lo que se acaba de ingresar
        self.tree_sesion.insert("", 0, values=(codigo, comuna, estado_bd))

    # Limpiar Scanner
    def deshacer_escaneo(self):
        seleccion = self.tree_sesion.selection()
        if not seleccion: return
        item = self.tree_sesion.item(seleccion[0])
        codigo_a_borrar = item['values'][0]
        
        bd.eliminar_paquete(codigo_a_borrar)
        self.tree_sesion.delete(seleccion[0])
        messagebox.showinfo("Eliminado", f"El paquete {codigo_a_borrar} fue eliminado del sistema.")
        self.entrada_masiva.focus()

    # Lógica del Buscador
    def buscar_codigo(self, event):
        codigo = self.entrada_buscar.get().strip().upper()
        datos = bd.buscar_paquete(codigo) # Consulta limpia a la BD
        
        if datos:
            # datos = (guia_id, comuna, proveedor, estado, fecha_manifiesto, fecha_recepcion)
            texto = f"GUÍA: {datos[0]}\nCOMUNA: {datos[1]}\nPROV: {datos[2]}\nESTADO: {datos[3]}\nREGISTRO: {datos[4]}"
            self.lbl_resultado_busqueda.config(text=texto, bg="#d4edda", fg="#155724")
            self.entrada_buscar.delete(0, tk.END)
            self.entrada_buscar.focus()
        else:
            self.lbl_resultado_busqueda.config(text="PAQUETE NO ENCONTRADO EN LA BASE DE DATOS", bg="#f8d7da", fg="#721c24")
            self.entrada_buscar.selection_range(0, tk.END)
            self.entrada_buscar.focus()