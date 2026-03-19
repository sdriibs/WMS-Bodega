import tkinter as tk
from tkinter import ttk, messagebox
import motor_rutas
import base_datos as bd 

class TabEnrutamiento:
    def __init__(self, notebook, comunas_oficiales):
        self.frame_principal = tk.Frame(notebook, bg="#f4f6f9")
        notebook.add(self.frame_principal, text="Armar Rutas de Reparto")
        
        self.comunas_oficiales = comunas_oficiales
        self.rutas_generadas = []
        
        self.construir_interfaz()

    def construir_interfaz(self):
        # Controles superiores
        frame_controles = tk.Frame(self.frame_principal, bg="#f4f6f9", pady=10)
        frame_controles.pack(fill=tk.X, padx=15)

        tk.Label(frame_controles, text="Conductores Disponibles:", bg="#f4f6f9").pack(side=tk.LEFT)
        self.combo_conductores = ttk.Combobox(frame_controles, values=["3", "4", "5", "6", "7"], width=5, state="readonly")
        self.combo_conductores.set("5")
        self.combo_conductores.pack(side=tk.LEFT, padx=10)

        btn_calcular = tk.Button(frame_controles, text="Calcular Rutas Lote", bg="#27ae60", fg="white", command=self.procesar_rutas)
        btn_calcular.pack(side=tk.LEFT, padx=10)

        # Ajuste Manual
        frame_manual = tk.LabelFrame(self.frame_principal, text="Ajuste Manual", bg="#f4f6f9", pady=5, padx=10)
        frame_manual.pack(fill=tk.X, padx=15, pady=5)

        tk.Label(frame_manual, text="Mover Comuna:", bg="#f4f6f9").pack(side=tk.LEFT)
        self.combo_comuna_manual = ttk.Combobox(frame_manual, state="readonly", width=20)
        self.combo_comuna_manual.pack(side=tk.LEFT, padx=5)

        tk.Label(frame_manual, text="Hacia:", bg="#f4f6f9").pack(side=tk.LEFT)
        self.combo_destino_manual = ttk.Combobox(frame_manual, state="readonly", width=15)
        self.combo_destino_manual.pack(side=tk.LEFT, padx=5)

        tk.Button(frame_manual, text="Aplicar Cambio", command=self.mover_comuna).pack(side=tk.LEFT, padx=10)

        # Contenedor de resultados
        self.frame_resultados = tk.Frame(self.frame_principal, bg="white", bd=1, relief=tk.SOLID)
        self.frame_resultados.pack(fill=tk.BOTH, expand=True, padx=15, pady=10)

    def enfocar_pistola(self):
        pass

    def obtener_datos_lote(self):
        # Conectar con db - devolver datos limpios para el motor de rutas
        
        return {
            "SAN_BERNARDO": 85, "SANTIAGO": 70, "PUENTE ALTO": 60,
            "Pedro Aguirre Cerda": 20, "QUILICURA": 50, "LAMPA": 15,
            "MAIPU": 0, "LA FLORIDA": 30
        }

    def procesar_rutas(self):
        datos_hoy = self.obtener_datos_lote()
        conductores = int(self.combo_conductores.get())
        
        self.rutas_generadas = motor_rutas.calcular_rutas(datos_hoy, conductores)
        self.actualizar_pantalla()
        self.actualizar_combos_manuales(datos_hoy)

    def actualizar_pantalla(self):
        for widget in self.frame_resultados.winfo_children():
            widget.destroy()

        for ruta in self.rutas_generadas:
            fila = tk.Frame(self.frame_resultados, bg="white", pady=10)
            fila.pack(fill=tk.X, padx=10, pady=2, anchor="w")

            texto = f"Furgón {ruta['id']} | {ruta['total']} Pkts | Núcleo: {ruta['nucleo']} | Comunas: {', '.join(ruta['comunas'])}"
            
            tk.Label(fila, text=texto, bg="white", font=("Arial", 10)).pack(side=tk.LEFT)
            
            btn_copiar = tk.Button(fila, text="Copiar", command=lambda t=texto: self.copiar_texto(t))
            btn_copiar.pack(side=tk.RIGHT)
            
            tk.Frame(self.frame_resultados, height=1, bg="#e0e0e0").pack(fill=tk.X, padx=10)

    def actualizar_combos_manuales(self, datos_crudos):
        datos_limpios = motor_rutas.normalizar_y_filtrar(datos_crudos)
        self.combo_comuna_manual['values'] = list(datos_limpios.keys())
        self.combo_destino_manual['values'] = [f"Furgón {r['id']}" for r in self.rutas_generadas]

    def mover_comuna(self):
        comuna = self.combo_comuna_manual.get()
        destino_str = self.combo_destino_manual.get()

        if not comuna or not destino_str:
            return

        id_destino = int(destino_str.replace("Furgón ", ""))
        datos_hoy = motor_rutas.normalizar_y_filtrar(self.obtener_datos_lote())
        carga_comuna = datos_hoy.get(comuna, 0)

        # Quitar de la ruta original
        for ruta in self.rutas_generadas:
            if comuna in ruta["comunas"]:
                ruta["comunas"].remove(comuna)
                ruta["total"] -= carga_comuna
                break

        # Agregar a la nueva ruta
        for ruta in self.rutas_generadas:
            if ruta["id"] == id_destino:
                ruta["comunas"].append(comuna)
                ruta["total"] += carga_comuna
                break

        self.actualizar_pantalla()

    def copiar_texto(self, texto):
        self.frame_principal.clipboard_clear()
        self.frame_principal.clipboard_append(texto)
        messagebox.showinfo("Éxito", "Ruta copiada al portapapeles para WhatsApp/Excel.")