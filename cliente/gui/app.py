import customtkinter as ctk
import threading
from cliente.constantes import COLOR_PRIMARIO, COLOR_HOVER, FONDO_DERECHA
from cliente.utils import centrar_ventana
from cliente.cliente_red import ClienteSeguro
from cliente import acciones  # Importación absoluta
from .ventana_login import VentanaLogin
from .ventana_iniciar import VentanaIniciar
from .ventana_matar import VentanaMatar
from .panel_texto import PanelTexto
from .panel_procesos import PanelProcesos
from .panel_recursos import PanelRecursos

class App(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("Sistema de Monitoreo Distribuido")
        centrar_ventana(self, 1000, 600)

        self.cliente = ClienteSeguro()

        # Control de monitoreo en tiempo real (se maneja desde el panel de procesos)
        self.panel_actual = None

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.crear_menu()
        self.crear_panel_datos()

        # Instancias de ventanas (para reutilizarlas si es necesario)
        self.ventana_login = None
        self.ventana_iniciar = None
        self.ventana_matar = None

    # ======================
    # MENU LATERAL
    # ======================
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
        """Activa los botones después del login."""
        self.btn_procesos.configure(state="normal")
        self.btn_recursos.configure(state="normal")
        self.btn_iniciar.configure(state="normal")
        self.btn_matar.configure(state="normal")

    # ======================
    # PANEL DERECHO (contenedor dinámico)
    # ======================
    def crear_panel_datos(self):
        self.panel = ctk.CTkFrame(self, fg_color=FONDO_DERECHA)
        self.panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Frame interior que contendrá los paneles
        self.panel_contenido = ctk.CTkFrame(self.panel, fg_color="transparent")
        self.panel_contenido.pack(expand=True, fill="both", padx=15, pady=15)

        # Mostrar panel de texto por defecto
        self.mostrar_panel_texto()

    def mostrar_panel_texto(self):
        """Cambia al panel de texto."""
        if self.panel_actual:
            self.panel_actual.detener()  # Si el panel actual tiene método detener, lo llama
            self.panel_actual.destroy()

        self.panel_actual = PanelTexto(self.panel_contenido)
        self.panel_actual.pack(expand=True, fill="both")
        self.panel_actual.escribir("Sistema iniciado.")

    def mostrar_panel_procesos(self):
        """Cambia al panel de procesos en tiempo real."""
        if self.panel_actual:
            self.panel_actual.detener()
            self.panel_actual.destroy()

        self.panel_actual = PanelProcesos(self.panel_contenido, self.cliente)
        self.panel_actual.pack(expand=True, fill="both")
        self.panel_actual.iniciar_monitoreo()

    def mostrar_panel_recursos(self):
        """Cambia al panel de recursos con gráficos."""
        if self.panel_actual:
            self.panel_actual.detener()
            self.panel_actual.destroy()
        
        self.panel_actual = PanelRecursos(self.panel_contenido, self.cliente)
        self.panel_actual.pack(expand=True, fill="both")
        self.panel_actual.iniciar_monitoreo()

    # ======================
    # ACCIONES DE LOS BOTONES
    # ======================
    def mostrar_procesos(self):
        self.mostrar_panel_procesos()

    def mostrar_recursos(self):
        self.mostrar_panel_recursos()

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