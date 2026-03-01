import customtkinter as ctk

from cliente.constantes import (
    COLOR_INPUT,
    COLOR_MUTED,
    COLOR_PRIMARIO,
    COLOR_TEXTO,
    FONDO_PANEL,
)
from cliente.logger import obtener_ultimos


class PanelLogs(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self._crear_layout()
        self.cargar_logs()

    def _crear_layout(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            top,
            text="REGISTROS DEL SISTEMA",
            text_color=COLOR_TEXTO,
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(side="left")

        self.lbl_count = ctk.CTkLabel(
            top,
            text="0 lineas",
            text_color=COLOR_MUTED,
            font=ctk.CTkFont(size=12),
        )
        self.lbl_count.pack(side="right", padx=(0, 8))

        self.btn_refresh = ctk.CTkButton(
            top,
            text="Actualizar",
            width=110,
            height=32,
            corner_radius=7,
            fg_color=COLOR_PRIMARIO,
            hover_color="#2BB3FF",
            text_color="#FFFFFF",
            command=self.cargar_logs,
        )
        self.btn_refresh.pack(side="right", padx=(0, 10))

        shell = ctk.CTkFrame(self, fg_color=FONDO_PANEL, corner_radius=8)
        shell.pack(fill="both", expand=True)

        self.textbox = ctk.CTkTextbox(
            shell,
            fg_color=COLOR_INPUT,
            text_color=COLOR_TEXTO,
            font=("Consolas", 11),
            wrap="none",
            border_width=0,
            corner_radius=6,
        )
        self.textbox.pack(fill="both", expand=True, padx=12, pady=12)

    def cargar_logs(self):
        lineas = obtener_ultimos(250)
        contenido = "".join(lineas) if lineas else "SIN DATOS"

        self.textbox.configure(state="normal")
        self.textbox.delete("1.0", "end")
        self.textbox.insert("1.0", contenido)
        self.textbox.configure(state="disabled")

        self.lbl_count.configure(text=f"{len(lineas)} lineas")

    def detener(self):
        pass
