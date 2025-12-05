import customtkinter as ctk

class VistaPrincipal(ctk.CTkFrame):
    def __init__(self, master, controller, font_family):
        super().__init__(master)
        self.controller = controller
        self.master = master
        self.font_family = font_family # Guardar font_family como atributo de instancia
        self.pack(fill="both", expand=True)
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=0)
        self.grid_columnconfigure(0, weight=1)
        self.frame_contenido = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_contenido.grid(row=0, column=0, sticky="nsew")
        self.crear_barra_navegacion()

    def crear_barra_navegacion(self):
        
        self.frame_nav = ctk.CTkFrame(self, corner_radius=0, fg_color="#000000")
        self.frame_nav.grid(row=1, column=0, sticky="ew")
        self.frame_nav.columnconfigure((0, 1, 2, 3), weight=0)
        self.frame_nav.columnconfigure(4, weight=1)
        boton_estilo = dict(
            corner_radius=20,
            border_width=0,
            fg_color="#6C63FF",
            hover_color="#8C86FF",
            text_color="white",
            font=ctk.CTkFont(family=self.font_family, size=13, weight="bold")
        )

        btn_busqueda = ctk.CTkButton(
            self.frame_nav,
            text="Búsqueda y Consulta",
            command=self.controller.mostrar_busqueda,
            **boton_estilo
        )
        btn_busqueda.grid(row=0, column=0)

        self.btn_admin = ctk.CTkButton(
            self.frame_nav,
            text="Administrar / Login",
            command=self.controller.mostrar_login,
            fg_color="#00C9A7",
            hover_color="#3DE7C0",
            text_color="white",
            font=ctk.CTkFont(family=self.font_family, size=13, weight="bold"),
            corner_radius=20
        )
        self.btn_admin.grid(row=0, column=1)

        estilo_secundario = boton_estilo.copy()
        estilo_secundario.update({"fg_color": "#F2B705", "hover_color": "#FFCF5A"})

        self.btn_exportar_nav = ctk.CTkButton(
            self.frame_nav,
            text="Exportar TEG",
            command=self.controller.exportar_paquete_nav,
            **estilo_secundario
        )
        self.btn_exportar_nav.grid(row=0, column=2)
        self.btn_exportar_nav.grid_remove()

        estilo_oscuro = boton_estilo.copy()
        estilo_oscuro.update({"fg_color": "#FF6B6B", "hover_color": "#FF8B8B"})

        self.btn_importar_nav = ctk.CTkButton(
            self.frame_nav,
            text="Importar TEG",
            command=self.controller.importar_paquete_nav,
            **estilo_oscuro
        )
        self.btn_importar_nav.grid(row=0, column=3)
        self.btn_importar_nav.grid_remove()

        label_titulo_nav = ctk.CTkLabel(
            self.frame_nav,
            text="Repositorio de TEG - UTS Anaco",
            anchor="e",
            font=ctk.CTkFont(family=self.font_family, size=13, weight="bold"),
            text_color="#ECECEC"
        )
        label_titulo_nav.grid(row=0, column=4, padx=(10, 20), pady=14, sticky="e")

    def get_frame_contenido(self):
        return self.frame_contenido

    def actualizar_estado_admin(self, logueado):
        if logueado:
            self.btn_admin.configure(text="Salir", command=self.controller.cerrar_sesion)
            self.btn_exportar_nav.grid()
            self.btn_importar_nav.grid()
            if not hasattr(self, 'btn_gestionar_tesis'):
                self.btn_gestionar_tesis = ctk.CTkButton(
                    self.frame_nav, 
                    text="➕ Agregar TEG",
                    command=self.controller.mostrar_gestion_tesis
                )
                self.btn_gestionar_tesis.grid(row=0, column=4, padx=20, pady=10)
        else:
            self.btn_admin.configure(text="🔑 Administrar / Login", command=self.controller.mostrar_login)
            self.btn_exportar_nav.grid_remove()
            self.btn_importar_nav.grid_remove()
            if hasattr(self, 'btn_gestionar_tesis'):
                self.btn_gestionar_tesis.destroy()
                del self.btn_gestionar_tesis