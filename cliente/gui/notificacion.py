# cliente/gui/notificacion.py
import customtkinter as ctk

class Notificacion(ctk.CTkToplevel):
    def __init__(self, parent, mensaje, duracion=3000, tipo="info"):
        super().__init__(parent)
        self.overrideredirect(True)  # Sin bordes
        self.attributes("-topmost", True)

        # Colores según tipo
        colores = {
            "info": "#3498db",
            "exito": "#2ecc71",
            "error": "#e74c3c",
            "alerta": "#f39c12"
        }
        color_fondo = colores.get(tipo, "#3498db")

        # Frame principal
        frame = ctk.CTkFrame(self, fg_color=color_fondo, corner_radius=10)
        frame.pack(padx=10, pady=10)

        # Mensaje
        label = ctk.CTkLabel(frame, text=mensaje, text_color="white", font=ctk.CTkFont(size=12))
        label.pack(padx=20, pady=10)

        # Posicionar en esquina inferior derecha
        self.update_idletasks()
        x = parent.winfo_x() + parent.winfo_width() - self.winfo_width() - 20
        y = parent.winfo_y() + parent.winfo_height() - self.winfo_height() - 20
        self.geometry(f"+{x}+{y}")

        # Cerrar después de duración
        self.after(duracion, self.destroy)