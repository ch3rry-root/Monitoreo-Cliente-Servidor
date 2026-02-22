import customtkinter as ctk
import threading
from cliente.utils import centrar_ventana
from cliente.constantes import COLOR_PRIMARIO, COLOR_HOVER

class VentanaLogin(ctk.CTkToplevel):
    def __init__(self, parent, cliente, callback_activar_botones):
        super().__init__(parent)
        self.parent = parent
        self.cliente = cliente
        self.callback_activar_botones = callback_activar_botones

        self.title("Login seguro")
        centrar_ventana(self, 350, 300)

        self.transient(parent)
        self.grab_set()
        self.lift()
        self.focus_force()

        self.crear_widgets()

    def crear_widgets(self):
        ctk.CTkLabel(self, text="IP Servidor").pack(pady=5)
        self.ip_entry = ctk.CTkEntry(self)
        self.ip_entry.pack()

        ctk.CTkLabel(self, text="Usuario").pack(pady=5)
        self.user_entry = ctk.CTkEntry(self)
        self.user_entry.pack()

        ctk.CTkLabel(self, text="Password").pack(pady=5)
        self.pass_entry = ctk.CTkEntry(self, show="*")
        self.pass_entry.pack()

        ctk.CTkButton(
            self,
            text="Conectar",
            fg_color=COLOR_PRIMARIO,
            hover_color=COLOR_HOVER,
            command=self.conectar
        ).pack(pady=20)

    def conectar(self):
        def tarea():
            try:
                respuesta = self.cliente.conectar(
                    self.ip_entry.get(),
                    self.user_entry.get(),
                    self.pass_entry.get()
                )
                if respuesta["status"] == "ok":
                    self.after(0, self.login_ok)
                else:
                    self.after(0, lambda: self.parent.panel_actual.escribir("[X] Login fallido"))
            except Exception as e:
                error_msg = str(e)
                self.after(0, lambda msg=error_msg: self.parent.panel_actual.escribir(f"[ERROR] {msg}"))

        threading.Thread(target=tarea, daemon=True).start()

    def login_ok(self):
        self.parent.panel_actual.escribir("[✓] Autenticado correctamente")
        self.callback_activar_botones()
        self.destroy()