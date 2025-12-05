import customtkinter as ctk
from tkinter import ttk, messagebox
import tkinter as tk
import os
import webbrowser

class VistaBusqueda(ctk.CTkFrame):

    def __init__(self, master, controller, font_family):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self.font_family = font_family # Guardar font_family como atributo de instancia
        
        self.grid_rowconfigure(1, weight=1)
        self.grid_columnconfigure(0, weight=1)

        self.crear_controles_busqueda()
        self.crear_treeview()
        self.limpiar_tabla()
        
        self.tree.bind("<Button-1>", self.manejar_clic_tabla)
        self.tree.bind("<Button-3>", self._mostrar_menu_contexto)
        self.tree.bind("<Motion>", self._on_tree_hover) # Para cambiar el cursor al pasar sobre el botón de descarga
        self._context_menu_teg_id = None
        self._crear_menu_contexto()


    def crear_controles_busqueda(self):
        
        frame_busqueda = ctk.CTkFrame(self)
        frame_busqueda.grid(row=0, column=0, sticky="ew", padx=10, pady=(10, 5))
        frame_busqueda.grid_columnconfigure(0, weight=1)
        frame_busqueda.grid_columnconfigure(1, weight=0)
        frame_busqueda.grid_columnconfigure(2, weight=0)
        
        self.entrada_busqueda = ctk.CTkEntry(
            frame_busqueda, 
            placeholder_text="Buscar por Título, Resumen o Palabras Clave del TEG...",
            height=35,
            font=(self.font_family, 14) # Aplicar la fuente
        )
        self.entrada_busqueda.grid(row=0, column=0, sticky="ew", padx=(10, 5), pady=10)

        try:
            lista_carreras = self.controller.obtener_lista_materias()
        except Exception:
            lista_carreras = []
        valores_combo = ["Todas las carreras"] + lista_carreras
        self.combo_carrera = ctk.CTkComboBox(frame_busqueda, values=valores_combo, state="readonly", width=230, font=(self.font_family, 14)) # Aplicar la fuente
        self.combo_carrera.set("Filtrar por Carrera (Escoja una)")
        self.combo_carrera.grid(row=0, column=1, padx=(5, 5), pady=10)
        
        btn_buscar = ctk.CTkButton(
            frame_busqueda, 
            text="Buscar",
            height=35,
            font=(self.font_family, 14), # Aplicar la fuente
            command=self.ejecutar_busqueda_controlador
        )
        btn_buscar.grid(row=0, column=2, padx=(5, 10), pady=10)
        
        self.entrada_busqueda.bind("<Return>", lambda event: self.ejecutar_busqueda_controlador())


    def crear_treeview(self):

        style = ttk.Style()
        style.theme_use("default") 
        style.configure("Treeview", 
                        background="#FFFFFF", 
                        foreground="#000000",
                        rowheight=25,
                        fieldbackground="#FFFFFF",
                        font=(self.font_family, 12)) # Aplicar la fuente a Treeview
        style.configure("Treeview.Heading", font=(self.font_family, 13, 'bold')) # Aplicar la fuente a los encabezados
        style.map('Treeview', background=[('selected', '#1f6aa5')])

        
        columnas = ('Título', 'Autores', 'Carrera', 'Año', 'PDF')
        
        self.tree = ttk.Treeview(self, columns=columnas, show='headings')
        self.tree.grid(row=1, column=0, sticky="nsew", padx=10, pady=(5, 10))
        
        self.tree.heading('Título', text='Título del TEG')
        self.tree.column('Título', width=300, anchor=tk.W)
        
        self.tree.heading('Autores', text='Autor(es)')
        self.tree.column('Autores', width=180, anchor=tk.W)
        
        self.tree.heading('Carrera', text='Carrera')
        self.tree.column('Carrera', width=120, anchor=tk.CENTER)
        
        self.tree.heading('Año', text='Año')
        self.tree.column('Año', width=60, anchor=tk.CENTER)
        
        self.tree.heading('PDF', text='Descargar PDF')
        self.tree.column('PDF', width=100, anchor=tk.CENTER, stretch=False)
        
        scrollbar = ctk.CTkScrollbar(self, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=1, column=1, sticky="ns", pady=(5, 10))
        
        
    def limpiar_tabla(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    
    def actualizar_resultados(self, resultados):

        self.limpiar_tabla()
        
        if not resultados:
            self.tree.insert('', tk.END, values=('No se encontraron resultados.', '', '', '', ''))
            return
            
        for tesis in resultados:

            tesis_id, titulo, autores, materia, anio, ruta_pdf = tesis
            

            self.tree.insert('', tk.END, iid=str(tesis_id),
                             values=(titulo, autores, materia, anio, "⬇️ Descargar"),
                             tags=(ruta_pdf,)
                            )




    def manejar_clic_tabla(self, event):
        
        region = self.tree.identify("region", event.x, event.y)
        
        if region == "cell":
            
            item = self.tree.identify_row(event.y)
            columna = self.tree.identify_column(event.x)
            

            if columna == '#5': 
                
                tags = self.tree.item(item, "tags")
                
                if tags:
                    ruta_pdf = tags[0]
                    self.controller.descargar_pdf(ruta_pdf)
                else:
                    print("Error: No se encontró la ruta del PDF para esta fila.")

    def _on_tree_hover(self, event):
        region = self.tree.identify("region", event.x, event.y)
        columna = self.tree.identify_column(event.x)

        if region == "cell" and columna == '#5': # Columna 'PDF'
            self.tree.config(cursor="hand2")
        else:
            self.tree.config(cursor="")

    def ejecutar_busqueda_controlador(self):

        termino = self.entrada_busqueda.get()
        carrera_sel = None
        if hasattr(self, 'combo_carrera'):
            carrera_sel = self.combo_carrera.get()
        if termino:
            self.controller.ejecutar_busqueda(termino, carrera_sel)
        else:
            self.controller.ejecutar_busqueda("", carrera_sel)


    def _crear_menu_contexto(self):
        self._menu_contexto = tk.Menu(self, tearoff=0)
        self._menu_contexto.add_command(label="Eliminar tesis", command=self._eliminar_tesis_seleccionada)

    def _mostrar_menu_contexto(self, event):
        if not getattr(self.controller, 'admin_logueado', False):
            return
        item = self.tree.identify_row(event.y)
        if not item:
            return
        self._context_menu_teg_id = item
        try:
            self._menu_contexto.tk_popup(event.x_root, event.y_root)
        finally:
            self._menu_contexto.grab_release()

    def _eliminar_tesis_seleccionada(self):
        if not self._context_menu_teg_id:
            return
        if not self.controller.admin_logueado:
            messagebox.showwarning("Acceso Denegado", "Debe iniciar sesión como administrador para eliminar tesis.")
            return
        if not messagebox.askyesno("Eliminar TEG", "¿Estás seguro de que deseas eliminar esta tesis?"):
            return
        teg_id = int(self._context_menu_teg_id)
        if self.controller.eliminar_tesis(teg_id):
            self.tree.delete(self._context_menu_teg_id)
        self._context_menu_teg_id = None

    def mostrar_mensaje(self, mensaje):
        print(f"Estado de la Vista de Búsqueda: {mensaje}")