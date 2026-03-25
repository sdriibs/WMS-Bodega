import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import pandas as pd
import sqlite3
import os

class ExportadorRapido:
    def __init__(self, root):
        self.root = root
        self.root.title("Exportador Rápido a Excel")
        self.root.geometry("600x500")
        self.root.configure(bg="#f0f0f0")
        
        # Diccionario principal: { "SANTIAGO": ["1234", "5678"], "PAC": ["9999"] }
        self.datos_escaneados = {}
        self.total_paquetes = 0

        self.construir_interfaz()

    def conectar_db(self):
        # Conecta a la misma base de datos del sistema principal
        if not os.path.exists("wms_operacion.db"):
            messagebox.showerror("Error", "No se encontró la base de datos 'wms_operacion.db'.")
            return None
        return sqlite3.connect("wms_operacion.db")

    def construir_interfaz(self):
        # --- ZONA DE ESCANEO ---
        frame_top = tk.Frame(self.root, bg="#f0f0f0", pady=20, padx=20)
        frame_top.pack(fill=tk.X)

        tk.Label(frame_top, text="Pistolear Código:", font=("Arial", 12, "bold"), bg="#f0f0f0").pack(side=tk.LEFT)
        self.entry_codigo = ttk.Entry(frame_top, width=30, font=("Arial", 12))
        self.entry_codigo.pack(side=tk.LEFT, padx=15)
        self.entry_codigo.bind("<Return>", self.procesar_codigo)
        self.entry_codigo.focus()

        # --- ZONA DE REGISTRO VISUAL ---
        frame_mid = tk.LabelFrame(self.root, text="Resumen de Lectura", bg="#f0f0f0", padx=10, pady=10)
        frame_mid.pack(fill=tk.BOTH, expand=True, padx=20)

        self.txt_resumen = tk.Text(frame_mid, font=("Arial", 11), state=tk.DISABLED, bg="white")
        self.txt_resumen.pack(fill=tk.BOTH, expand=True)

        # --- ZONA DE EXPORTACIÓN ---
        frame_bot = tk.Frame(self.root, bg="#f0f0f0", pady=15, padx=20)
        frame_bot.pack(fill=tk.X)

        self.lbl_contador = tk.Label(frame_bot, text="Total escaneados: 0", font=("Arial", 12, "bold"), bg="#f0f0f0", fg="#2980b9")
        self.lbl_contador.pack(side=tk.LEFT)

        btn_exportar = tk.Button(frame_bot, text="📊 Exportar a Excel", bg="#27ae60", fg="white", font=("Arial", 11, "bold"), command=self.generar_excel)
        btn_exportar.pack(side=tk.RIGHT)
        
        btn_limpiar = tk.Button(frame_bot, text="🧹 Limpiar", bg="#c0392b", fg="white", font=("Arial", 11), command=self.limpiar_datos)
        btn_limpiar.pack(side=tk.RIGHT, padx=15)

    def procesar_codigo(self, event=None):
        codigo = self.entry_codigo.get().strip().upper()
        if not codigo: return

        # 1. Evitar duplicados en el escaneo actual
        for lista_codigos in self.datos_escaneados.values():
            if codigo in lista_codigos:
                messagebox.showwarning("Duplicado", f"El código {codigo} ya fue escaneado en esta sesión.")
                self.entry_codigo.delete(0, tk.END)
                return

        # 2. Consultar a la base de datos
        conexion = self.conectar_db()
        if not conexion: return
        
        cursor = conexion.cursor()
        cursor.execute("SELECT comuna FROM paquetes WHERE codigo_barras = ?", (codigo,))
        resultado = cursor.fetchone()
        conexion.close()

        # 3. Clasificar el resultado
        if resultado:
            comuna = resultado[0]
            if comuna not in self.datos_escaneados:
                self.datos_escaneados[comuna] = []
            
            self.datos_escaneados[comuna].append(codigo)
            self.total_paquetes += 1
            self.actualizar_pantalla()
        else:
            messagebox.showerror("No Encontrado", f"El paquete {codigo} NO existe en la base de datos. No se puede clasificar.")

        self.entry_codigo.delete(0, tk.END)
        self.entry_codigo.focus()

    def actualizar_pantalla(self):
        self.txt_resumen.config(state=tk.NORMAL)
        self.txt_resumen.delete(1.0, tk.END)
        
        for comuna, codigos in self.datos_escaneados.items():
            self.txt_resumen.insert(tk.END, f"📌 {comuna} ({len(codigos)} paquetes)\n")
            
        self.txt_resumen.config(state=tk.DISABLED)
        self.lbl_contador.config(text=f"Total escaneados: {self.total_paquetes}")

    def limpiar_datos(self):
        if messagebox.askyesno("Confirmar", "¿Borrar todo lo escaneado?"):
            self.datos_escaneados.clear()
            self.total_paquetes = 0
            self.actualizar_pantalla()
            self.entry_codigo.focus()

    def generar_excel(self):
        if not self.datos_escaneados:
            messagebox.showwarning("Vacío", "No hay paquetes escaneados para exportar.")
            return

        # Pedir al usuario dónde guardar el archivo
        ruta_guardado = filedialog.asksaveasfilename(
            defaultextension=".xlsx",
            filetypes=[("Excel files", "*.xlsx")],
            title="Guardar reporte como..."
        )
        
        if not ruta_guardado: return

        try:
            df = pd.DataFrame(dict([ (k, pd.Series(v)) for k, v in self.datos_escaneados.items() ]))
            
            df.to_excel(ruta_guardado, index=False)
            
            messagebox.showinfo("Éxito", f"Reporte Excel generado correctamente en:\n{ruta_guardado}")
            
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo generar el Excel:\n{str(e)}")

if __name__ == "__main__":
    root = tk.Tk()
    app = ExportadorRapido(root)
    root.mainloop()