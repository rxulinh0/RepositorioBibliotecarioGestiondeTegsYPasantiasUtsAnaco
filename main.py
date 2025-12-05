import customtkinter as ctk
from controller.controlador_app import ControladorApp
import os
from PIL import Image
import tkinter.font as tkfont
from PIL import ImageFont

def main():
	ctk.set_appearance_mode("System")
	ctk.set_default_color_theme("themes/coffee.json")
	root = ctk.CTk()

	# Ruta de la fuente
	font_path = os.path.join(os.path.dirname(__file__), "assets", "fonts", "Nunito-ExtraBold.ttf")

	# Cargar la fuente con PIL para obtener su nombre de familia
	try:
		pil_font = ImageFont.truetype(font_path, 1) # El tamaño no importa, solo para obtener el nombre
		font_family = pil_font.font.family
		print(f"DEBUG: Font family detected: {font_family}") # Para depuración
	except Exception as e:
		print(f"ERROR: No se pudo cargar la fuente con PIL: {e}")
		font_family = "Nunito ExtraBold" # Fallback si no se puede cargar con PIL

	# Registrar y configurar las fuentes por defecto de tkinter
	try:
		default_font = tkfont.nametofont("TkDefaultFont")
		default_font.configure(family=font_family, size=14)

		text_font = tkfont.nametofont("TkTextFont")
		text_font.configure(family=font_family, size=14)

		fixed_font = tkfont.nametofont("TkFixedFont")
		fixed_font.configure(family=font_family, size=14)

		# CustomTkinter usa internamente CTkFont. Podemos intentar configurarlo también.
		# ctk.CTkFont utiliza internamente las fuentes de Tkinter, así que esto podría ser redundante
		# pero lo dejamos por si acaso.
		# ctk.set_font(ctk.CTkFont(family=font_family, size=14))

	except Exception as e:
		print(f"WARNING: No se pudo configurar la fuente de Tkinter: {e}")

	ctk.set_widget_scaling(1.0) # Asegúrate de que el escalado no interfiera

	root.title("Repositorio de Biblioteca UTS Anaco")
	root.geometry("1200x800")
	root.minsize(1200,800)
	mostrar_splash(root, font_family)

	root.mainloop()


def mostrar_splash(root, font_family):
	root.withdraw()

	splash = ctk.CTkToplevel()
	splash.overrideredirect(True)
	splash.attributes("-topmost", True)

	width, height = 700, 700
	screen_w = splash.winfo_screenwidth()
	screen_h = splash.winfo_screenheight()
	x = (screen_w // 2) - (width // 2)
	y = (screen_h // 2) - (height // 2)
	splash.geometry(f"{width}x{height}+{x}+{y}")

	frame = ctk.CTkFrame(splash)
	frame.pack(fill="both", expand=True, padx=20, pady=20)
	frame.grid_columnconfigure(0, weight=1)

	logo_path = os.path.join(os.path.dirname(__file__), "assets", "uts_logo.png")
	try:
		img = Image.open(logo_path)
		ctk_img = ctk.CTkImage(light_image=img, dark_image=img, size=(400, 400))
		img_label = ctk.CTkLabel(frame, image=ctk_img, text="")
		img_label.grid(row=0, column=0, pady=(10, 10))
	except Exception:
		pass

	label_titulo = ctk.CTkLabel(frame, text="Sistema de Repositorio de TEG", font=ctk.CTkFont(family=font_family, size=26, weight="bold"))
	label_titulo.grid(row=1, column=0, pady=(40, 0))

	label_subtitulo = ctk.CTkLabel(frame, text="Biblioteca UTS Anaco", font=ctk.CTkFont(family=font_family, size=20))
	label_subtitulo.grid(row=2, column=0, pady=(4, 10))

	def iniciar_app():
		splash.destroy()
		root.deiconify()
		ControladorApp(root, font_family)

	splash.after(2500, iniciar_app)


if __name__ == "__main__":
	main()