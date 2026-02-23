import customtkinter as ctk
import threading
import os
from tkinter import filedialog
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
        centrar_ventana(self, 400, 380)
        self.transient(parent)
        self.grab_set()
        self.lift()
        self.focus_force()
        
        self.crear_widgets()
        self.validar_campos()  # Inicialmente deshabilitado

    def crear_widgets(self):
        # IP
        ctk.CTkLabel(self, text="IP Servidor").pack(pady=5)
        self.ip_entry = ctk.CTkEntry(self)
        self.ip_entry.pack()
        self.ip_entry.bind("<KeyRelease>", self.validar_campos)

        # Usuario
        ctk.CTkLabel(self, text="Usuario").pack(pady=5)
        self.user_entry = ctk.CTkEntry(self)
        self.user_entry.pack()
        self.user_entry.bind("<KeyRelease>", self.validar_campos)

        # Password
        ctk.CTkLabel(self, text="Password").pack(pady=5)
        self.pass_entry = ctk.CTkEntry(self, show="*")
        self.pass_entry.pack()
        self.pass_entry.bind("<KeyRelease>", self.validar_campos)

        # Certificado (obligatorio)
        ctk.CTkLabel(self, text="Certificado del servidor").pack(pady=5)
        frame_cert = ctk.CTkFrame(self, fg_color="transparent")
        frame_cert.pack(pady=5)

        self.cert_entry = ctk.CTkEntry(frame_cert, width=200)
        self.cert_entry.pack(side="left", padx=(0,5))
        self.cert_entry.bind("<KeyRelease>", self.validar_campos)

        self.btn_examinar = ctk.CTkButton(
            frame_cert,
            text="Examinar...",
            fg_color="#555555",
            hover_color="#777777",
            command=self.seleccionar_certificado,
            width=80
        )
        self.btn_examinar.pack(side="left")

        # Botón conectar
        self.btn_conectar = ctk.CTkButton(
            self,
            text="Conectar",
            fg_color=COLOR_PRIMARIO,
            hover_color=COLOR_HOVER,
            command=self.conectar,
            state="disabled"
        )
        self.btn_conectar.pack(pady=20)

        # Etiqueta informativa
        self.lbl_info = ctk.CTkLabel(
            self,
            text="",
            font=ctk.CTkFont(size=10),
            text_color="orange"
        )
        self.lbl_info.pack()

    def seleccionar_certificado(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar certificado del servidor",
            filetypes=[("Archivos de certificado", "*.crt *.pem"), ("Todos", "*.*")]
        )
        if archivo:
            self.cert_entry.delete(0, "end")
            self.cert_entry.insert(0, archivo)
            self.validar_campos()

    def validar_campos(self, event=None):
        ip = self.ip_entry.get().strip()
        usuario = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()
        cert_path = self.cert_entry.get().strip()

        cert_existe = os.path.isfile(cert_path) if cert_path else False

        if ip and usuario and password and cert_existe:
            self.btn_conectar.configure(state="normal")
            self.lbl_info.configure(text="", text_color="orange")
        else:
            self.btn_conectar.configure(state="disabled")
            if not cert_existe and cert_path:
                self.lbl_info.configure(text="El archivo de certificado no existe", text_color="red")
            elif not cert_path:
                self.lbl_info.configure(text="Debe seleccionar un certificado", text_color="orange")
            else:
                self.lbl_info.configure(text="Complete todos los campos", text_color="orange")

    def conectar(self):
        self.btn_conectar.configure(state="disabled")

        def tarea():
            ip = self.ip_entry.get().strip()
            usuario = self.user_entry.get().strip()
            password = self.pass_entry.get()
            cert_path = self.cert_entry.get().strip()

            try:
                respuesta = self.cliente.conectar(ip, usuario, password, cert_path)

                if respuesta["status"] == "ok":
                    registrar_log(f"Login exitoso: usuario '{usuario}' desde IP {ip}")
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
                self.after(0, lambda i=ip, msg=error_msg: MensajePersonalizado(
                    self.parent, "Error de conexión",
                    f"No se pudo conectar a {i}:\n{msg}", tipo="error"
                ))
                self.after(500, self.destroy)

        threading.Thread(target=tarea, daemon=True).start()

    def login_ok(self):
        self.callback_activar_botones()
        self.destroy()