import customtkinter as ctk
from cliente.constantes import COLOR_PRIMARIO, COLOR_HOVER, FONDO_DERECHA, COLOR_TEXTO
from cliente.utils import centrar_ventana
from .ventana_login import VentanaLogin
from .ventana_iniciar import VentanaIniciar
from .ventana_matar import VentanaMatar
from .pestana_servidor import PestanaServidor

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Monitoreo")
        centrar_ventana(self, 1200, 700)  # Un poco más grande

        # Configurar tema
        ctk.set_appearance_mode("dark")
        self.configure(fg_color="#1a1a1a")

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.crear_menu()
        self.crear_panel_derecho()
        self.crear_barra_estado()

        self.pestanas = {}  # nombre -> objeto PestanaServidor
        self.ventana_login = None
        self.ventana_iniciar = None
        self.ventana_matar = None

    # ======================
    # MENU LATERAL
    # ======================
    def crear_menu(self):
        self.menu = ctk.CTkFrame(self, width=250, corner_radius=0)
        self.menu.grid(row=0, column=0, sticky="ns", rowspan=2)

        # Título con icono
        titulo = ctk.CTkLabel(
            self.menu,
            text="Panel",
            font=ctk.CTkFont(size=24, weight="bold"),
            text_color=COLOR_TEXTO
        )
        titulo.pack(pady=(30, 20))

        # Botones con iconos
        self.btn_nueva_conexion = self.crear_boton("➕ Nueva conexión", self.abrir_ventana_login)
        self.btn_procesos = self.crear_boton("📋 Procesos", self.mostrar_procesos, False)
        self.btn_recursos = self.crear_boton("📈 Recursos", self.mostrar_recursos, False)
        self.btn_iniciar = self.crear_boton("▶ Iniciar Proceso", self.abrir_ventana_iniciar, False)
        self.btn_matar = self.crear_boton("⛔ Matar Proceso", self.abrir_ventana_matar, False)
        self.btn_logs = self.crear_boton("📜 Ver Logs", self.mostrar_logs, False)
        self.btn_cerrar_pestana = self.crear_boton("❌ Cerrar pestaña", self.cerrar_pestana_activa, False)

    def crear_boton(self, texto, comando, activo=True):
        boton = ctk.CTkButton(
            self.menu,
            text=texto,
            fg_color="transparent",
            text_color="white",
            hover_color=COLOR_HOVER,
            anchor="w",
            height=40,
            corner_radius=0,
            command=comando
        )
        boton.pack(padx=10, pady=2, fill="x")
        if not activo:
            boton.configure(state="disabled", text_color="gray")
        return boton

    def activar_botones_servidor(self):
        """Habilita los botones que dependen de una pestaña activa."""
        self.btn_procesos.configure(state="normal", text_color="white")
        self.btn_recursos.configure(state="normal", text_color="white")
        self.btn_iniciar.configure(state="normal", text_color="white")
        self.btn_matar.configure(state="normal", text_color="white")
        self.btn_logs.configure(state="normal", text_color="white")
        self.btn_cerrar_pestana.configure(state="normal", text_color="white")

    def desactivar_botones_servidor(self):
        """Deshabilita los botones cuando no hay pestañas."""
        self.btn_procesos.configure(state="disabled", text_color="gray")
        self.btn_recursos.configure(state="disabled", text_color="gray")
        self.btn_iniciar.configure(state="disabled", text_color="gray")
        self.btn_matar.configure(state="disabled", text_color="gray")
        self.btn_logs.configure(state="disabled", text_color="gray")
        self.btn_cerrar_pestana.configure(state="disabled", text_color="gray")

    # ======================
    # PANEL DERECHO CON PESTAÑAS
    # ======================
    def crear_panel_derecho(self):
        self.panel = ctk.CTkFrame(self, fg_color=FONDO_DERECHA, corner_radius=10)
        self.panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=(10,5))

        # Tabview con estilo personalizado
        self.tabview = ctk.CTkTabview(
            self.panel,
            fg_color="transparent",
            segmented_button_selected_color=COLOR_PRIMARIO,
            segmented_button_selected_hover_color=COLOR_HOVER,
            corner_radius=8
        )
        self.tabview.pack(expand=True, fill="both")

    def nueva_pestana(self, cliente, ip, usuario, cert_path):
        """Crea una nueva pestaña con el servidor conectado."""
        base = f"{ip} - {usuario}"
        nombre = base
        contador = 1
        while nombre in self.pestanas:
            contador += 1
            nombre = f"{base} ({contador})"

        self.tabview.add(nombre)
        pestana_frame = self.tabview.tab(nombre)
        pestana = PestanaServidor(pestana_frame, cliente, ip, usuario, self.mostrar_alerta)
        pestana.pack(expand=True, fill="both")

        self.pestanas[nombre] = pestana
        self.activar_botones_servidor()
        self.actualizar_barra_estado()

    def pestana_activa(self):
        nombre = self.tabview.get()
        return self.pestanas.get(nombre)

    def cerrar_pestana_activa(self):
        nombre = self.tabview.get()
        if nombre and nombre in self.pestanas:
            pestana = self.pestanas.pop(nombre)
            pestana.cerrar()
            self.tabview.delete(nombre)

        if not self.pestanas:
            self.desactivar_botones_servidor()
            self.barra_estado.configure(text="📴 Sin conexiones activas")
        else:
            self.actualizar_barra_estado()

    # ======================
    # BARRA DE ESTADO
    # ======================
    def crear_barra_estado(self):
        self.barra_estado = ctk.CTkLabel(
            self,
            text="📴 Sin conexiones activas",
            anchor="w",
            font=ctk.CTkFont(size=11),
            fg_color="#2b2b2b",
            text_color="gray"
        )
        self.barra_estado.grid(row=1, column=1, sticky="ew", padx=10, pady=(0,5))

    def actualizar_barra_estado(self):
        pestana = self.pestana_activa()
        if pestana:
            self.barra_estado.configure(
                text=f"🟢 Conectado a {pestana.ip} como {pestana.usuario} | Pestañas: {len(self.pestanas)}",
                text_color="lightgreen"
            )
        else:
            self.barra_estado.configure(text=f"📶 Conexiones activas: {len(self.pestanas)}", text_color="gray")

    # ======================
    # ACCIONES
    # ======================
    def mostrar_procesos(self):
        pestana = self.pestana_activa()
        if pestana:
            pestana.mostrar_panel_procesos()
            self.actualizar_barra_estado()

    def mostrar_recursos(self):
        pestana = self.pestana_activa()
        if pestana:
            pestana.mostrar_panel_recursos()
            self.actualizar_barra_estado()

    def mostrar_logs(self):
        pestana = self.pestana_activa()
        if pestana:
            pestana.mostrar_panel_logs()
            self.actualizar_barra_estado()

    def abrir_ventana_iniciar(self):
        pestana = self.pestana_activa()
        if not pestana:
            return
        if self.ventana_iniciar is None or not self.ventana_iniciar.winfo_exists():
            self.ventana_iniciar = VentanaIniciar(self, pestana.cliente)
        else:
            self.ventana_iniciar.focus()

    def abrir_ventana_matar(self):
        pestana = self.pestana_activa()
        if not pestana:
            return
        if self.ventana_matar is None or not self.ventana_matar.winfo_exists():
            self.ventana_matar = VentanaMatar(self, pestana.cliente)
        else:
            self.ventana_matar.focus()

    def abrir_ventana_login(self):
        if self.ventana_login is None or not self.ventana_login.winfo_exists():
            self.ventana_login = VentanaLogin(self, self.nueva_pestana)
        else:
            self.ventana_login.focus()

    def mostrar_alerta(self, mensaje):
        # Las alertas ya se manejan desde panel_recursos
        pass