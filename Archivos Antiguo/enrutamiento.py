import tkinter as tk
from tkinter import ttk, messagebox
import motor_rutas
import base_datos as bd 

class TabEnrutamiento:
    def __init__(self, notebook, comunas_oficiales):
        self.frame_principal = tk.Frame(notebook, bg="#FFFFFF")
        notebook.add(self.frame_principal, text="Barrido y Rutas")
        
        self.comunas_oficiales = comunas_oficiales
        self.rutas_generadas = []
        
        # Control estricto de paquetería
        self.paquetes_escaneados = set() # Evita duplicados (O(1) lookup)
        self.conteo_por_comuna = {}      # Alimenta al motor de rutas
        
        self.construir_interfaz()

    def construir_interfaz(self):
        # --- PANEL IZQUIERDO: FASE 2 (BARRIDO Y CONTROL) ---
        frame_izq = tk.Frame(self.frame_principal, bg="#FFFFFF")
        frame_izq.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        lbl_titulo_izq = tk.Label(frame_izq, text="Fase 2: Barrido Físico", bg="#FFFFFF", fg="#34a853", font=("Google Sans Text", 12, "bold"))
        lbl_titulo_izq.pack(anchor="w", pady=(0, 10))

        frame_escaner = tk.Frame(frame_izq, bg="#202124")
        frame_escaner.pack(fill=tk.X)

        tk.Label(frame_escaner, text="Pistolear Código:", bg="#202124", fg="white").pack(side=tk.LEFT)
        self.entry_escaner = ttk.Entry(frame_escaner, width=25)
        self.entry_escaner.pack(side=tk.LEFT, padx=10)
        self.entry_escaner.bind("<Return>", self.registrar_paquete)

        self.lbl_ultimo = tk.Label(frame_izq, text="Último: Ninguno", bg="#202124", fg="#e8eaed", font=("Google Sans Text", 11))
        self.lbl_ultimo.pack(anchor="w", pady=10)

        # Tabla de confirmados
        columnas_paquetes = ("codigo", "comuna")
        self.tabla_paquetes = ttk.Treeview(frame_izq, columns=columnas_paquetes, show="headings", height=15)
        self.tabla_paquetes.heading("codigo", text="Código Paquete")
        self.tabla_paquetes.heading("comuna", text="Comuna Destino")
        self.tabla_paquetes.column("codigo", width=150)
        self.tabla_paquetes.column("comuna", width=150)
        self.tabla_paquetes.pack(fill=tk.BOTH, expand=True)

        self.lbl_total = tk.Label(frame_izq, text="Total Confirmados: 0", bg="#202124", fg="white", font=("Google Sans Text", 12, "bold"))
        self.lbl_total.pack(anchor="e", pady=5)

        btn_limpiar = tk.Button(frame_izq, text="Limpiar Sesión", bg="#c0392b", fg="white", relief=tk.FLAT, command=self.limpiar_sesion)
        btn_limpiar.pack(anchor="w", pady=5)

        # --- PANEL DERECHO: FASE 3 (RUTAS Y ASIGNACIÓN) ---
        frame_der = tk.Frame(self.frame_principal, bg="#202124")
        frame_der.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        lbl_titulo_der = tk.Label(frame_der, text="Fase 3: Armado y Asignación", bg="#202124", fg="#34a853", font=("Google Sans Text", 12, "bold"))
        lbl_titulo_der.pack(anchor="w", pady=(0, 10))

        frame_controles = tk.Frame(frame_der, bg="#202124")
        frame_controles.pack(fill=tk.X, pady=5)

        tk.Label(frame_controles, text="Dividir en cuántas rutas:", bg="#202124", fg="white").pack(side=tk.LEFT)
        self.combo_rutas = ttk.Combobox(frame_controles, values=["1", "2", "3", "4", "5", "6", "7"], width=5, state="readonly")
        self.combo_rutas.set("5")
        self.combo_rutas.pack(side=tk.LEFT, padx=10)

        btn_calcular = tk.Button(frame_controles, text="Calcular Rutas", bg="#27ae60", fg="white", relief=tk.FLAT, command=self.procesar_rutas)
        btn_calcular.pack(side=tk.LEFT, padx=10)

        self.frame_resultados = tk.Frame(frame_der, bg="#292a2d", bd=1, relief=tk.SOLID)
        self.frame_resultados.pack(fill=tk.BOTH, expand=True, pady=10)

    def enfocar_pistola(self):
        self.entry_escaner.focus()

    def obtener_comuna_bd(self, codigo):
        if "X" in codigo.upper():
            return None # Simula paquete no encontrado en BD
        return "SANTIAGO" if len(codigo) % 2 == 0 else "PAC"

    def registrar_paquete(self, event=None):
        codigo = self.entry_escaner.get().strip().upper()
        if not codigo:
            return

        if codigo in self.paquetes_escaneados:
            messagebox.showwarning("Duplicado", f"El paquete {codigo} ya fue escaneado en esta sesión.")
            self.entry_escaner.delete(0, tk.END)
            return

        comuna = self.obtener_comuna_bd(codigo)

        if comuna:
            self.paquetes_escaneados.add(codigo)
            self.conteo_por_comuna[comuna] = self.conteo_por_comuna.get(comuna, 0) + 1
            
            self.tabla_paquetes.insert("", 0, values=(codigo, comuna))
            self.lbl_ultimo.config(text=f"Último: {codigo} -> {comuna}", fg="#34a853")
            self.lbl_total.config(text=f"Total Confirmados: {len(self.paquetes_escaneados)}")
        else:
            self.lbl_ultimo.config(text=f"Error: {codigo} no existe en inventario.", fg="#c0392b")
            messagebox.showerror("Error de Inventario", f"El paquete {codigo} no tiene registro en la base de datos (Fase 1).")

        self.entry_escaner.delete(0, tk.END)
        self.entry_escaner.focus()

    def limpiar_sesion(self):
        if messagebox.askyesno("Confirmar", "¿Borrar sesión de barrido y empezar de cero?"):
            self.paquetes_escaneados.clear()
            self.conteo_por_comuna.clear()
            for item in self.tabla_paquetes.get_children():
                self.tabla_paquetes.delete(item)
            self.lbl_total.config(text="Total Confirmados: 0")
            self.lbl_ultimo.config(text="Último: Ninguno", fg="#e8eaed")
            for widget in self.frame_resultados.winfo_children():
                widget.destroy()
            self.entry_escaner.focus()

    def procesar_rutas(self):
        if not self.conteo_por_comuna:
            messagebox.showwarning("Sin Datos", "Debes pistolear la carga física antes de calcular rutas.")
            return

        cantidad_rutas = int(self.combo_rutas.get())
        self.rutas_generadas = motor_rutas.calcular_rutas(self.conteo_por_comuna, cantidad_rutas)
        self.actualizar_pantalla_rutas()

    def actualizar_pantalla_rutas(self):
        for widget in self.frame_resultados.winfo_children():
            widget.destroy()

        # Extraer lista de conductores del CRUD para la asignación
        try:
            conductores_db = bd.obtener_conductores()
            lista_asignacion = [f"{c[1]} - {c[2]}" for c in conductores_db]
        except Exception:
            lista_asignacion = ["Sin conductores registrados"]

        for ruta in self.rutas_generadas:
            fila = tk.Frame(self.frame_resultados, bg="#292a2d", pady=8, padx=10)
            fila.pack(fill=tk.X, pady=2)

            # Datos duros de la ruta
            texto_info = f"Ruta {ruta['id']} | {ruta['total']} Pkts | {', '.join(ruta['comunas'])}"
            tk.Label(fila, text=texto_info, bg="#292a2d", fg="white", font=("Google Sans Text", 10)).pack(side=tk.TOP, anchor="w")

            # Controles de asignación por ruta
            frame_controles_ruta = tk.Frame(fila, bg="#292a2d")
            frame_controles_ruta.pack(side=tk.TOP, fill=tk.X, pady=(5,0))

            tk.Label(frame_controles_ruta, text="Asignar a:", bg="#292a2d", fg="#7f8c8d").pack(side=tk.LEFT)
            
            combo_chofer = ttk.Combobox(frame_controles_ruta, values=lista_asignacion, state="readonly", width=30)
            combo_chofer.pack(side=tk.LEFT, padx=10)
            
            btn_copiar = tk.Button(frame_controles_ruta, text="Copiar Resumen", bg="#4d4d4d", fg="white", relief=tk.FLAT, 
                                   command=lambda t=texto_info, c=combo_chofer: self.copiar_ruta(t, c.get()))
            btn_copiar.pack(side=tk.RIGHT)
            
            tk.Frame(self.frame_resultados, height=1, bg="#4d4d4d").pack(fill=tk.X)

    def copiar_ruta(self, info_ruta, chofer):
        if not chofer:
            chofer = "Sin conductor asignado"
        texto_final = f"{chofer} | {info_ruta}"
        self.frame_principal.clipboard_clear()
        self.frame_principal.clipboard_append(texto_final)
        messagebox.showinfo("Copiado", "Ruta y conductor copiados al portapapeles.")