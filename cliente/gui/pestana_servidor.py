# cliente/gui/pestana_servidor.py
import customtkinter as ctk

from .panel_procesos import PanelProcesos
from .panel_recursos import PanelRecursos
from .panel_logs import PanelLogs

class PestanaServidor(ctk.CTkFrame):
    """
    Representa una pestaña individual con su propio cliente y panel.
    """
    def __init__(self, parent, cliente, ip, usuario, icon_manager, callback_alerta):
        super().__init__(parent, fg_color="transparent")
        self.cliente = cliente
        self.ip = ip
        self.usuario = usuario
        self.icon_manager = icon_manager
        self.callback_alerta = callback_alerta
        self.panel_actual = None

    def mostrar_panel_procesos(self):
        panel = PanelProcesos(self, self.cliente)
        self._cambiar_panel(panel)
        panel.iniciar_monitoreo()

    def mostrar_panel_recursos(self):
        panel = PanelRecursos(self, self.cliente, self.icon_manager, self.callback_alerta)
        self._cambiar_panel(panel)
        panel.iniciar_monitoreo()

    def mostrar_panel_logs(self):
        self._cambiar_panel(PanelLogs(self))

    def _cambiar_panel(self, nuevo_panel):
        if self.panel_actual:
            self.panel_actual.detener()
            self.panel_actual.destroy()
        self.panel_actual = nuevo_panel
        self.panel_actual.pack(expand=True, fill="both")

    def cerrar(self):
        if self.panel_actual:
            self.panel_actual.detener()
        self.cliente.desconectar()
        self.destroy()