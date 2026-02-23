# cliente/gui/ventana_matar.py
import customtkinter as ctk
import threading
from cliente.utils import centrar_ventana
from cliente.constantes import COLOR_BOTONES, COLOR_HOVER
from cliente import acciones
from .mensaje_personalizado import MensajePersonalizado
from cliente.logger import registrar_log

class VentanaMatar(ctk.CTkToplevel):
    def __init__(self, parent, cliente, icon_manager):
        super().__init__(parent)
        self.parent = parent
        self.cliente = cliente
        self.icon_manager = icon_manager
        self.procesando = False
        self.title("Matar proceso")
        centrar_ventana(self, 350, 200)
        self.transient(parent)
        self.grab_set()
        self.focus()
        
        # Establecer icono de ventana
        if self.icon_manager:
            self.icon_manager.set_window_icon(self, "kill")
        
        self.crear_widgets()
        self.protocol("WM_DELETE_WINDOW", self.cerrar_seguro)

    def crear_widgets(self):
        self.label = ctk.CTkLabel(self, text="PID")
        self.label.pack(pady=10)
        self.pid_entry = ctk.CTkEntry(self)
        self.pid_entry.pack()
        self.pid_entry.focus()
        self.btn_matar = ctk.CTkButton(
            self,
            text="Terminar",
            fg_color=COLOR_BOTONES,
            hover_color=COLOR_HOVER,
            command=self.matar
        )
        self.btn_matar.pack(pady=20)

    def cerrar_seguro(self):
        self.procesando = False
        self.destroy()

    def matar(self):
        if self.procesando:
            return
        pid_texto = self.pid_entry.get().strip()
        if not pid_texto.isdigit():
            MensajePersonalizado(
                self.parent,
                "Error",
                "Ingrese solo números enteros para el PID",
                tipo="error",
                icon_manager=self.icon_manager
            )
            registrar_log(f"Intento de matar proceso con PID inválido: '{pid_texto}'")
            return

        self.procesando = True
        self.btn_matar.configure(state="disabled")
        pid = int(pid_texto)

        def tarea():
            try:
                data = acciones.terminar_proceso(self.cliente, str(pid))
                if data.get("estado") == "ok":
                    mensaje = data.get("mensaje", f"Proceso {pid} terminado")
                    self.after(0, lambda m=mensaje: MensajePersonalizado(
                        self.parent, "Éxito", m, tipo="exito", icon_manager=self.icon_manager
                    ))
                    registrar_log(f"Proceso terminado: PID {pid}")
                else:
                    error_msg = data.get("mensaje", "Error desconocido")
                    self.after(0, lambda e=error_msg: MensajePersonalizado(
                        self.parent, "Error", f"No se pudo terminar el proceso:\n{e}",
                        tipo="error", icon_manager=self.icon_manager
                    ))
                    registrar_log(f"Error al terminar proceso PID {pid}: {error_msg}")
            except Exception as e:
                self.after(0, lambda e=e: MensajePersonalizado(
                    self.parent, "Error", f"Excepción: {e}", tipo="error",
                    icon_manager=self.icon_manager
                ))
                registrar_log(f"Excepción al terminar proceso PID {pid}: {e}")
            finally:
                self.after(500, self.cerrar_seguro)

        threading.Thread(target=tarea, daemon=True).start()