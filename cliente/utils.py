import customtkinter as ctk
import datetime
import os

LOG_FILE = "actividades.log"

def centrar_ventana(ventana, ancho=350, alto=300):
    """Centra una ventana en la pantalla."""
    ventana.update_idletasks()
    x = (ventana.winfo_screenwidth() // 2) - (ancho // 2)
    y = (ventana.winfo_screenheight() // 2) - (alto // 2)
    ventana.geometry(f"{ancho}x{alto}+{x}+{y}")

