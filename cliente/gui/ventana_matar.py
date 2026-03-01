import threading

import customtkinter as ctk

from cliente import acciones
from cliente.constantes import (
    COLOR_BORDE,
    COLOR_ERROR,
    COLOR_ERROR_HOVER,
    COLOR_INPUT,
    COLOR_MUTED,
    COLOR_PRIMARIO,
    COLOR_TEXTO,
    FONDO_CARD,
)
from cliente.logger import registrar_log

class VentanaMatar(ctk.CTkFrame):
    def __init__(self, parent, cliente, on_close, mostrar_mensaje=None):
        super().__init__(parent, fg_color="transparent")
        self.cliente = cliente
        self.on_close = on_close
        self.mostrar_mensaje = mostrar_mensaje
        self.procesando = False

        self.crear_widgets()

    def crear_widgets(self):
        card = ctk.CTkFrame(
            self,
            fg_color=FONDO_CARD,
            corner_radius=14,
            border_width=1,
            border_color=COLOR_BORDE,
        )
        card.pack(expand=True, fill="both")

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=18, pady=(16, 0))

        ctk.CTkLabel(
            top,
            text="Finalizar proceso",
            font=ctk.CTkFont(size=20, weight="bold"),
            text_color=COLOR_TEXTO,
        ).pack(side="left")

        ctk.CTkButton(
            top,
            text="Cerrar",
            width=82,
            height=30,
            fg_color="#2A3040",
            hover_color="#3A4357",
            text_color=COLOR_TEXTO,
            command=self.cerrar_seguro,
        ).pack(side="right")

        ctk.CTkLabel(
            card,
            text="Ingresa el PID exacto del proceso que deseas detener.",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_MUTED,
        ).pack(anchor="w", padx=18, pady=(2, 12))

        self.pid_entry = ctk.CTkEntry(
            card,
            placeholder_text="PID (solo numeros)",
            height=42,
            fg_color=COLOR_INPUT,
            text_color=COLOR_TEXTO,
            border_width=1,
            border_color=COLOR_BORDE,
        )
        self.pid_entry.pack(fill="x", padx=18)
        self._aplicar_estilo_input(self.pid_entry)

        self.btn_matar = ctk.CTkButton(
            card,
            text="Terminar",
            fg_color=COLOR_ERROR,
            hover_color=COLOR_ERROR_HOVER,
            text_color="#F8FAFC",
            font=ctk.CTkFont(size=13, weight="bold"),
            height=42,
            command=self.matar,
        )
        self.btn_matar.pack(fill="x", padx=18, pady=(16, 8))

        self.lbl_estado = ctk.CTkLabel(
            card,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_MUTED,
        )
        self.lbl_estado.pack(pady=(0, 10))

    def focus_principal(self):
        self.pid_entry.focus_set()

    def _aplicar_estilo_input(self, entry):
        entry.bind(
            "<FocusIn>",
            lambda _e, en=entry: en.configure(border_width=2, border_color=COLOR_PRIMARIO),
        )
        entry.bind(
            "<FocusOut>",
            lambda _e, en=entry: en.configure(border_width=1, border_color=COLOR_BORDE),
        )

    def _safe_after(self, callback):
        try:
            self.after(0, callback)
        except Exception:
            pass

    def _mostrar_mensaje(self, titulo, mensaje, tipo):
        if callable(self.mostrar_mensaje):
            self.mostrar_mensaje(titulo, mensaje, tipo=tipo)
        else:
            self.lbl_estado.configure(text=mensaje)

    def cerrar_seguro(self):
        self.procesando = False
        if callable(self.on_close):
            self.on_close()

    def matar(self):
        if self.procesando:
            return

        pid_texto = self.pid_entry.get().strip()
        if not pid_texto.isdigit():
            self._mostrar_mensaje("Error", "Ingresa solo numeros enteros para el PID.", "error")
            registrar_log(f"Intento de matar proceso con PID invalido: '{pid_texto}'")
            return

        self.procesando = True
        self.btn_matar.configure(state="disabled")
        self.pid_entry.configure(state="disabled")
        self.lbl_estado.configure(text="Solicitando finalizacion...")

        pid = int(pid_texto)

        def tarea():
            try:
                data = acciones.terminar_proceso(self.cliente, str(pid))
                if data.get("estado") == "ok":
                    mensaje = data.get("mensaje", f"Proceso {pid} terminado")
                    self._safe_after(lambda m=mensaje: self._mostrar_mensaje("Exito", m, "exito"))
                    registrar_log(f"Proceso terminado: PID {pid}")
                else:
                    error_msg = data.get("mensaje", "Error desconocido")
                    self._safe_after(lambda e=error_msg: self._mostrar_mensaje("Error", f"No se pudo terminar el proceso:\n{e}", "error"))
                    registrar_log(f"Error al terminar proceso PID {pid}: {error_msg}")
            except Exception as e:
                self._safe_after(lambda e=e: self._mostrar_mensaje("Error", f"Excepcion: {e}", "error"))
                registrar_log(f"Excepcion al terminar proceso PID {pid}: {e}")
            finally:
                if not callable(self.mostrar_mensaje):
                    self._safe_after(self.cerrar_seguro)

        threading.Thread(target=tarea, daemon=True).start()
