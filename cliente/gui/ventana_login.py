import customtkinter as ctk
import threading
from cliente.utils import centrar_ventana
from cliente.constantes import COLOR_PRIMARIO, COLOR_HOVER
from cliente.logger import registrar_log
from .mensaje_personalizado import MensajePersonalizado

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
            # Capturamos los valores al inicio del hilo
            ip = self.ip_entry.get()
            usuario = self.user_entry.get()
            password = self.pass_entry.get()

            try:
                respuesta = self.cliente.conectar(ip, usuario, password)

                if respuesta["status"] == "ok":
                    registrar_log(f"Login exitoso: usuario '{usuario}' desde IP {ip}")
                    # Capturamos usuario en el lambda
                    self.after(0, lambda u=usuario: MensajePersonalizado(
                        self.parent, "Éxito", f"Bienvenido {u}", tipo="exito"
                    ))
                    self.after(0, self.login_ok)
                else:
                    registrar_log(f"Login fallido: usuario '{usuario}' desde IP {ip}")
                    self.after(0, lambda: MensajePersonalizado(
                        self.parent, "Error", "Credenciales incorrectas", tipo="error"
                    ))
                    self.after(500, self.destroy)

            except Exception as e:
                error_msg = str(e)
                registrar_log(f"Error de conexión desde IP {ip}: {error_msg}")
                # Capturamos ip y error_msg
                self.after(0, lambda i=ip, msg=error_msg: MensajePersonalizado(
                    self.parent, "Error de conexión",
                    f"No se pudo conectar a {i}:\n{msg}", tipo="error"
                ))
                self.after(500, self.destroy)

        threading.Thread(target=tarea, daemon=True).start()

    def login_ok(self):
        self.callback_activar_botones()
        self.destroy()