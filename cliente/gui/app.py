import customtkinter as ctk
import threading
from cliente.constantes import COLOR_PRIMARIO, COLOR_HOVER, FONDO_DERECHA
from cliente.utils import centrar_ventana
from cliente.cliente_red import ClienteSeguro
from cliente import acciones
from .ventana_login import VentanaLogin
from .ventana_iniciar import VentanaIniciar
from .ventana_matar import VentanaMatar
from .panel_texto import PanelTexto
from .panel_procesos import PanelProcesos
from .panel_recursos import PanelRecursos
from .panel_logs import PanelLogs

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Monitoreo Distribuido")
        centrar_ventana(self, 1000, 600)

        self.cliente = ClienteSeguro()

        self.panel_actual = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.crear_menu()
        self.crear_panel_datos()

        self.ventana_login = None
        self.ventana_iniciar = None
        self.ventana_matar = None

    def crear_menu(self):
        self.menu = ctk.CTkFrame(self, width=220)
        self.menu.grid(row=0, column=0, sticky="ns")

        titulo = ctk.CTkLabel(
            self.menu,
            text="Sistema\nDistribuido",
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color="#CBA6FF"
        )
        titulo.pack(pady=20)

        self.btn_login = self.crear_boton("Login", self.abrir_ventana_login)
        self.btn_procesos = self.crear_boton("Procesos", self.mostrar_procesos, False)
        self.btn_recursos = self.crear_boton("Recursos", self.mostrar_recursos, False)
        self.btn_iniciar = self.crear_boton("Iniciar Proceso", self.abrir_ventana_iniciar, False)
        self.btn_matar = self.crear_boton("Matar Proceso", self.abrir_ventana_matar, False)
        self.btn_logs = self.crear_boton("Ver Logs", self.mostrar_logs, False)

    def crear_boton(self, texto, comando, activo=True):
        boton = ctk.CTkButton(
            self.menu,
            text=texto,
            fg_color=COLOR_PRIMARIO,
            hover_color=COLOR_HOVER,
            corner_radius=12,
            height=40,
            command=comando
        )
        boton.pack(padx=20, pady=10, fill="x")
        if not activo:
            boton.configure(state="disabled")
        return boton

    def activar_botones(self):
        """Activa los botones de acciones y cambia login por cerrar sesión."""
        self.btn_procesos.configure(state="normal")
        self.btn_recursos.configure(state="normal")
        self.btn_iniciar.configure(state="normal")
        self.btn_matar.configure(state="normal")
        self.btn_logs.configure(state="normal")
        
        # Cambiar botón de login a cerrar sesión
        self.btn_login.configure(
            text="Cerrar sesión",
            fg_color="#FF4444",  # Rojo
            hover_color="#FF6666",
            command=self.cerrar_sesion
        )

    def cerrar_sesion(self):
        """Cierra la conexión y vuelve al estado inicial."""
        # Detener monitoreo del panel actual
        if self.panel_actual:
            self.panel_actual.detener()
            self.panel_actual.destroy()
            self.panel_actual = None
        
        # Cerrar conexión del cliente
        self.cliente.desconectar()
        
        # Restaurar panel de texto
        self.mostrar_panel_texto()
        self.panel_actual.escribir("Sesión cerrada.")
        
        # Restaurar botón de login
        self.btn_login.configure(
            text="Login",
            fg_color=COLOR_PRIMARIO,
            hover_color=COLOR_HOVER,
            command=self.abrir_ventana_login
        )
        
        # Deshabilitar botones de acciones
        self.btn_procesos.configure(state="disabled")
        self.btn_recursos.configure(state="disabled")
        self.btn_iniciar.configure(state="disabled")
        self.btn_matar.configure(state="disabled")
        self.btn_logs.configure(state="disabled")
        
        # Resetear instancias de ventanas
        self.ventana_login = None
        self.ventana_iniciar = None
        self.ventana_matar = None

    def crear_panel_datos(self):
        self.panel = ctk.CTkFrame(self, fg_color=FONDO_DERECHA)
        self.panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        self.panel_contenido = ctk.CTkFrame(self.panel, fg_color="transparent")
        self.panel_contenido.pack(expand=True, fill="both", padx=15, pady=15)

        self.mostrar_panel_texto()

    def mostrar_panel_texto(self):
        if self.panel_actual:
            self.panel_actual.detener()
            self.panel_actual.destroy()

        self.panel_actual = PanelTexto(self.panel_contenido)
        self.panel_actual.pack(expand=True, fill="both")
        self.panel_actual.escribir("Sistema iniciado.")

    def mostrar_panel_procesos(self):
        if self.panel_actual:
            self.panel_actual.detener()
            self.panel_actual.destroy()

        self.panel_actual = PanelProcesos(self.panel_contenido, self.cliente)
        self.panel_actual.pack(expand=True, fill="both")
        self.panel_actual.iniciar_monitoreo()

    def mostrar_panel_recursos(self):
        if self.panel_actual:
            self.panel_actual.detener()
            self.panel_actual.destroy()

        self.panel_actual = PanelRecursos(self.panel_contenido, self.cliente, self.mostrar_alerta)
        self.panel_actual.pack(expand=True, fill="both")
        self.panel_actual.iniciar_monitoreo()

    def mostrar_panel_logs(self):
        if self.panel_actual:
            self.panel_actual.detener()
            self.panel_actual.destroy()

        self.panel_actual = PanelLogs(self.panel_contenido)
        self.panel_actual.pack(expand=True, fill="both")

    def mostrar_alerta(self, mensaje):
        if isinstance(self.panel_actual, PanelTexto):
            self.panel_actual.escribir(f"⚠️ {mensaje}")
        else:
            print(f"ALERTA: {mensaje}")

    def mostrar_procesos(self):
        self.mostrar_panel_procesos()

    def mostrar_recursos(self):
        self.mostrar_panel_recursos()

    def mostrar_logs(self):
        self.mostrar_panel_logs()

    def abrir_ventana_login(self):
        if self.ventana_login is None or not self.ventana_login.winfo_exists():
            self.ventana_login = VentanaLogin(self, self.cliente, self.activar_botones)
        else:
            self.ventana_login.focus()

    def abrir_ventana_iniciar(self):
        if self.ventana_iniciar is None or not self.ventana_iniciar.winfo_exists():
            self.ventana_iniciar = VentanaIniciar(self, self.cliente)
        else:
            self.ventana_iniciar.focus()

    def abrir_ventana_matar(self):
        if self.ventana_matar is None or not self.ventana_matar.winfo_exists():
            self.ventana_matar = VentanaMatar(self, self.cliente)
        else:
            self.ventana_matar.focus()