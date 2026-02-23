import customtkinter as ctk
from cliente.constantes import COLOR_PRIMARIO, COLOR_HOVER, FONDO_DERECHA
from cliente.utils import centrar_ventana
from .ventana_login import VentanaLogin
from .ventana_iniciar import VentanaIniciar
from .ventana_matar import VentanaMatar
from .pestana_servidor import PestanaServidor

class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Sistema de Monitoreo Distribuido")
        centrar_ventana(self, 1000, 600)

        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.crear_menu()
        self.crear_panel_derecho()

        self.pestanas = {}  # nombre -> objeto PestanaServidor
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

        self.btn_nueva_conexion = self.crear_boton("Nueva conexión", self.abrir_ventana_login)
        self.btn_procesos = self.crear_boton("Procesos", self.mostrar_procesos, False)
        self.btn_recursos = self.crear_boton("Recursos", self.mostrar_recursos, False)
        self.btn_iniciar = self.crear_boton("Iniciar Proceso", self.abrir_ventana_iniciar, False)
        self.btn_matar = self.crear_boton("Matar Proceso", self.abrir_ventana_matar, False)
        self.btn_logs = self.crear_boton("Ver Logs", self.mostrar_logs, False)
        self.btn_cerrar_pestana = self.crear_boton("Cerrar pestaña", self.cerrar_pestana_activa, False)

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
        boton.pack(padx=20, pady=5, fill="x")
        if not activo:
            boton.configure(state="disabled")
        return boton

    def activar_botones_servidor(self):
        """Habilita los botones que dependen de una pestaña activa."""
        self.btn_procesos.configure(state="normal")
        self.btn_recursos.configure(state="normal")
        self.btn_iniciar.configure(state="normal")
        self.btn_matar.configure(state="normal")
        self.btn_logs.configure(state="normal")
        self.btn_cerrar_pestana.configure(state="normal")

    def desactivar_botones_servidor(self):
        """Deshabilita los botones cuando no hay pestañas."""
        self.btn_procesos.configure(state="disabled")
        self.btn_recursos.configure(state="disabled")
        self.btn_iniciar.configure(state="disabled")
        self.btn_matar.configure(state="disabled")
        self.btn_logs.configure(state="disabled")
        self.btn_cerrar_pestana.configure(state="disabled")

    # ======================
    # PANEL DERECHO CON PESTAÑAS
    # ======================
    def crear_panel_derecho(self):
        self.panel = ctk.CTkFrame(self, fg_color=FONDO_DERECHA)
        self.panel.grid(row=0, column=1, sticky="nsew", padx=10, pady=10)

        # Tabview para las pestañas
        self.tabview = ctk.CTkTabview(self.panel, fg_color="transparent")
        self.tabview.pack(expand=True, fill="both")

    def nueva_pestana(self, cliente, ip, usuario, cert_path):
        """Crea una nueva pestaña con el servidor conectado."""
        # Generar nombre de pestaña (IP + usuario, o contador si se repite)
        base = f"{ip} - {usuario}"
        nombre = base
        contador = 1
        while nombre in self.pestanas:
            contador += 1
            nombre = f"{base} ({contador})"

        # Agregar la pestaña al tabview
        self.tabview.add(nombre)

        # Crear el frame de la pestaña y colocarlo dentro
        pestana_frame = self.tabview.tab(nombre)
        pestana = PestanaServidor(pestana_frame, cliente, ip, usuario, self.mostrar_alerta)
        pestana.pack(expand=True, fill="both")

        # Guardar referencia
        self.pestanas[nombre] = pestana

        # Activar botones de servidor
        self.activar_botones_servidor()

    def pestana_activa(self):
        """Devuelve el objeto PestanaServidor de la pestaña actual, o None."""
        nombre = self.tabview.get()
        return self.pestanas.get(nombre)

    def cerrar_pestana_activa(self):
        """Cierra la pestaña actual y limpia recursos."""
        nombre = self.tabview.get()
        if nombre and nombre in self.pestanas:
            pestana = self.pestanas.pop(nombre)
            pestana.cerrar()
            self.tabview.delete(nombre)

        # Si no quedan pestañas, desactivar botones
        if not self.pestanas:
            self.desactivar_botones_servidor()
            # Mostrar panel vacío o mensaje
            if hasattr(self, 'tabview') and len(self.tabview._segmented_button._buttons_dict) == 0:
                # No hay pestañas, podríamos mostrar un mensaje
                pass

    # ======================
    # ACCIONES DE LOS BOTONES (afectan a la pestaña activa)
    # ======================
    def mostrar_procesos(self):
        pestana = self.pestana_activa()
        if pestana:
            pestana.mostrar_panel_procesos()

    def mostrar_recursos(self):
        pestana = self.pestana_activa()
        if pestana:
            pestana.mostrar_panel_recursos()

    def mostrar_logs(self):
        pestana = self.pestana_activa()
        if pestana:
            pestana.mostrar_panel_logs()

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

    # ======================
    # ALERTAS (se pasan a cada pestaña)
    # ======================
    def mostrar_alerta(self, mensaje):
        """Este método es llamado desde los paneles de recursos para alertas emergentes.
        Lo manejamos con MensajePersonalizado directamente, pero como ya se hace en panel_recursos,
        aquí no es necesario hacer nada. Lo dejamos por si acaso."""
        pass