# cliente/gui/panel_logs.py
import customtkinter as ctk
from cliente.logger import obtener_ultimos

class PanelLogs(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.crear_widgets()
        self.cargar_logs()

    def crear_widgets(self):
        # Frame superior con botón de refrescar
        top_frame = ctk.CTkFrame(self, fg_color="transparent")
        top_frame.pack(fill="x", pady=(0, 10))

        self.btn_refresh = ctk.CTkButton(
            top_frame,
            text="Refrescar",
            command=self.cargar_logs,
            width=100
        )
        self.btn_refresh.pack(side="left")

        # Área de texto con scroll
        self.textbox = ctk.CTkTextbox(
            self,
            font=("Consolas", 12),
            wrap="word"
        )
        self.textbox.pack(expand=True, fill="both")

    def cargar_logs(self):
        """Carga las últimas líneas del log en el textbox."""
        lineas = obtener_ultimos(200)  # Últimas 200 líneas
        contenido = "".join(lineas) if lineas else "No hay registros aún."

        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", contenido)
        self.textbox.see("end")  # Scroll al final

    def detener(self):
        """No hay actualizaciones periódicas, pero lo dejamos por compatibilidad."""
        pass