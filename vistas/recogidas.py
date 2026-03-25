import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
import base_datos as bd

class TabRecogidas:
    def __init__(self, notebook):
        self.frame_principal = tk.Frame(notebook)
        notebook.add(self.frame_principal, text="1. Recogidas (Excel)")
        self.df_actual = pd.DataFrame()
        self.modo_vista = tk.StringVar(value="Comuna") 
        self.var_tanda = tk.StringVar(value="PM") # NUEVO: Selector por defecto
        self.construir_interfaz()

    def construir_interfaz(self):
        # --- NUEVO: SELECTOR DE TANDA ---
        frame_triage = tk.LabelFrame(self.frame_principal, text="1. Etiqueta de Triage (Obligatorio)", padx=10, pady=5)
        frame_triage.pack(fill=tk.X, padx=15, pady=5)
        
        tk.Radiobutton(frame_triage, text="Tanda AM (Mañana)", variable=self.var_tanda, value="AM").pack(side=tk.LEFT, padx=15)
        tk.Radiobutton(frame_triage, text="Tanda PM (Tarde)", variable=self.var_tanda, value="PM").pack(side=tk.LEFT, padx=15)
        tk.Radiobutton(frame_triage, text="Histórico (Semana Entera)", variable=self.var_tanda, value="HISTORICO").pack(side=tk.LEFT, padx=15)

        # Zona de carga
        frame_carga = tk.Frame(self.frame_principal, pady=10, padx=15)
        frame_carga.pack(fill=tk.X)
        tk.Button(frame_carga, text="📂 Seleccionar Excel", bg="#27ae60", fg="white", font=("Arial", 11, "bold"), command=self.cargar_excel).pack(side=tk.LEFT)
        self.lbl_estado = tk.Label(frame_carga, text="Esperando archivo...", font=("Arial", 11, "italic"), fg="gray")
        self.lbl_estado.pack(side=tk.LEFT, padx=15)
        self.lbl_total = tk.Label(frame_carga, text="Total: 0 paquetes", font=("Arial", 12, "bold"))
        self.lbl_total.pack(side=tk.RIGHT, padx=15)

        # Filtros y Tabla
        frame_filtros = tk.Frame(self.frame_principal, padx=15)
        frame_filtros.pack(fill=tk.X, pady=5)
        tk.Label(frame_filtros, text="Agrupar por:", font=("Arial", 10)).pack(side=tk.LEFT)
        tk.Radiobutton(frame_filtros, text="Ciudad", variable=self.modo_vista, value="Comuna", command=self.actualizar_tabla).pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(frame_filtros, text="Negocio", variable=self.modo_vista, value="Proveedor", command=self.actualizar_tabla).pack(side=tk.LEFT, padx=5)
        tk.Button(frame_filtros, text="💾 Subir a Base de Datos", bg="#2980b9", fg="white", font=("Arial", 10, "bold"), command=self.guardar_en_bd).pack(side=tk.RIGHT)

        self.tree = ttk.Treeview(self.frame_principal, columns=("Agrupacion", "Cantidad"), show="headings", height=15)
        self.tree.heading("Agrupacion", text="Grupo")
        self.tree.heading("Cantidad", text="Cantidad de Paquetes")
        self.tree.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

    def cargar_excel(self):
        ruta_archivo = filedialog.askopenfilename(filetypes=[("Archivos Excel", "*.xlsx *.xls")])
        if not ruta_archivo: return
        try:
            df = pd.read_excel(ruta_archivo)
            df.columns = df.columns.str.strip() 
            columnas_requeridas = ["Número de guía", "Ciudad", "Negocio"]
            faltantes = [col for col in columnas_requeridas if col not in df.columns]
            if faltantes: return messagebox.showerror("Error", f"Faltan columnas:\n{', '.join(faltantes)}")
            
            self.df_actual = df[columnas_requeridas].dropna(subset=["Número de guía"])
            self.df_actual["Número de guía"] = self.df_actual["Número de guía"].astype(str).str.strip().str.upper()
            self.df_actual["Ciudad"] = self.df_actual["Ciudad"].astype(str).str.strip().str.upper()
            self.df_actual["Negocio"] = self.df_actual["Negocio"].astype(str).str.strip().str.upper()

            self.lbl_estado.config(text=f"Archivo cargado: {ruta_archivo.split('/')[-1]}", fg="black")
            self.lbl_total.config(text=f"Total: {len(self.df_actual)} paquetes")
            self.actualizar_tabla()
        except Exception as e:
            messagebox.showerror("Error", f"Error procesando:\n{str(e)}")

    def actualizar_tabla(self):
        for item in self.tree.get_children(): self.tree.delete(item)
        if self.df_actual.empty: return
        columna = "Ciudad" if self.modo_vista.get() == "Comuna" else "Negocio"
        resumen = self.df_actual.groupby(columna).size().reset_index(name='Cantidad').sort_values('Cantidad', ascending=False)
        for _, row in resumen.iterrows(): self.tree.insert("", tk.END, values=(row[columna], row['Cantidad']))

    def guardar_en_bd(self):
        if self.df_actual.empty: return messagebox.showwarning("Atención", "No hay datos.")
        lista_datos = list(self.df_actual.itertuples(index=False, name=None))
        tanda_seleccionada = self.var_tanda.get() # Capturamos la tanda
        
        try:
            bd.procesar_excel_masivo(lista_datos, tanda_seleccionada)
            messagebox.showinfo("Éxito", f"Datos subidos con etiqueta: {tanda_seleccionada}")
            self.df_actual = pd.DataFrame()
            self.actualizar_tabla()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def enfocar_pistola(self): pass