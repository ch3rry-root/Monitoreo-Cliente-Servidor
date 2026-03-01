import os
import threading
from tkinter import filedialog

import customtkinter as ctk

from cliente.cliente_red import ClienteSeguro
from cliente.constantes import (
    COLOR_BORDE,
    COLOR_ERROR,
    COLOR_ERROR_HOVER,
    COLOR_HOVER,
    COLOR_INPUT,
    COLOR_MUTED,
    COLOR_PRIMARIO,
    COLOR_SUCCESS,
    COLOR_TEXTO,
    COLOR_WARNING,
    FONDO_CARD,
)
from cliente.logger import registrar_log

class VentanaLogin(ctk.CTkFrame):
    def __init__(self, parent, callback_nueva_pestana, on_close, mostrar_mensaje=None):
        super().__init__(parent, fg_color="transparent")
        self.callback_nueva_pestana = callback_nueva_pestana
        self.on_close = on_close
        self.mostrar_mensaje = mostrar_mensaje
        self.procesando = False

        self.crear_widgets()
        self.validar_campos()

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
        top.pack(fill="x", padx=18, pady=(14, 4))

        ctk.CTkLabel(
            top,
            text="Nueva conexion segura",
            font=ctk.CTkFont(size=21, weight="bold"),
            text_color=COLOR_TEXTO,
        ).pack(side="left")

        ctk.CTkButton(
            top,
            text="X",
            width=32,
            height=32,
            corner_radius=16,
            fg_color=COLOR_ERROR,
            hover_color=COLOR_ERROR_HOVER,
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.cerrar_seguro,
        ).pack(side="right")

        ctk.CTkLabel(
            card,
            text="Conecta un servidor remoto usando credenciales y certificado.",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_MUTED,
        ).pack(anchor="w", padx=18, pady=(0, 10))

        bloque_ip = ctk.CTkFrame(card, fg_color="transparent")
        bloque_ip.pack(fill="x", padx=18)
        self.ip_entry = self._crear_campo(
            bloque_ip,
            etiqueta="Direccion IP",
            placeholder="Ejemplo: 192.168.1.100",
        )

        fila_cred = ctk.CTkFrame(card, fg_color="transparent")
        fila_cred.pack(fill="x", padx=18)
        fila_cred.grid_columnconfigure(0, weight=1)
        fila_cred.grid_columnconfigure(1, weight=1)

        bloque_user = ctk.CTkFrame(fila_cred, fg_color="transparent")
        bloque_user.grid(row=0, column=0, sticky="ew", padx=(0, 6))
        self.user_entry = self._crear_campo(
            bloque_user,
            etiqueta="Usuario",
            placeholder="admin",
        )

        bloque_pass = ctk.CTkFrame(fila_cred, fg_color="transparent")
        bloque_pass.grid(row=0, column=1, sticky="ew", padx=(6, 0))
        self.pass_entry = self._crear_campo(
            bloque_pass,
            etiqueta="Contraseña",
            placeholder="********",
            show="*",
        )

        ctk.CTkLabel(
            card,
            text="Certificado",
            anchor="w",
            text_color=COLOR_TEXTO,
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(fill="x", padx=18, pady=(8, 0))

        frame_cert = ctk.CTkFrame(card, fg_color="transparent")
        frame_cert.pack(fill="x", padx=18, pady=(4, 8))

        self.cert_entry = ctk.CTkEntry(
            frame_cert,
            placeholder_text="Selecciona archivo .crt o .pem",
            height=36,
            fg_color=COLOR_INPUT,
            text_color=COLOR_TEXTO,
            border_width=1,
            border_color=COLOR_BORDE,
        )
        self.cert_entry.pack(side="left", expand=True, fill="x", padx=(0, 8))
        self.cert_entry.bind("<KeyRelease>", self.validar_campos)
        self._aplicar_estilo_input(self.cert_entry)

        self.btn_examinar = ctk.CTkButton(
            frame_cert,
            text="Examinar",
            width=106,
            height=36,
            fg_color="#334155",
            hover_color="#475569",
            text_color=COLOR_TEXTO,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.seleccionar_certificado,
        )
        self.btn_examinar.pack(side="right")

        pie = ctk.CTkFrame(card, fg_color="transparent")
        pie.pack(fill="x", padx=18, pady=(6, 12))
        pie.grid_columnconfigure(0, weight=1)

        self.lbl_info = ctk.CTkLabel(
            pie,
            text="",
            font=ctk.CTkFont(size=12),
            text_color=COLOR_WARNING,
            anchor="w",
        )
        self.lbl_info.grid(row=0, column=0, sticky="w")

        self.btn_conectar = ctk.CTkButton(
            pie,
            text="Conectar",
            fg_color=COLOR_PRIMARIO,
            hover_color=COLOR_HOVER,
            text_color="#FFFFFF",
            command=self.conectar,
            state="disabled",
            width=160,
            height=40,
            font=ctk.CTkFont(size=14, weight="bold"),
        )
        self.btn_conectar.grid(row=0, column=1, sticky="e")

    def focus_principal(self):
        self.ip_entry.focus_set()

    def _crear_campo(self, parent, etiqueta, placeholder, show=None):
        ctk.CTkLabel(
            parent,
            text=etiqueta,
            anchor="w",
            text_color=COLOR_TEXTO,
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(fill="x")

        entry = ctk.CTkEntry(
            parent,
            placeholder_text=placeholder,
            height=36,
            show=show,
            fg_color=COLOR_INPUT,
            text_color=COLOR_TEXTO,
            border_width=1,
            border_color=COLOR_BORDE,
        )
        entry.pack(fill="x", pady=(4, 8))
        entry.bind("<KeyRelease>", self.validar_campos)
        self._aplicar_estilo_input(entry)

        return entry

    def _aplicar_estilo_input(self, entry):
        entry.bind(
            "<FocusIn>",
            lambda _e, en=entry: en.configure(border_width=2, border_color=COLOR_PRIMARIO),
            add="+",
        )
        entry.bind(
            "<FocusOut>",
            lambda _e, en=entry: en.configure(border_width=1, border_color=COLOR_BORDE),
            add="+",
        )

    def seleccionar_certificado(self):
        archivo = filedialog.askopenfilename(
            title="Seleccionar certificado del servidor",
            filetypes=[("Certificados", "*.crt *.pem"), ("Todos", "*.*")],
            parent=self.winfo_toplevel(),
        )
        if archivo:
            self.cert_entry.delete(0, "end")
            self.cert_entry.insert(0, archivo)
            self.validar_campos()

    def validar_campos(self, event=None):
        _ = event
        if not self.winfo_exists():
            return

        ip = self.ip_entry.get().strip()
        usuario = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()
        cert_path = self.cert_entry.get().strip()

        cert_existe = os.path.isfile(cert_path) if cert_path else False

        if ip and usuario and password and cert_existe and not self.procesando:
            self.btn_conectar.configure(state="normal")
            self.lbl_info.configure(text="Listo para conectar", text_color=COLOR_SUCCESS)
        else:
            self.btn_conectar.configure(state="disabled")
            if cert_path and not cert_existe:
                self.lbl_info.configure(text="El certificado no existe", text_color=COLOR_ERROR)
            elif not cert_path:
                self.lbl_info.configure(text="Selecciona un certificado", text_color=COLOR_WARNING)
            else:
                self.lbl_info.configure(text="Completa todos los campos", text_color=COLOR_WARNING)

    def _safe_after(self, callback):
        try:
            self.after(0, callback)
        except Exception:
            pass

    def conectar(self):
        if self.procesando:
            return

        self.procesando = True
        self.btn_conectar.configure(state="disabled")
        self.ip_entry.configure(state="disabled")
        self.user_entry.configure(state="disabled")
        self.pass_entry.configure(state="disabled")
        self.cert_entry.configure(state="disabled")
        self.btn_examinar.configure(state="disabled")
        self.lbl_info.configure(text="Conectando...", text_color=COLOR_WARNING)

        ip = self.ip_entry.get().strip()
        usuario = self.user_entry.get().strip()
        password = self.pass_entry.get()
        cert_path = self.cert_entry.get().strip()

        def tarea():
            cliente = ClienteSeguro()
            try:
                respuesta = cliente.conectar(ip, usuario, password, cert_path)
                if respuesta["status"] == "ok":
                    registrar_log(f"Login exitoso: usuario '{usuario}' desde IP {ip}")
                    self._safe_after(lambda: self.callback_nueva_pestana(cliente, ip, usuario, cert_path))
                    self._safe_after(self.cerrar_seguro)
                else:
                    registrar_log(f"Login fallido: usuario '{usuario}' desde IP {ip}")
                    self._safe_after(lambda: self.mostrar_error("Credenciales incorrectas"))
            except Exception as e:
                error_msg = str(e)
                registrar_log(f"Error de conexion desde IP {ip}: {error_msg}")
                self._safe_after(lambda msg=error_msg: self.mostrar_error(f"No se pudo conectar:\n{msg}"))

        threading.Thread(target=tarea, daemon=True).start()

    def mostrar_error(self, mensaje):
        if callable(self.mostrar_mensaje):
            self.mostrar_mensaje("Error", mensaje, tipo="error")
        else:
            self.lbl_info.configure(text=mensaje, text_color=COLOR_ERROR)
        self.procesando = False

    def cerrar_seguro(self):
        self.procesando = False
        if callable(self.on_close):
            self.on_close()
