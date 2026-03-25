import tkinter as tk
from tkinter import ttk, messagebox
import base_datos as bd

class TabRegistro:
    def __init__(self, notebook, comunas_oficiales):
        self.frame_principal = tk.Frame(notebook)
        notebook.add(self.frame_principal, text="2. Registro Paquetería")
        self.comunas_oficiales = comunas_oficiales
        self.conteo_comunas = {}
        self.total_escaneados = 0 
        self.var_tanda = tk.StringVar(value="PM") # NUEVO
        self.construir_interfaz()

    def construir_interfaz(self):
        # --- NUEVO: SELECTOR DE TANDA ---
        frame_triage = tk.Frame(self.frame_principal, pady=5, padx=15)
        frame_triage.pack(fill=tk.X)
        tk.Label(frame_triage, text="Triage:", font=("Arial", 11, "bold")).pack(side=tk.LEFT)
        tk.Radiobutton(frame_triage, text="AM", variable=self.var_tanda, value="AM").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(frame_triage, text="PM", variable=self.var_tanda, value="PM").pack(side=tk.LEFT, padx=5)
        tk.Radiobutton(frame_triage, text="Histórico", variable=self.var_tanda, value="HISTORICO").pack(side=tk.LEFT, padx=5)

        # Controles
        frame_controles = tk.Frame(self.frame_principal, pady=10, padx=15)
        frame_controles.pack(fill=tk.X)
        self.lbl_total_escaneados = tk.Label(frame_controles, text="TOTAL SESIÓN: 0", font=("Arial", 15, "bold"), fg="#27ae60")
        self.lbl_total_escaneados.pack(side=tk.RIGHT, padx=15)

        tk.Label(frame_controles, text="Buscar:", font=("Arial", 11, "bold")).pack(side=tk.LEFT)
        self.var_busqueda = tk.StringVar()
        self.entry_buscador = ttk.Entry(frame_controles, textvariable=self.var_busqueda, width=12, font=("Arial", 11))
        self.entry_buscador.pack(side=tk.LEFT, padx=(5, 10))
        self.entry_buscador.bind("<KeyRelease>", self.filtrar_comunas)

        tk.Label(frame_controles, text="Comuna:", font=("Arial", 11)).pack(side=tk.LEFT)
        self.combo_comuna = ttk.Combobox(frame_controles, values=self.comunas_oficiales, state="readonly", width=18)
        self.combo_comuna.pack(side=tk.LEFT, padx=5)

        tk.Label(frame_controles, text="Código:", font=("Arial", 11)).pack(side=tk.LEFT, padx=(20, 0))
        self.entry_codigo = ttk.Entry(frame_controles, width=30, font=("Arial", 11))
        self.entry_codigo.pack(side=tk.LEFT, padx=10)
        self.entry_codigo.bind("<Return>", self.procesar_escaneo)

        # Tablas y resumen
        frame_registro = tk.LabelFrame(self.frame_principal, text="Registro", padx=10, pady=5)
        frame_registro.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        self.tabla_registro = ttk.Treeview(frame_registro, columns=("codigo", "estado", "comuna"), show="headings", height=10)
        for col, text in zip(("codigo", "estado", "comuna"), ("Código", "Estado", "Comuna")): self.tabla_registro.heading(col, text=text)
        self.tabla_registro.pack(fill=tk.BOTH, expand=True)

        frame_resumen = tk.LabelFrame(self.frame_principal, text="Control por Comunas", padx=10, pady=5)
        frame_resumen.pack(fill=tk.X, padx=15, pady=5)
        self.lbl_resumen = tk.Label(frame_resumen, text="Sin paquetes registrados.", font=("Arial", 11, "bold"), justify=tk.LEFT, anchor="w", wraplength=1000)
        self.lbl_resumen.pack(fill=tk.X)

    def filtrar_comunas(self, event):
        busqueda = self.var_busqueda.get().strip().upper()
        if busqueda:
            coincidencias = [c for c in self.comunas_oficiales if busqueda in c]
            self.combo_comuna['values'] = coincidencias
            if coincidencias: self.combo_comuna.set(coincidencias[0])
            else: self.combo_comuna.set('')

    def enfocar_pistola(self): self.entry_codigo.focus()

    def procesar_escaneo(self, event=None):
        codigo = self.entry_codigo.get().strip().upper()
        if not codigo: return

        comuna_seleccionada = self.combo_comuna.get()
        tanda_seleccionada = self.var_tanda.get() # Capturamos la tanda
        
        comuna_final, estado = bd.pistolear_paquete(codigo, comuna_seleccionada, tanda_seleccionada)

        if estado == "ERROR":
            messagebox.showerror("Falta Información", "Usa el buscador para asignarle una comuna.")
            self.entry_codigo.selection_range(0, tk.END)
            return

        self.tabla_registro.insert("", 0, values=(codigo, estado, comuna_final))
        self.conteo_comunas[comuna_final] = self.conteo_comunas.get(comuna_final, 0) + 1
        self.total_escaneados += 1 
        self.actualizar_resumen()
        self.entry_codigo.delete(0, tk.END)
        self.entry_codigo.focus()

    def actualizar_resumen(self):
        self.lbl_resumen.config(text=" | ".join([f"{c}: {k}" for c, k in self.conteo_comunas.items()]))
        self.lbl_total_escaneados.config(text=f"TOTAL SESIÓN: {self.total_escaneados}")