import customtkinter as ctk
from tkinter import messagebox

class VistaLogin(ctk.CTkFrame):

    def __init__(self, master, controller, font_family):
        super().__init__(master, fg_color="transparent")
        self.controller = controller
        self.font_family = font_family # Guardar font_family como atributo de instancia
        
        self.grid_rowconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)
        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(2, weight=1)
        
        self.crear_formulario()


    def crear_formulario(self):
        
        frame_login = ctk.CTkFrame(self)
        frame_login.grid(row=1, column=1, padx=20, pady=20, sticky="nsew")
        
        frame_login.columnconfigure(0, weight=1)
        frame_login.columnconfigure(1, weight=1)
        
        ctk.CTkLabel(
            frame_login, 
            text="🔑 ACCESO ADMINISTRADOR", 
            font=ctk.CTkFont(family=self.font_family, size=20, weight="bold")
        ).grid(row=0, column=0, columnspan=2, padx=30, pady=(20, 30), sticky="n")
    
        ctk.CTkLabel(frame_login, text="Usuario:", font=(self.font_family, 14)).grid(row=1, column=0, padx=20, pady=5, sticky="w")
        self.entry_usuario = ctk.CTkEntry(frame_login, placeholder_text="Nombre de Usuario", width=250, font=(self.font_family, 14))
        self.entry_usuario.grid(row=2, column=0, columnspan=2, padx=20, pady=(0, 15), sticky="ew")
    
        ctk.CTkLabel(frame_login, text="Contraseña:", font=(self.font_family, 14)).grid(row=3, column=0, padx=20, pady=5, sticky="w")
        self.entry_password = ctk.CTkEntry(frame_login, placeholder_text="Contraseña", show="*", width=250, font=(self.font_family, 14))
        self.entry_password.grid(row=4, column=0, columnspan=2, padx=20, pady=(0, 30), sticky="ew")
        
        self.entry_password.bind("<Return>", lambda event: self.intentar_login_ui())
    
        btn_login = ctk.CTkButton(
            frame_login, 
            text="Iniciar Sesión",
            command=self.intentar_login_ui,
            height=40,
            font=(self.font_family, 16, "bold") # Aplicar fuente al botón de login
        )
        btn_login.grid(row=5, column=0, columnspan=2, padx=20, pady=(0, 20), sticky="ew")
        
        self.label_mensaje = ctk.CTkLabel(frame_login, text="", text_color="red", font=(self.font_family, 12)) # Aplicar fuente al mensaje de error
        self.label_mensaje.grid(row=6, column=0, columnspan=2, padx=20, pady=(0, 10))
    

    def intentar_login_ui(self):
        usuario = self.entry_usuario.get()
        password = self.entry_password.get()
        
        self.label_mensaje.configure(text="")

        if not usuario or not password:
            self.label_mensaje.configure(text="Complete todos los campos.")
            return

        login_exitoso = self.controller.intentar_login(usuario, password)

        if login_exitoso:
            messagebox.showinfo("Éxito", "¡Inicio de sesión como administrador exitoso!")
        else:
            self.label_mensaje.configure(text="Error de credenciales. Intente de nuevo.")
            self.entry_password.delete(0, 'end')
