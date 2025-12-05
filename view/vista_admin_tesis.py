import customtkinter as ctk
from tkinter import filedialog, messagebox, ttk

from core.pdf_parser import extraer_datos_pdf

class VistaAdminTesis(ctk.CTkFrame):


    def __init__(self, master, controller, font_family):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self.font_family = font_family # Guardar font_family como atributo de instancia
        
        self.ruta_pdf_origen = None 
        
        self.grid_columnconfigure(1, weight=1)
        
        # Configuración de fuentes para etiquetas y entradas
        label_font = (self.font_family, 14)
        entry_font = (self.font_family, 14)
        button_font = (self.font_family, 14, "bold")
        heading_font = (self.font_family, 13, 'bold')
        
        ctk.CTkLabel(self, text="Título:", font=label_font).grid(row=0, column=0, padx=10, pady=5, sticky="w")
        self.entry_titulo = ctk.CTkEntry(self, width=300, font=entry_font)
        self.entry_titulo.grid(row=0, column=1, padx=10, pady=5, sticky="ew")
        
        ctk.CTkLabel(self, text="Resumen:", font=label_font).grid(row=1, column=0, padx=10, pady=5, sticky="w")
        self.entry_resumen = ctk.CTkTextbox(self, height=100, font=entry_font)
        self.entry_resumen.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self, text="Año:", font=label_font).grid(row=2, column=0, padx=10, pady=5, sticky="w")
        self.entry_anio = ctk.CTkEntry(self, font=entry_font)
        self.entry_anio.grid(row=2, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self, text="Palabras Clave:", font=label_font).grid(row=3, column=0, padx=10, pady=5, sticky="w")
        self.entry_palabras = ctk.CTkEntry(self, placeholder_text="separadas,por,comas", font=entry_font)
        self.entry_palabras.grid(row=3, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self, text="Carrera:", font=label_font).grid(row=4, column=0, padx=10, pady=5, sticky="w")
        lista_carreras = self.controller.obtener_lista_materias() 
        self.combo_carrera = ctk.CTkComboBox(self, values=lista_carreras, state="readonly", font=entry_font)
        self.combo_carrera.grid(row=4, column=1, padx=10, pady=5, sticky="ew")

        ctk.CTkLabel(self, text="Autores del TEG:", font=label_font).grid(row=5, column=0, padx=10, pady=(15, 5), sticky="nw")

        frame_autores = ctk.CTkFrame(self)
        frame_autores.grid(row=5, column=1, padx=10, pady=(10, 5), sticky="ew")
        frame_autores.grid_columnconfigure(0, weight=1)
        frame_autores.grid_columnconfigure(1, weight=1)

        self.entry_autor_nombre = ctk.CTkEntry(frame_autores, placeholder_text="Nombre", font=entry_font)
        self.entry_autor_nombre.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="ew")

        self.entry_autor_apellido = ctk.CTkEntry(frame_autores, placeholder_text="Apellido", font=entry_font)
        self.entry_autor_apellido.grid(row=0, column=1, padx=(5, 0), pady=5, sticky="ew")

        btn_agregar_autor = ctk.CTkButton(frame_autores, text="Agregar Autor", command=self.agregar_autor_a_lista, height=30, font=button_font)
        btn_agregar_autor.grid(row=1, column=0, columnspan=2, padx=0, pady=(5, 10), sticky="ew")

        # Estilo para Treeview de autores
        style_autores = ttk.Style()
        style_autores.theme_use("default") 
        style_autores.configure("Treeview.Authors", 
                                background="#FFFFFF", 
                                foreground="#000000",
                                rowheight=25,
                                fieldbackground="#FFFFFF",
                                font=(self.font_family, 12))
        style_autores.configure("Treeview.Heading.Authors", font=heading_font)
        style_autores.map('Treeview.Authors', background=[('selected', '#1f6aa5')])

        self.tree_autores = ttk.Treeview(frame_autores, columns=("Nombre", "Apellido"), show="headings", height=4, style="Treeview.Authors")
        self.tree_autores.heading("Nombre", text="Nombre")
        self.tree_autores.heading("Apellido", text="Apellido")
        self.tree_autores.column("Nombre", width=120)
        self.tree_autores.column("Apellido", width=120)
        self.tree_autores.grid(row=2, column=0, columnspan=2, sticky="nsew")

        scrollbar_autores = ctk.CTkScrollbar(frame_autores, command=self.tree_autores.yview)
        self.tree_autores.configure(yscrollcommand=scrollbar_autores.set)
        scrollbar_autores.grid(row=2, column=2, sticky="ns")

        btn_eliminar_autor = ctk.CTkButton(frame_autores, text="Eliminar Autor", command=self.eliminar_autor_seleccionado, height=28, font=button_font)
        btn_eliminar_autor.grid(row=3, column=0, columnspan=2, padx=0, pady=(5, 0), sticky="ew")

        ctk.CTkLabel(self, text="Archivo PDF:", font=label_font).grid(row=6, column=0, padx=10, pady=5, sticky="w")
        frame_pdf = ctk.CTkFrame(self, fg_color="transparent")
        frame_pdf.grid(row=6, column=1, padx=10, pady=5, sticky="ew")
        frame_pdf.grid_columnconfigure(0, weight=0)
        frame_pdf.grid_columnconfigure(1, weight=0)
        frame_pdf.grid_columnconfigure(2, weight=1)

        self.btn_seleccionar_pdf = ctk.CTkButton(frame_pdf, text="Seleccionar PDF...", command=self.seleccionar_pdf, font=button_font)
        self.btn_seleccionar_pdf.grid(row=0, column=0, padx=(0, 5), pady=5, sticky="w")

        self.btn_escanear_pdf = ctk.CTkButton(frame_pdf, text="Escanear Metadatos", command=self._intentar_autocompletar_desde_pdf, font=button_font)
        self.btn_escanear_pdf.grid(row=0, column=1, padx=(0, 5), pady=5, sticky="w")

        self.label_pdf_seleccionado = ctk.CTkLabel(frame_pdf, text="Ningún archivo seleccionado.", text_color="gray", font=label_font)
        self.label_pdf_seleccionado.grid(row=0, column=2, padx=(5, 0), pady=5, sticky="w")

        self.btn_guardar = ctk.CTkButton(self, text="Guardar TEG", height=40, command=self.guardar_tesis, font=(self.font_family, 16, "bold"))
        self.btn_guardar.grid(row=8, column=0, columnspan=2, padx=10, pady=(20, 5), sticky="ew")

        frame_sincronizacion = ctk.CTkFrame(self, fg_color="transparent")
        frame_sincronizacion.grid(row=9, column=0, columnspan=2, padx=10, pady=(0, 20), sticky="ew")
        frame_sincronizacion.grid_columnconfigure(0, weight=1)
        frame_sincronizacion.grid_columnconfigure(1, weight=1)

        btn_exportar = ctk.CTkButton(frame_sincronizacion, text="Exportar TEG", command=self.exportar_tesis, font=button_font)
        btn_exportar.grid(row=0, column=0, padx=(0, 5), sticky="ew")
        btn_importar = ctk.CTkButton(frame_sincronizacion, text="Importar TEG", command=self.importar_tesis, font=button_font)
        btn_importar.grid(row=0, column=1, padx=(5, 0), sticky="ew")

    def seleccionar_pdf(self):
        """Abre un diálogo para seleccionar el archivo PDF local."""
        ruta = filedialog.askopenfilename(
            title="Seleccionar TEG (PDF)",
            filetypes=[("Archivos PDF", "*.pdf")]
        )
        if ruta:
            self.ruta_pdf_origen = ruta
            self.label_pdf_seleccionado.configure(text=ruta.split('/')[-1])
            self._intentar_autocompletar_desde_pdf()

    def agregar_autor_a_lista(self):
        nombre = self.entry_autor_nombre.get().strip()
        apellido = self.entry_autor_apellido.get().strip()

        if not nombre or not apellido:
            messagebox.showwarning("Autor incompleto", "Debe ingresar nombre y apellido del autor.")
            return

        self.tree_autores.insert("", "end", values=(nombre, apellido))
        self.entry_autor_nombre.delete(0, "end")
        self.entry_autor_apellido.delete(0, "end")

    def eliminar_autor_seleccionado(self):
        seleccionado = self.tree_autores.selection()
        for item in seleccionado:
            self.tree_autores.delete(item)

    def guardar_tesis(self):
        if not self.ruta_pdf_origen:
            messagebox.showerror("Error", "Debe seleccionar un archivo PDF.")
            return

        autores = []
        for item in self.tree_autores.get_children():
            nombre, apellido = self.tree_autores.item(item, "values")
            autores.append((nombre, apellido))

        if not autores:
            if not messagebox.askyesno("Sin autores", "No ha agregado autores para este TEG. ¿Desea continuar de todos modos?"):
                return

        datos_formulario = {
            'titulo': self.entry_titulo.get(),
            'resumen': self.entry_resumen.get("1.0", "end-1c"), # Obtener texto del Textbox
            'anio': self.entry_anio.get(),
            'palabras_clave': self.entry_palabras.get(),
            'carrera_nombre': self.combo_carrera.get(),
            'ruta_pdf_origen_local': self.ruta_pdf_origen,
            'autores': autores
        }

        self.controller.procesar_nueva_tesis(datos_formulario)

    def exportar_tesis(self):
        ruta = filedialog.asksaveasfilename(
            title="Exportar paquete de TEG",
            defaultextension=".zip",
            filetypes=[("Archivo ZIP", "*.zip")]
        )
        if not ruta:
            return
        if self.controller.exportar_paquete_tesis(ruta):
            messagebox.showinfo("Exportación completada", "Se generó el paquete con las tesis seleccionadas.")

    def importar_tesis(self):
        ruta = filedialog.askopenfilename(
            title="Importar paquete de TEG",
            filetypes=[("Archivos ZIP", "*.zip")]
        )
        if not ruta:
            return
        sobrescribir = messagebox.askyesno("Sobrescribir registros", "¿Deseas reemplazar los TEG existentes cuando el GUID coincida?")
        resultado = self.controller.importar_paquete_tesis(ruta, sobrescribir=sobrescribir)
        if resultado:
            mensaje = (
                f"Importación finalizada:\n" \
                f"  - TEG importados: {resultado.get('tegs_importados', 0)}\n" \
                f"  - TEG actualizados: {resultado.get('tegs_actualizados', 0)}\n" \
                f"  - Autores creados: {resultado.get('autores_creados', 0)}"
            )
            messagebox.showinfo("Importación completada", mensaje)

    def _intentar_autocompletar_desde_pdf(self):
        if not self.ruta_pdf_origen:
            return
        datos = extraer_datos_pdf(self.ruta_pdf_origen)
        if not datos:
            return

        if datos.get('titulo') and not self.entry_titulo.get().strip():
            self.entry_titulo.delete(0, 'end')
            self.entry_titulo.insert(0, datos['titulo'])

        if datos.get('resumen') and not self.entry_resumen.get('1.0', 'end-1c').strip():
            self.entry_resumen.delete('1.0', 'end')
            self.entry_resumen.insert('1.0', datos['resumen'])

        if datos.get('anio') and not self.entry_anio.get().strip():
            self.entry_anio.delete(0, 'end')
            self.entry_anio.insert(0, datos['anio'])

        if datos.get('palabras_clave') and not self.entry_palabras.get().strip():
            self.entry_palabras.delete(0, 'end')
            self.entry_palabras.insert(0, datos['palabras_clave'])

        if datos.get('autores') and not self.tree_autores.get_children():
            self._cargar_autores_detectados(datos['autores'])

    def _cargar_autores_detectados(self, autores):
        for autor in self.tree_autores.get_children():
            self.tree_autores.delete(autor)
        for nombre, apellido in autores:
            self.tree_autores.insert('', 'end', values=(nombre, apellido))