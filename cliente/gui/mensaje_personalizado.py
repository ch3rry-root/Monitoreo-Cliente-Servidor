import customtkinter as ctk

from cliente.constantes import (
    COLOR_BORDE,
    COLOR_ERROR,
    COLOR_MUTED,
    COLOR_SUCCESS,
    COLOR_TEXTO,
    COLOR_WARNING,
    FONDO_CARD,
)


class MensajePersonalizado(ctk.CTkFrame):
    def __init__(self, parent, titulo, mensaje, tipo="exito", on_close=None):
        super().__init__(parent, fg_color="transparent")
        self.on_close = on_close

        estilos = {
            "exito": COLOR_SUCCESS,
            "warning": COLOR_WARNING,
            "error": COLOR_ERROR,
        }
        color_boton = estilos.get(tipo, COLOR_WARNING)

        card = ctk.CTkFrame(
            self,
            fg_color=FONDO_CARD,
            corner_radius=14,
            border_width=1,
            border_color=COLOR_BORDE,
        )
        card.pack(expand=True, fill="both")

        top = ctk.CTkFrame(card, fg_color="transparent")
        top.pack(fill="x", padx=18, pady=(14, 0))

        ctk.CTkLabel(
            top,
            text=titulo,
            font=ctk.CTkFont(size=22, weight="bold"),
            text_color=COLOR_TEXTO,
        ).pack(anchor="center")

        ctk.CTkLabel(
            card,
            text=mensaje,
            font=ctk.CTkFont(size=13),
            text_color=COLOR_TEXTO,
            wraplength=390,
            justify="center",
        ).pack(padx=18, pady=(22, 24), fill="x")

        ctk.CTkButton(
            card,
            text="Aceptar",
            fg_color=color_boton,
            hover_color="#16A34A" if tipo == "exito" else "#D97706" if tipo == "warning" else "#DC2626",
            text_color="#F8FAFC",
            width=190,
            height=40,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.cerrar,
        ).pack(pady=(0, 18))

        ctk.CTkLabel(
            card,
            text="",
            font=ctk.CTkFont(size=11),
            text_color=COLOR_MUTED,
        ).pack()

    def focus_principal(self):
        self.focus_set()

    def cerrar(self):
        if callable(self.on_close):
            self.on_close()
