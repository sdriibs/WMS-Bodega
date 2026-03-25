import tkinter as tk
from tkinter import ttk, messagebox
import base_datos as bd

class TabConductores:
    def __init__(self, notebook):
        self.frame_principal = tk.Frame(notebook)
        notebook.add(self.frame_principal, text="Conductores")
        
        # Variable de estado para saber si estamos creando o editando
        self.id_edicion = None 
        
        self.construir_interfaz()
        self.cargar_datos()

    def construir_interfaz(self):
        frame_form = tk.LabelFrame(self.frame_principal, text="Registro de Conductor", pady=15, padx=15)
        frame_form.pack(side=tk.LEFT, fill=tk.Y, padx=10, pady=10)

        tk.Label(frame_form, text="Nombre Completo:").pack(anchor="w")
        self.entry_nombre = ttk.Entry(frame_form, width=30)
        self.entry_nombre.pack(pady=(0, 15), ipady=3)

        tk.Label(frame_form, text="Tipo de Vehículo:").pack(anchor="w")
        self.combo_vehiculo = ttk.Combobox(frame_form, state="readonly", width=27)
        self.combo_vehiculo['values'] = ["AUTO", "FURGON", "MOTO", "CAMION"]
        self.combo_vehiculo.pack(pady=(0, 20), ipady=3)

        # Guardamos la referencia del botón para poder cambiarle el texto y color
        self.btn_guardar = tk.Button(frame_form, text="Guardar Nuevo", command=self.guardar_conductor, bg="#27ae60", fg="white")
        self.btn_guardar.pack(fill=tk.X, pady=5)

        btn_editar = tk.Button(frame_form, text="Editar Seleccionado", command=self.preparar_edicion, bg="#2980b9", fg="white")
        btn_editar.pack(fill=tk.X, pady=5)

        btn_eliminar = tk.Button(frame_form, text="Eliminar Seleccionado", command=self.eliminar_seleccionado, bg="#c0392b", fg="white")
        btn_eliminar.pack(fill=tk.X, pady=5)

        # Botón para cancelar la edición y limpiar el formulario
        self.btn_cancelar = tk.Button(frame_form, text="Cancelar Edición", command=self.limpiar_formulario, fg="#7f8c8d")
        
        frame_tabla = tk.Frame(self.frame_principal)
        frame_tabla.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=10, pady=10)

        columnas = ("id", "nombre", "vehiculo")
        self.tabla = ttk.Treeview(frame_tabla, columns=columnas, show="headings")
        
        self.tabla.heading("id", text="ID")
        self.tabla.heading("nombre", text="Nombre Conductor")
        self.tabla.heading("vehiculo", text="Tipo de Vehículo")

        self.tabla.column("id", width=50, anchor="center")
        self.tabla.column("nombre", width=200)
        self.tabla.column("vehiculo", width=150, anchor="center")

        scrollbar = ttk.Scrollbar(frame_tabla, orient=tk.VERTICAL, command=self.tabla.yview)
        self.tabla.configure(yscroll=scrollbar.set)

        self.tabla.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

    def cargar_datos(self):
        for item in self.tabla.get_children():
            self.tabla.delete(item)
            
        conductores = bd.obtener_conductores()
        for cond in conductores:
            self.tabla.insert("", tk.END, values=cond)

    def preparar_edicion(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showinfo("Aviso", "Selecciona un conductor de la tabla para editar.")
            return

        item = self.tabla.item(seleccion)
        self.id_edicion = item['values'][0]
        nombre_actual = item['values'][1]
        vehiculo_actual = item['values'][2]

        # Llenado del formulario con los datos seleccionados
        self.entry_nombre.delete(0, tk.END)
        self.entry_nombre.insert(0, nombre_actual)
        self.combo_vehiculo.set(vehiculo_actual)

        # Cambio de aspecto visual para indicar modo edición
        self.btn_guardar.config(text="Actualizar Registro", bg="#d35400") # Color naranja
        self.btn_cancelar.pack(fill=tk.X, pady=(15, 0)) # Mostramos botón cancelar

    def guardar_conductor(self):
        nombre = self.entry_nombre.get().strip().upper()
        vehiculo = self.combo_vehiculo.get()

        if not nombre or not vehiculo:
            messagebox.showwarning("Error", "Debes completar el nombre y seleccionar un vehículo.")
            return

        if self.id_edicion is None:
            # Flujo de creación
            bd.insertar_conductor(nombre, vehiculo)
        else:
            # Flujo de actualización
            bd.actualizar_conductor(self.id_edicion, nombre, vehiculo)
        
        self.limpiar_formulario()
        self.cargar_datos()

    def limpiar_formulario(self):
        self.id_edicion = None
        self.entry_nombre.delete(0, tk.END)
        self.combo_vehiculo.set('')
        
        # Restaurar aspecto visual original
        self.btn_guardar.config(text="Guardar Nuevo", bg="#27ae60")
        self.btn_cancelar.pack_forget()

    def eliminar_seleccionado(self):
        seleccion = self.tabla.selection()
        if not seleccion:
            messagebox.showinfo("Aviso", "Selecciona un conductor de la lista para eliminar.")
            return
            
        if messagebox.askyesno("Confirmar", "¿Seguro que deseas eliminar este registro?"):
            item = self.tabla.item(seleccion)
            id_conductor = item['values'][0]
            
            bd.eliminar_conductor(id_conductor)
            
            # Limpiar el formulario
            if self.id_edicion == id_conductor:
                self.limpiar_formulario()
                
            self.cargar_datos()

    def enfocar_pistola(self):
            # Esta pestaña no usa lector de códigos de barra, así que no hace nada
            pass