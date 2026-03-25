import tkinter as tk
from tkinter import ttk, messagebox
import base_datos as bd
import motor_rutas
import traceback

class TabRutas:
    def __init__(self, notebook):
        self.frame_principal = tk.Frame(notebook)
        notebook.add(self.frame_principal, text="3. Armado de Rutas")
        
        self.rutas_borrador = []
        self.vars_conductores = {} 
        
        self.construir_interfaz()
        self.actualizar_texto_resumen() 

    def construir_interfaz(self):
        # --- ZONA 1: CANASTO ---
        frame_canasto = tk.LabelFrame(self.frame_principal, text="1. Canasto de Despacho (Persistente)", padx=10, pady=10)
        frame_canasto.pack(fill=tk.X, padx=15, pady=5)

        tk.Label(frame_canasto, text="Escanear Paquete:", font=("Arial", 11)).pack(side=tk.LEFT)
        self.entry_pistola = ttk.Entry(frame_canasto, width=25, font=("Arial", 11))
        self.entry_pistola.pack(side=tk.LEFT, padx=10)
        self.entry_pistola.bind("<Return>", self.escanear_a_canasto)

        btn_vaciar = tk.Button(frame_canasto, text="🗑️ Vaciar Canasto", bg="#c0392b", fg="white", font=("Arial", 10, "bold"), command=self.limpiar_canasto)
        btn_vaciar.pack(side=tk.RIGHT, padx=5)

        self.lbl_total_canasto = tk.Label(frame_canasto, text="Total en Canasto: 0", font=("Arial", 11, "bold"), fg="#d35400")
        self.lbl_total_canasto.pack(side=tk.RIGHT, padx=15)

        self.txt_resumen = tk.Text(self.frame_principal, height=4, bg="#f9f9f9", font=("Arial", 10), state=tk.DISABLED)
        self.txt_resumen.pack(fill=tk.X, padx=15, pady=5)

        # --- ZONA 2: CÁLCULO Y MODO DUAL ---
        frame_calculo = tk.Frame(self.frame_principal, pady=5)
        frame_calculo.pack(fill=tk.X, padx=15)

        tk.Label(frame_calculo, text="Vehículos a usar:", font=("Arial", 10)).pack(side=tk.LEFT)
        self.combo_num_rutas = ttk.Combobox(frame_calculo, values=["1", "2", "3", "4", "5", "6", "7", "8"], width=5, state="readonly")
        self.combo_num_rutas.set("3")
        self.combo_num_rutas.pack(side=tk.LEFT, padx=10)

        btn_sugerir = tk.Button(frame_calculo, text="⚡ Sugerir Rutas", bg="#2980b9", fg="white", font=("Arial", 10, "bold"), command=self.generar_sugerencia)
        btn_sugerir.pack(side=tk.LEFT, padx=5)

        btn_manual = tk.Button(frame_calculo, text="📝 Armado Manual", bg="#e67e22", fg="white", font=("Arial", 10, "bold"), command=self.generar_manual)
        btn_manual.pack(side=tk.LEFT, padx=5)

        btn_borrar_rutas = tk.Button(frame_calculo, text="🧹 Borrar Rutas Visuales", bg="#7f8c8d", fg="white", font=("Arial", 10), command=self.limpiar_solo_rutas)
        btn_borrar_rutas.pack(side=tk.LEFT, padx=15)

        # --- ZONA 3: PIZARRA ---
        self.frame_pizarra = tk.LabelFrame(self.frame_principal, text="2. Pizarra de Asignación", padx=10, pady=10)
        self.frame_pizarra.pack(fill=tk.BOTH, expand=True, padx=15, pady=5)
        
        self.canvas_rutas = tk.Frame(self.frame_pizarra)
        self.canvas_rutas.pack(fill=tk.BOTH, expand=True)

        frame_cirugia = tk.Frame(self.frame_pizarra, pady=10)
        frame_cirugia.pack(fill=tk.X, side=tk.BOTTOM)
        tk.Label(frame_cirugia, text="Mover comuna:").pack(side=tk.LEFT)
        self.combo_mover_comuna = ttk.Combobox(frame_cirugia, state="readonly", width=15)
        self.combo_mover_comuna.pack(side=tk.LEFT, padx=5)
        tk.Label(frame_cirugia, text="Hacia Ruta:").pack(side=tk.LEFT)
        self.combo_mover_destino = ttk.Combobox(frame_cirugia, state="readonly", width=8)
        self.combo_mover_destino.pack(side=tk.LEFT, padx=5)
        tk.Button(frame_cirugia, text="🔄 Aplicar Traspaso", command=self.aplicar_cirugia).pack(side=tk.LEFT, padx=10)

        # --- ZONA 4: CIERRE ---
        btn_confirmar = tk.Button(self.frame_principal, text="💾 CONFIRMAR Y DESPACHAR", bg="#27ae60", fg="white", font=("Arial", 12, "bold"), pady=10, command=self.confirmar_despacho)
        btn_confirmar.pack(fill=tk.X, padx=15, pady=15)

    def limpiar_canasto(self):
        if messagebox.askyesno("Confirmar", "¿Vaciar canasto? Los paquetes no se borrarán de la base de datos general."):
            bd.vaciar_canasto_db() 
            self.actualizar_texto_resumen()
            self.borrado_silencioso_pizarra()
            self.entry_pistola.focus()

    def limpiar_solo_rutas(self):
        self.borrado_silencioso_pizarra()

    def borrado_silencioso_pizarra(self):
        self.rutas_borrador.clear()
        for widget in self.canvas_rutas.winfo_children(): widget.destroy()
        self.vars_conductores.clear()
        self.combo_mover_comuna.set('')
        self.combo_mover_destino.set('')
        self.combo_mover_comuna['values'] = []
        self.combo_mover_destino['values'] = []

    def enfocar_pistola(self):
        self.entry_pistola.focus()
        self.actualizar_texto_resumen() 

    def actualizar_texto_resumen(self):
        canasto_actual = bd.obtener_canasto_db()
        self.txt_resumen.config(state=tk.NORMAL)
        self.txt_resumen.delete(1.0, tk.END)
        
        total_paquetes = 0
        textos = []
        for comuna, codigos in canasto_actual.items():
            cantidad = len(codigos)
            total_paquetes += cantidad
            textos.append(f"{comuna}: {cantidad}")
            
        self.txt_resumen.insert(tk.END, " | ".join(textos) if textos else "Canasto vacío.")
        self.txt_resumen.config(state=tk.DISABLED)
        self.lbl_total_canasto.config(text=f"Total en Canasto: {total_paquetes}")

    def escanear_a_canasto(self, event=None):
        codigo = self.entry_pistola.get().strip().upper()
        if not codigo: return

        canasto_actual = bd.obtener_canasto_db()
        for codigos_en_comuna in canasto_actual.values():
            if codigo in codigos_en_comuna:
                messagebox.showwarning("Duplicado", f"El paquete {codigo} ya está en el canasto.")
                self.entry_pistola.delete(0, tk.END)
                return

        info_paquete = bd.consultar_estado_paquete(codigo)
        estados_validos = ['PREVIO', 'CONFIRMADO', 'REASIGNADO', 'NUEVO']

        if not info_paquete:
            messagebox.showerror("Error", "NO EXISTE EN BODEGA.")
        elif info_paquete['estado'] == 'EN_RUTA':
            messagebox.showerror("Error", "Ya fue despachado.")
        elif info_paquete['estado'] in estados_validos:
            comuna = info_paquete['comuna']
            bd.agregar_al_canasto_db(codigo, comuna) 
            self.actualizar_texto_resumen()

        self.entry_pistola.delete(0, tk.END)
        self.entry_pistola.focus()

    def generar_manual(self):
        canasto_actual = bd.obtener_canasto_db()
        if not canasto_actual:
            return messagebox.showwarning("Aviso", "El canasto está vacío. Pistolea carga primero.")
            
        num_vehiculos = int(self.combo_num_rutas.get())
        self.rutas_borrador = [{'id': i+1, 'comunas': [], 'total': 0} for i in range(num_vehiculos)]
        self.dibujar_pizarra()

    def generar_sugerencia(self):
        try:
            canasto_actual = bd.obtener_canasto_db()
            if not canasto_actual:
                return messagebox.showwarning("Aviso", "El canasto está vacío.")

            conteo_para_motor = {comuna: len(codigos) for comuna, codigos in canasto_actual.items()}
            num_vehiculos = int(self.combo_num_rutas.get())
            
            self.rutas_borrador = motor_rutas.calcular_rutas(conteo_para_motor, num_vehiculos)
            self.dibujar_pizarra()
        except Exception as e:
            messagebox.showerror("Fallo del Sistema", f"Ocurrió un error:\n{str(e)}")

    # --- NUEVA FUNCIÓN: ELIMINAR RUTA INDIVIDUAL ---
    def eliminar_ruta(self, ruta_a_eliminar):
        if messagebox.askyesno("Confirmar", f"¿Eliminar la Ruta #{ruta_a_eliminar['id']}?\n\nLos bultos asignados a esta ruta volverán a estar disponibles en el canasto."):
            self.rutas_borrador.remove(ruta_a_eliminar)
            self.dibujar_pizarra()

    def dibujar_pizarra(self):
        # 1. EL TRUCO DE LA MEMORIA: Rescatamos los conductores antes de borrar la pizarra
        conductores_guardados = {}
        for id_ruta, var_tk in self.vars_conductores.items():
            seleccion = var_tk.get()
            if seleccion and "Seleccione" not in seleccion:
                conductores_guardados[id_ruta] = seleccion

        # Limpieza visual segura
        for widget in self.canvas_rutas.winfo_children():
            widget.destroy()
        self.vars_conductores.clear()
        
        canasto_actual = bd.obtener_canasto_db()

        for ruta in self.rutas_borrador:
            frame_fila = tk.Frame(self.canvas_rutas, pady=10, borderwidth=2, relief=tk.GROOVE, bg="#ffffff")
            frame_fila.pack(fill=tk.X, pady=5, padx=10)

            tk.Label(frame_fila, text=f"Ruta #{ruta['id']}", font=("Arial", 12, "bold"), width=8, bg="#ffffff").pack(side=tk.LEFT)
            
            var_chofer = tk.StringVar()
            
            # Restauramos la memoria del conductor si es que existía
            if ruta['id'] in conductores_guardados:
                var_chofer.set(conductores_guardados[ruta['id']])
            else:
                var_chofer.set("Seleccione Conductor...")

            combo_chofer = ttk.Combobox(frame_fila, textvariable=var_chofer, state="readonly", width=35)
            combo_chofer.config(postcommand=lambda cb=combo_chofer: self.refrescar_lista_combobox(cb))
            combo_chofer.pack(side=tk.LEFT, padx=15)
            self.vars_conductores[ruta['id']] = var_chofer

            lbl_capacidad = tk.Label(frame_fila, text=f"Bultos: {ruta['total']}", font=("Arial", 11, "bold"), bg="#ffffff")
            lbl_capacidad.pack(side=tk.LEFT, padx=(10, 20))
            combo_chofer.bind("<<ComboboxSelected>>", lambda e, lbl=lbl_capacidad, tot=ruta['total'], cb=combo_chofer: self.validar_capacidad(cb, lbl, tot))
            
            # Forzamos la validación visual inmediata si cargó un conductor de la memoria
            if ruta['id'] in conductores_guardados:
                self.validar_capacidad(combo_chofer, lbl_capacidad, ruta['total'])

            # --- NUEVO: BOTÓN ELIMINAR (X ROJA) ---
            # Se empaquetan en orden inverso (RIGHT) para que la X quede al extremo derecho
            btn_eliminar = tk.Button(frame_fila, text="❌", bg="#c0392b", fg="white", font=("Arial", 9, "bold"), command=lambda r=ruta: self.eliminar_ruta(r))
            btn_eliminar.pack(side=tk.RIGHT, padx=(5, 15))

            btn_modal = tk.Button(frame_fila, text="➕ Asignar Comunas", bg="#f1c40f", font=("Arial", 9, "bold"), command=lambda r=ruta: self.abrir_modal_asignacion(r))
            btn_modal.pack(side=tk.RIGHT, padx=5)

            info_comunas = f"Comunas: {', '.join(ruta['comunas'])}"
            tk.Label(frame_fila, text=info_comunas, wraplength=450, justify="left", bg="#ffffff", font=("Arial", 10)).pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)

        self.combo_mover_comuna['values'] = list(canasto_actual.keys())
        self.combo_mover_destino['values'] = [f"Ruta {r['id']}" for r in self.rutas_borrador]
        self.canvas_rutas.update_idletasks()

    def abrir_modal_asignacion(self, ruta_actual):
        canasto_actual = bd.obtener_canasto_db()
        
        comunas_ya_asignadas = set()
        for r in self.rutas_borrador:
            comunas_ya_asignadas.update(r['comunas'])
            
        comunas_disponibles = {comuna: len(codigos) for comuna, codigos in canasto_actual.items() if comuna not in comunas_ya_asignadas}

        modal = tk.Toplevel(self.frame_principal)
        modal.title(f"Asignando carga a Ruta #{ruta_actual['id']}")
        modal.geometry("400x550") 
        modal.grab_set() 
        
        if not comunas_disponibles:
            tk.Label(modal, text="No quedan comunas libres en el canasto.", font=("Arial", 11), pady=30).pack()
            tk.Button(modal, text="Cerrar", command=modal.destroy, font=("Arial", 10)).pack()
            return

        tk.Label(modal, text="Selecciona las comunas para esta ruta:", font=("Arial", 11, "bold")).pack(pady=10)

        frame_botones = tk.Frame(modal, pady=10, bg="#e0e0e0")
        frame_botones.pack(side=tk.BOTTOM, fill=tk.X)

        frame_scroll = tk.Frame(modal)
        frame_scroll.pack(side=tk.TOP, fill=tk.BOTH, expand=True, padx=10, pady=5)

        canvas = tk.Canvas(frame_scroll, highlightthickness=0)
        scrollbar = ttk.Scrollbar(frame_scroll, orient="vertical", command=canvas.yview)
        frame_checks = tk.Frame(canvas)

        frame_checks.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=frame_checks, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        canvas.bind_all("<MouseWheel>", _on_mousewheel) 

        def cerrar_modal():
            canvas.unbind_all("<MouseWheel>")
            modal.destroy()
        modal.protocol("WM_DELETE_WINDOW", cerrar_modal)

        variables_check = {}
        for comuna, cantidad in comunas_disponibles.items():
            var = tk.BooleanVar()
            chk = tk.Checkbutton(frame_checks, text=f"{comuna} ({cantidad} bultos)", variable=var, font=("Arial", 11))
            chk.pack(anchor="w", pady=5)
            variables_check[comuna] = (var, cantidad)

        def confirmar_seleccion():
            for comuna, (var, cantidad) in variables_check.items():
                if var.get(): 
                    ruta_actual['comunas'].append(comuna)
                    ruta_actual['total'] += cantidad
            cerrar_modal()
            self.dibujar_pizarra() 

        tk.Button(frame_botones, text="❌ Cancelar", bg="#c0392b", fg="white", font=("Arial", 10, "bold"), command=cerrar_modal).pack(side=tk.LEFT, padx=15, expand=True)
        tk.Button(frame_botones, text="💾 Agregar a la Ruta", bg="#27ae60", fg="white", font=("Arial", 10, "bold"), command=confirmar_seleccion).pack(side=tk.RIGHT, padx=15, expand=True)

    def refrescar_lista_combobox(self, cb):
        cb['values'] = [f"[{c[0]}] {c[1]} - {c[2]}" for c in bd.obtener_conductores()]

    def validar_capacidad(self, cb, lbl, tot):
        sel = cb.get().upper()
        if "SELECCIONE" in sel or not sel: return
        lim = 35 if "MOTO" in sel else (60 if "AUTO" in sel or "FURGON" in sel or "FURGÓN" in sel else 9999)
        lbl.config(text=f"Bultos: {tot} {'(OK)' if tot <= lim else f'(SOBRECARGA > {lim})'}", fg="#27ae60" if tot <= lim else "#c0392b")

    def aplicar_cirugia(self):
        comuna, destino_str = self.combo_mover_comuna.get(), self.combo_mover_destino.get()
        if not comuna or not destino_str: return
        
        id_destino = int(destino_str.replace("Ruta ", ""))
        canasto_actual = bd.obtener_canasto_db()
        cantidad = len(canasto_actual.get(comuna, []))

        for ruta in self.rutas_borrador:
            if comuna in ruta['comunas']:
                ruta['comunas'].remove(comuna)
                ruta['total'] -= cantidad
                break
        for ruta in self.rutas_borrador:
            if ruta['id'] == id_destino:
                ruta['comunas'].append(comuna)
                ruta['total'] += cantidad
                break
        self.dibujar_pizarra()

    def confirmar_despacho(self):
        if not self.rutas_borrador: return
        canasto_actual = bd.obtener_canasto_db()

        asignaciones = {}
        for id_ruta, var_tk in self.vars_conductores.items():
            sel = var_tk.get()
            if "Seleccione" in sel or not sel: return messagebox.showerror("Error", f"Falta conductor en Ruta #{id_ruta}.")
            asignaciones[id_ruta] = int(sel.split("]")[0].replace("[", ""))

        if not messagebox.askyesno("Confirmar", "¿Cerrar rutas definitivamente?"): return

        for ruta in self.rutas_borrador:
            id_conductor = asignaciones[ruta['id']]
            codigos_ruta = []
            for comuna in ruta['comunas']: codigos_ruta.extend(canasto_actual[comuna])
            if codigos_ruta: bd.cerrar_ruta(codigos_ruta, id_conductor)

        messagebox.showinfo("Éxito", "Despacho confirmado.")
        bd.vaciar_canasto_db() 
        self.actualizar_texto_resumen()
        self.borrado_silencioso_pizarra()
        self.entry_pistola.focus()