from core.manager_base_de_datos import ManagerBaseDeDatos
from typing import Dict, Optional

from core.manager_autenticacion import ManagerAutenticacion
from view.vista_principal import VistaPrincipal
from view.vista_inicio_de_sesion import VistaLogin
from view.vista_busqueda import VistaBusqueda
from view.vista_admin_tesis import VistaAdminTesis
import webbrowser
import os
import shutil
import re
import unicodedata
import datetime
import traceback
from tkinter import filedialog, messagebox

from core import sync_manager

import core.config as config

class ControladorApp:
    def __init__(self, master_root, font_family):
        self.master = master_root
        self.font_family = font_family

        self.admin_logueado = False
        self._datos_cache_canvas = {}

        try:
            self.db_manager = ManagerBaseDeDatos()
            self.auth_manager = ManagerAutenticacion()
        
        except Exception as e:
            print(f"Error fatal al inicializar modelos: {e}")
            self.master.quit()
        
        self.vista_principal = VistaPrincipal(master_root, self, self.font_family)
        print("Controlador: VistaPrincipal inicializada")

        self.vista_contenido_actual = None
        self.mostrar_busqueda()

    def cargar_vista_en_contenido(self, clase_vista):
        if self.vista_contenido_actual is not None:
            self.vista_contenido_actual.destroy()

        frame_contenido = self.vista_principal.get_frame_contenido()
        self.vista_contenido_actual = clase_vista(frame_contenido, self, self.font_family)
        self.vista_contenido_actual.pack(fill="both", expand=True)

    def cargar_vista(self, clase_vista):
        self.cargar_vista_en_contenido(clase_vista)

    def mostrar_busqueda(self):
        self.cargar_vista_en_contenido(VistaBusqueda)
    
    def descargar_pdf(self, ruta_archivo_pdf):
        print(f"Controlador: Solicitud de descarga/apertura para: {ruta_archivo_pdf}")

        try:
            webbrowser.open(ruta_archivo_pdf)
            print("Controlador: Intentando abrir el archivo con el navegador/sistema.")
            
        except Exception as e:
            print(f"Error al intentar abrir el archivo: {e}")
    def mostrar_login(self):
        self.cargar_vista_en_contenido(VistaLogin)


    def intentar_login(self, usuario, password):
        es_valido = self.auth_manager.verificar_credenciales(usuario, password)
        
        if es_valido:
            self.admin_logueado = True
            print("Controlador: Login exitoso.")
            self.vista_principal.actualizar_estado_admin(True)
            self.mostrar_consulta()
            return True
        else:
            print("Controlador: Login fallido.")
            return False

    def ejecutar_busqueda(self, termino, carrera_nombre=None):
        if not termino:
            termino = ""
            
        carrera_id = None
        if carrera_nombre and carrera_nombre.strip() and not carrera_nombre.startswith("Todas"):
            if not hasattr(self, 'carreras_mapa') or not self.carreras_mapa:
                self.obtener_lista_materias()
            carrera_id = self.carreras_mapa.get(carrera_nombre)

        resultados = self.db_manager.buscar_libros_o_tesis(termino, carrera_id)
        
        if isinstance(self.vista_contenido_actual, VistaBusqueda):
            self.vista_contenido_actual.actualizar_resultados(resultados)
        else:
            print("Error: El controlador intentó actualizar resultados en una vista incorrecta.")
    def mostrar_gestion_tesis(self):
        if self.admin_logueado:
            self.cargar_vista_en_contenido(VistaAdminTesis)
        else:
            messagebox.showwarning("Acceso Denegado", "Debe iniciar sesión como administrador.")
            self.mostrar_login()

    def mostrar_consulta(self):
        self.mostrar_busqueda()

    def cerrar_sesion(self):
        self.admin_logueado = False
        try:
            self.vista_principal.actualizar_estado_admin(False)
        except Exception:
            pass
        self.mostrar_busqueda()

    def eliminar_tesis(self, teg_id: int) -> bool:
        resultado, ruta_pdf = self.db_manager.eliminar_teg(teg_id)
        if resultado and ruta_pdf and os.path.exists(ruta_pdf):
            try:
                os.remove(ruta_pdf)
            except Exception as exc:
                print(f"Advertencia: no se pudo eliminar el PDF asociado: {exc}")
        return resultado

    def obtener_lista_materias(self):
        carreras_tuplas = self.db_manager.obtener_todas_materias() 
        
        self.carreras_mapa = {nombre: id_car for id_car, nombre in carreras_tuplas}
        
        return [nombre for id_car, nombre in carreras_tuplas]

    def procesar_nueva_tesis(self, datos_formulario):  
        try:
            anio = int(datos_formulario['anio'])
            carrera_nombre = datos_formulario['carrera_nombre']
            carrera_id = self.carreras_mapa.get(carrera_nombre)
            
            if not carrera_id:
                messagebox.showerror("Error", "Carrera no válida.")
                return

            ruta_base = config.RUTA_BASE_TESIS
            autores_nuevos = datos_formulario.get('autores', [])
            abreviatura = self._extraer_abreviatura_carrera(carrera_nombre)
            apellido_principal = self._obtener_apellido_principal(autores_nuevos)
            ruta_destino_pdf = self._generar_ruta_destino_tesis(
                ruta_base,
                abreviatura,
                apellido_principal,
                anio
            )

            os.makedirs(os.path.dirname(ruta_destino_pdf), exist_ok=True)

            print(f"Copiando PDF de {datos_formulario['ruta_pdf_origen_local']} a {ruta_destino_pdf}")
            shutil.copyfile(datos_formulario['ruta_pdf_origen_local'], ruta_destino_pdf)
            print("Copia de archivo exitosa.")

            tesis_data = {
                'titulo': datos_formulario['titulo'],
                'resumen': datos_formulario['resumen'],
                'anio': anio,
                'palabras_clave': datos_formulario['palabras_clave'],
                'ruta_pdf': ruta_destino_pdf,
                'usuario_id': 1,
                'materia_id': carrera_id
            }
            
            autores_existentes = []

            exito = self.db_manager.insertar_nueva_tesis(tesis_data, autores_existentes, autores_nuevos)
            
            if exito:
                messagebox.showinfo("Éxito", "Nuevo TEG guardado correctamente.")
                self.mostrar_consulta() 
            else:
                os.remove(ruta_destino_pdf)
                messagebox.showerror("Error de Base de Datos", "No se pudo guardar el TEG. El archivo PDF no se almacenó.")

        except ValueError:
            messagebox.showerror("Error de Formato", "El año debe ser un número válido.")
        except IOError as e:
            messagebox.showerror("Error de Archivo", f"No se pudo copiar el archivo PDF al servidor: {e}")
        except Exception as e:
            detalle = traceback.format_exc()
            print(detalle)
            messagebox.showerror("Error Inesperado", f"Ocurrió un error: {e}\n\n{detalle}")

    def exportar_paquete_tesis(self, ruta_zip: str) -> bool:
        try:
            sync_manager.export_tegs_package(ruta_zip)
            return True
        except Exception as ex:
            messagebox.showerror("Error de Exportación", f"No se pudo exportar: {ex}")
            return False

    def importar_paquete_tesis(self, ruta_zip: str, sobrescribir: bool = False) -> Optional[Dict[str, int]]:
        try:
            return sync_manager.import_tegs_package(ruta_zip, sobrescribir=sobrescribir)
        except Exception as ex:
            messagebox.showerror("Error de Importación", f"No se pudo importar: {ex}")
            return None

    def exportar_paquete_nav(self):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        ruta = filedialog.asksaveasfilename(
            title="Exportar paquete de TEG",
            defaultextension=".zip",
            initialfile=f"tegs_{timestamp}.zip",
            filetypes=[("Archivo ZIP", "*.zip")]
        )
        if not ruta:
            return
        if self.exportar_paquete_tesis(ruta):
            messagebox.showinfo("Exportación completada", "Se generó el paquete con las tesis seleccionadas.")

    def importar_paquete_nav(self):
        ruta = filedialog.askopenfilename(
            title="Importar paquete de TEG",
            filetypes=[("Archivos ZIP", "*.zip")]
        )
        if not ruta:
            return
        sobrescribir = messagebox.askyesno("Sobrescribir registros", "¿Deseas reemplazar los TEG existentes cuando el GUID coincida?")
        resultado = self.importar_paquete_tesis(ruta, sobrescribir=sobrescribir)
        if resultado:
            mensaje = (
                f"Importación finalizada:\n"
                f"  - TEG importados: {resultado.get('tegs_importados', 0)}\n"
                f"  - TEG actualizados: {resultado.get('tegs_actualizados', 0)}\n"
                f"  - Autores creados: {resultado.get('autores_creados', 0)}"
            )
            messagebox.showinfo("Importación completada", mensaje)

    def _extraer_abreviatura_carrera(self, carrera_nombre: str) -> str:
        if not carrera_nombre:
            return "SINCAR"
        coincidencia = re.search(r"\(([^)]+)\)", carrera_nombre)
        if coincidencia:
            return self._normalizar_segmento(coincidencia.group(1))
        primeras_letras = ''.join(palabra[0] for palabra in carrera_nombre.split() if palabra)
        return self._normalizar_segmento(primeras_letras)

    def _obtener_apellido_principal(self, autores):
        if not autores:
            return "SINAPELLIDO"
        apellido = autores[0][1].split()[0] if autores[0][1] else "SINAPELLIDO"
        return self._normalizar_segmento(apellido)

    def _normalizar_segmento(self, valor: str) -> str:
        if not valor:
            return "SININFO"
        valor = unicodedata.normalize("NFKD", valor).encode("ascii", "ignore").decode("ascii")
        valor = valor.replace(" ", "_")
        valor = re.sub(r"[^A-Za-z0-9_]+", "", valor)
        return valor.upper() or "SININFO"

    def _generar_ruta_destino_tesis(self, ruta_base: str, abreviatura: str, apellido: str, anio: int) -> str:
        os.makedirs(ruta_base, exist_ok=True)
        nombre_base = f"{abreviatura}_{apellido}_{anio}"
        contador = 0
        while True:
            sufijo = f"_{contador}" if contador else ""
            nombre_archivo = f"{nombre_base}{sufijo}.pdf"
            ruta = os.path.join(ruta_base, nombre_archivo)
            if not os.path.exists(ruta):
                return ruta
            contador += 1