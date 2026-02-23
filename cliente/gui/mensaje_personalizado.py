# cliente/gui/mensaje_personalizado.py
import customtkinter as ctk
from cliente.constantes import COLOR_PRIMARIO, COLOR_HOVER
from cliente.utils import centrar_ventana

class MensajePersonalizado(ctk.CTkToplevel):
    def __init__(self, parent, titulo, mensaje, tipo="exito", icon_manager=None, icono=None):
        super().__init__(parent)
        self.title(titulo)
        
        # Ajustar tamaño de ventana según contenido (ligeramente más grande)
        centrar_ventana(self, 450, 250)
        
        self.transient(parent)
        self.grab_set()
        self.focus()

        self.marco = ctk.CTkFrame(self, fg_color="transparent")
        self.marco.pack(expand=True, fill="both", padx=20, pady=20)

        # Determinar color de fondo del botón según tipo
        if tipo == "exito":
            color_boton = "#4CAF50"   # Verde
            icono_pred = "success" if icon_manager else None
        elif tipo == "error":
            color_boton = "#FF4444"    # Rojo
            icono_pred = "warning" if icon_manager else None
        elif tipo == "warning":
            color_boton = "#FFA500"    # Naranja
            icono_pred = "warning" if icon_manager else None
        else:
            color_boton = "#3498db"    # Azul
            icono_pred = None

        # Mostrar icono si se proporcionó o se puede cargar
        if icono is not None:
            # Si ya pasaron un icono CTkImage, lo usamos
            label_icon = ctk.CTkLabel(self.marco, image=icono, text="")
            label_icon.pack(pady=(0, 10))
        elif icon_manager and icono_pred:
            # Cargar icono por nombre
            icono_cargado = icon_manager.load_icon_large(icono_pred, (64, 64))
            if icono_cargado:
                label_icon = ctk.CTkLabel(self.marco, image=icono_cargado, text="")
                label_icon.pack(pady=(0, 10))
        else:
            # Fallback a emoji
            if tipo == "exito":
                emoji = "✓"
            else:
                emoji = "✗"
            ctk.CTkLabel(
                self.marco,
                text=emoji,
                font=ctk.CTkFont(size=48, weight="bold"),
                text_color=color_boton
            ).pack(pady=(0, 10))

        # Mensaje
        ctk.CTkLabel(
            self.marco,
            text=mensaje,
            font=ctk.CTkFont(size=14),
            wraplength=400  # Aumentado para mejor legibilidad
        ).pack(pady=10)

        # Botón Aceptar (más ancho)
        ctk.CTkButton(
            self.marco,
            text="Aceptar",
            fg_color=color_boton,
            hover_color="#45a049" if color_boton == "#4CAF50" else "#e57373",
            command=self.destroy,
            width=200,  # Aumentado de 150 a 200
            height=40   # Un poco más alto
        ).pack(pady=10)