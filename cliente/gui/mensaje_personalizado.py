import customtkinter as ctk
from cliente.constantes import COLOR_PRIMARIO, COLOR_HOVER
from cliente.utils import centrar_ventana

class MensajePersonalizado(ctk.CTkToplevel):
    def __init__(self, parent, titulo, mensaje, tipo="exito"):
        super().__init__(parent)
        self.title(titulo)
        
        # Centrar la ventana
        centrar_ventana(self, 400, 200)
        
        self.transient(parent)
        self.grab_set()
        self.focus()

        # Marco principal
        self.marco = ctk.CTkFrame(self, fg_color="transparent")
        self.marco.pack(expand=True, fill="both", padx=20, pady=20)

        # Icono según tipo
        if tipo == "exito":
            icono = "✓"
            color_boton = "#4CAF50"   # Verde
        else:
            icono = "✗"
            color_boton = "#FF4444"  # Rojo

        # Etiqueta del icono
        ctk.CTkLabel(
            self.marco,
            text=icono,
            font=ctk.CTkFont(size=48, weight="bold"),
            text_color=color_boton
        ).pack(pady=(0, 10))

        # Mensaje
        ctk.CTkLabel(
            self.marco,
            text=mensaje,
            font=ctk.CTkFont(size=14),
            wraplength=350
        ).pack(pady=10)

        # Botón Aceptar
        ctk.CTkButton(
            self.marco,
            text="Aceptar",
            fg_color=color_boton,
            hover_color="#45a049" if color_boton == "#4CAF50" else "#e57373",
            command=self.destroy,
            width=150,
            height=35
        ).pack(pady=10)
        
        # No usamos wait_window() para evitar problemas de foco