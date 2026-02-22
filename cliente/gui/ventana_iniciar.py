import customtkinter as ctk
import threading
from cliente.utils import centrar_ventana
from cliente.constantes import COLOR_PRIMARIO, COLOR_HOVER
from cliente import acciones
from .mensaje_personalizado import MensajePersonalizado

class VentanaIniciar(ctk.CTkToplevel):
    def __init__(self, parent, cliente):
        super().__init__(parent)
        self.parent = parent
        self.cliente = cliente
        self.procesando = False

        self.title("Iniciar proceso")
        centrar_ventana(self, 350, 200)

        self.transient(parent)
        self.grab_set()
        self.focus()

        self.crear_widgets()
        self.protocol("WM_DELETE_WINDOW", self.cerrar_seguro)

    def crear_widgets(self):
        self.label = ctk.CTkLabel(self, text="Comando")
        self.label.pack(pady=10)

        self.cmd_entry = ctk.CTkEntry(self, width=250)
        self.cmd_entry.pack()
        self.cmd_entry.focus()

        self.btn_iniciar = ctk.CTkButton(
            self,
            text="Iniciar",
            fg_color=COLOR_PRIMARIO,
            hover_color=COLOR_HOVER,
            command=self.iniciar
        )
        self.btn_iniciar.pack(pady=20)

    def cerrar_seguro(self):
        """Evita errores si se cierra mientras se procesa."""
        self.procesando = False
        self.destroy()

    def iniciar(self):
        if self.procesando:
            return
        self.procesando = True
        self.btn_iniciar.configure(state="disabled")

        comando = self.cmd_entry.get()

        def tarea():
            try:
                data = acciones.iniciar_proceso(self.cliente, comando)
                if data.get("estado") == "ok":
                    mensaje = f"Proceso iniciado correctamente.\nPID: {data.get('pid')}"
                    self.after(0, lambda m=mensaje: MensajePersonalizado(self.parent, "Éxito", m, tipo="exito"))
                else:
                    error_msg = data.get("mensaje", "Error desconocido")
                    self.after(0, lambda e=error_msg: MensajePersonalizado(self.parent, "Error", f"No se pudo iniciar el proceso:\n{e}", tipo="error"))
            except Exception as e:
                self.after(0, lambda e=e: MensajePersonalizado(self.parent, "Error", f"Excepción: {e}", tipo="error"))
            finally:
                self.after(500, self.cerrar_seguro)  # Pequeño retraso para evitar conflictos

        threading.Thread(target=tarea, daemon=True).start()