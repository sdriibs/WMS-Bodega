import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import pandas as pd
from datetime import datetime
import base_datos as bd

class TabRecepcion:
    def __init__(self, notebook):
        self.frame = tk.Frame(notebook)
        notebook.add(self.frame, text="Recepción de Recogidas")
        
        # Variables de memoria de esta pestaña
        self.base_paquetes = {}
        self.conteo_comunas = {}
        self.conteo_proveedores = {}

        # Interfaz
        frame_top = tk.Frame(self.frame, pady=10)
        frame_top.pack(fill=tk.X)
        tk.Button(frame_top, text="Subir Manifiesto Diario", font=("Arial", 11, "bold"), bg="#007bff", fg="white", command=self.cargar_archivo).pack()
        self.lbl_estado = tk.Label(frame_top, text="Esperando manifiesto...", font=("Arial", 10))
        self.lbl_estado.pack()

        tk.Label(self.frame, text="Pistolear Llegada:", font=("Arial", 12, "bold")).pack()
        self.entrada_rec = tk.Entry(self.frame, font=("Arial", 20), justify="center", width=25)
        self.entrada_rec.pack(pady=5)
        self.entrada_rec.bind('<Return>', self.procesar_recepcion)
        
        self.lbl_res = tk.Label(self.frame, text="ESPERANDO...", font=("Arial", 18, "bold"), width=20, height=2, bg="#e9ecef")
        self.lbl_res.pack(pady=5)

        frame_tablas = tk.Frame(self.frame)
        frame_tablas.pack(fill=tk.BOTH, expand=True, pady=10)
        
        self.arbol_com = ttk.Treeview(frame_tablas, columns=("C", "E", "R"), show="headings")
        self.arbol_com.heading("C", text="Comuna"); self.arbol_com.heading("E", text="Esp"); self.arbol_com.heading("R", text="Rec")
        self.arbol_com.column("C", width=150); self.arbol_com.column("E", width=50); self.arbol_com.column("R", width=50)
        
        self.arbol_prov = ttk.Treeview(frame_tablas, columns=("P", "E", "R"), show="headings")
        self.arbol_prov.heading("P", text="Proveedor"); self.arbol_prov.heading("E", text="Esp"); self.arbol_prov.heading("R", text="Rec")
        self.arbol_prov.column("P", width=150); self.arbol_prov.column("E", width=50); self.arbol_prov.column("R", width=50)
        
        self.arbol_com.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=5)
        self.arbol_prov.pack(side=tk.RIGHT, expand=True, fill=tk.BOTH, padx=5)

    def enfocar_pistola(self):
        self.entrada_rec.focus()

    def cargar_archivo(self):
        ruta = filedialog.askopenfilename(title="Seleccionar manifiesto", filetypes=[("Excel/CSV", "*.xlsx *.csv")])
        if not ruta: return
        try:
            df = pd.read_csv(ruta, sep=None, engine='python') if ruta.endswith('.csv') else pd.read_excel(ruta)
            df.columns = df.columns.astype(str).str.strip().str.upper()
            
            self.base_paquetes.clear(); self.conteo_comunas.clear(); self.conteo_proveedores.clear()
            
            for _, fila in df.iterrows():
                codigo = str(fila.get('NÚMERO DE GUÍA', '')).strip().upper()
                comuna = str(fila.get('CIUDAD', '')).strip().upper()
                proveedor = str(fila.get('NEGOCIO', '')).strip().upper()
                if not codigo or codigo == 'NAN': continue
                
                self.base_paquetes[codigo] = {'comuna': comuna, 'proveedor': proveedor, 'estado': 'Pendiente'}
                bd.insertar_o_actualizar_paquete(codigo, comuna, proveedor, 'Pendiente')
                
                if comuna not in self.conteo_comunas: self.conteo_comunas[comuna] = {'esperados': 0, 'recibidos': 0}
                self.conteo_comunas[comuna]['esperados'] += 1
                if proveedor not in self.conteo_proveedores: self.conteo_proveedores[proveedor] = {'esperados': 0, 'recibidos': 0}
                self.conteo_proveedores[proveedor]['esperados'] += 1
                
            self.actualizar_tablas()
            self.lbl_estado.config(text=f"Manifiesto Cargado: {len(self.base_paquetes)} paquetes", fg="blue")
            self.entrada_rec.focus()
        except Exception as e:
            messagebox.showerror("Error", f"Falló la carga: {e}")

    def procesar_recepcion(self, event):
        codigo = self.entrada_rec.get().strip().upper()
        self.entrada_rec.delete(0, tk.END) 
        if not codigo: return

        if codigo in self.base_paquetes:
            if self.base_paquetes[codigo]['estado'] == 'Pendiente':
                c = self.base_paquetes[codigo]['comuna']
                p = self.base_paquetes[codigo]['proveedor']
                self.base_paquetes[codigo]['estado'] = 'Recibido'
                self.conteo_comunas[c]['recibidos'] += 1
                self.conteo_proveedores[p]['recibidos'] += 1
                
                bd.insertar_o_actualizar_paquete(codigo, c, p, 'Recibido')
                
                self.lbl_res.config(text=f"{c}\n({p})", bg="#28a745", fg="white")
                self.actualizar_tablas()
            else:
                self.lbl_res.config(text="¡DUPLICADO!", bg="#ffc107", fg="black")
        else:
            self.lbl_res.config(text=f"¡NO RECONOCIDO!\n{codigo}", bg="#dc3545", fg="white")

    def actualizar_tablas(self):
        for f in self.arbol_com.get_children(): self.arbol_com.delete(f)
        for f in self.arbol_prov.get_children(): self.arbol_prov.delete(f)
        for c, d in sorted(self.conteo_comunas.items(), key=lambda x: x[1]['esperados'], reverse=True): 
            self.arbol_com.insert("", "end", values=(c, d['esperados'], d['recibidos']))
        for p, d in sorted(self.conteo_proveedores.items(), key=lambda x: x[1]['esperados'], reverse=True): 
            self.arbol_prov.insert("", "end", values=(p, d['esperados'], d['recibidos']))