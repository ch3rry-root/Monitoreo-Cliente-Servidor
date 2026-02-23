# cliente/gui/icon_manager.py
import os
import platform
from pathlib import Path
from PIL import Image
import customtkinter as ctk

class IconManager:
    """Gestor de iconos multiplataforma usando CTkImage (recomendado por CustomTkinter)"""
    
    def __init__(self):
        self.base_path = Path(__file__).parent.parent / "assets"
        self.icon_cache = {}  # Guardar referencias para evitar garbage collection
        
    def get_icon_path(self, name):
        """Obtiene la ruta del icono según el SO"""
        if platform.system() == "Windows":
            return self.base_path / "icons" / f"{name}.ico"
        else:
            # En Linux/macOS podemos usar PNG, pero intentamos .ico primero si existe
            ico_path = self.base_path / "icons" / f"{name}.ico"
            if ico_path.exists():
                return ico_path
            return self.base_path / "png" / f"{name}.png"
    
    def load_icon(self, name, size=(24, 24)):
        """Carga un icono como CTkImage para usar en botones (escalable en HighDPI)"""
        icon_path = self.get_icon_path(name)
        
        if not icon_path.exists():
            print(f"⚠️ Icono no encontrado: {icon_path}")
            return None
            
        try:
            # Cargar con PIL
            pil_image = Image.open(icon_path)
            
            # Crear CTkImage con el tamaño deseado
            ctk_image = ctk.CTkImage(
                light_image=pil_image,
                dark_image=pil_image,  # Misma imagen para modo oscuro/claro
                size=size
            )
            
            # Guardar referencia para evitar que se elimine
            self.icon_cache[name] = ctk_image
            return ctk_image
        except Exception as e:
            print(f"Error cargando icono {name}: {e}")
            return None
    
    def load_icon_large(self, name, size=(64, 64)):
        """Carga un icono grande para mensajes emergentes"""
        return self.load_icon(name, size)
    
    def set_window_icon(self, window, icon_name="app"):
        """Establece el icono de una ventana (CTk o CTkToplevel)"""
        icon_path = self.get_icon_path(icon_name)
        
        if not icon_path.exists():
            return
            
        system = platform.system()
        
        try:
            if system == "Windows":
                # En Windows, necesitamos un pequeño delay para CTkToplevel 
                window.after(200, lambda: window.iconbitmap(str(icon_path)))
            else:
                # En Linux/macOS usamos iconphoto con PhotoImage (CTkImage no sirve para ventana)
                # Pero podemos convertir el .ico a PhotoImage para el icono de ventana
                img = Image.open(icon_path)
                from PIL import ImageTk
                photo = ImageTk.PhotoImage(img, master=window)
                window.after(200, lambda: window.iconphoto(True, photo))
                self.icon_cache[f"window_{id(window)}"] = photo
        except Exception as e:
            print(f"Error estableciendo icono: {e}")