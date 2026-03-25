import tkinter as tk
from tkinter import ttk
import sqlite3
from datetime import datetime

class TabAuditoria:
    def __init__(self, notebook):
        self.frame_principal = tk.Frame(notebook)
        notebook.add(self.frame_principal, text="4. Cuadratura Bodega")
        self.construir_interfaz()

    def construir_interfaz(self):
        # Cabecera
        frame_top = tk.Frame(self.frame_principal, pady=20, padx=20)
        frame_top.pack(fill=tk.X)
        tk.Label(frame_top, text="DASHBOARD DE AUDITORÍA Y CUADRATURA", font=("Arial", 16, "bold"), fg="#2c3e50").pack(side=tk.LEFT)
        tk.Button(frame_top, text="🔄 Actualizar Datos", bg="#34495e", fg="white", font=("Arial", 11, "bold"), command=self.calcular_cuadratura).pack(side=tk.RIGHT)

        # Paneles de datos
        self.frame_paneles = tk.Frame(self.frame_principal, padx=20)
        self.frame_paneles.pack(fill=tk.X, pady=10)

        # Panel 1: Frescos
        self.panel_fresco = tk.LabelFrame(self.frame_paneles, text="Carga Fresca (Hoy antes de 22:00)", font=("Arial", 11, "bold"), fg="#27ae60", bd=2, padx=15, pady=15)
        self.panel_fresco.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        self.lbl_fresco_am = tk.Label(self.panel_fresco, text="AM: 0", font=("Arial", 14))
        self.lbl_fresco_am.pack()
        self.lbl_fresco_pm = tk.Label(self.panel_fresco, text="PM: 0", font=("Arial", 14))
        self.lbl_fresco_pm.pack()
        self.lbl_fresco_total = tk.Label(self.panel_fresco, text="Total Fresca: 0", font=("Arial", 18, "bold"), fg="#27ae60", pady=10)
        self.lbl_fresco_total.pack()

        # Panel 2: Rezagados / Antiguos
        self.panel_viejo = tk.LabelFrame(self.frame_paneles, text="Carga Antigua / Rezagada", font=("Arial", 11, "bold"), fg="#c0392b", bd=2, padx=15, pady=15)
        self.panel_viejo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        self.lbl_viejo_desc = tk.Label(self.panel_viejo, text="Vencida (>22h) o Histórica", font=("Arial", 10), fg="gray")
        self.lbl_viejo_desc.pack()
        self.lbl_viejo_total = tk.Label(self.panel_viejo, text="Total Antigua: 0", font=("Arial", 18, "bold"), fg="#c0392b", pady=20)
        self.lbl_viejo_total.pack()

        # Panel 3: Total Físico Esperado
        self.panel_total = tk.LabelFrame(self.frame_paneles, text="TOTAL FÍSICO ESPERADO EN GALPÓN", font=("Arial", 11, "bold"), bg="#f1c40f", bd=2, padx=15, pady=15)
        self.panel_total.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=10)
        tk.Label(self.panel_total, text="(Todo lo que NO está en ruta)", font=("Arial", 10), bg="#f1c40f").pack()
        self.lbl_total_bodega = tk.Label(self.panel_total, text="0 PAQUETES", font=("Arial", 22, "bold"), bg="#f1c40f", pady=15)
        self.lbl_total_bodega.pack()

        self.calcular_cuadratura()

    def calcular_cuadratura(self):
        conexion = sqlite3.connect("wms_operacion.db")
        cursor = conexion.cursor()
        
        # Traemos todo lo que está físicamente en bodega (cualquier cosa que NO sea EN_RUTA)
        cursor.execute("SELECT tanda, fecha_hora FROM paquetes WHERE estado != 'EN_RUTA'")
        paquetes_en_bodega = cursor.fetchall()
        conexion.close()

        ahora = datetime.now()
        hoy_str = ahora.strftime("%Y-%m-%d")
        
        # Regla de las 22:00
        ya_son_las_10 = ahora.hour >= 22

        frescos_am = 0
        frescos_pm = 0
        viejos = 0

        for tanda, fecha_hora in paquetes_en_bodega:
            es_viejo = False
            
            # Si no tiene fecha, o es HISTORICO, es viejo automático
            if not fecha_hora or tanda == "HISTORICO":
                es_viejo = True
            else:
                # Extraer solo la fecha (YYYY-MM-DD)
                fecha_paquete = fecha_hora.split(" ")[0]
                
                if fecha_paquete != hoy_str:
                    es_viejo = True # Es de ayer o antes
                elif ya_son_las_10:
                    es_viejo = True # Es de hoy, pero ya pasaron las 22:00
                    
            if es_viejo:
                viejos += 1
            else:
                if tanda == "AM": frescos_am += 1
                elif tanda == "PM": frescos_pm += 1

        total_fresco = frescos_am + frescos_pm
        total_bodega = total_fresco + viejos

        # Actualizar UI
        self.lbl_fresco_am.config(text=f"AM: {frescos_am}")
        self.lbl_fresco_pm.config(text=f"PM: {frescos_pm}")
        self.lbl_fresco_total.config(text=f"Total Fresca: {total_fresco}")
        self.lbl_viejo_total.config(text=f"Total Antigua: {viejos}")
        self.lbl_total_bodega.config(text=f"{total_bodega} PAQUETES")

    def enfocar_pistola(self): pass