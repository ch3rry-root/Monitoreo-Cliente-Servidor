# cliente/gui/barra_titulo.py
import customtkinter as ctk

class BarraTitulo(ctk.CTkFrame):
    def __init__(self, parent, titulo="Sistema de Monitoreo", cerrar_func=None):
        super().__init__(parent, height=40, corner_radius=0, fg_color="#1E1E2E")
        self.parent = parent
        self.cerrar_func = cerrar_func

        # Hacer que la barra sea arrastrable
        self.bind("<Button-1>", self.start_move)
        self.bind("<B1-Motion>", self.on_move)

        # Título centrado
        self.label_titulo = ctk.CTkLabel(self, text=titulo, font=ctk.CTkFont(size=14, weight="bold"))
        self.label_titulo.pack(side="left", padx=10)

        # Botones de ventana
        self.btn_minimizar = ctk.CTkButton(self, text="─", width=30, height=30, corner_radius=0,
                                           fg_color="transparent", hover_color="#4A4E69",
                                           command=self.minimizar)
        self.btn_minimizar.pack(side="right", padx=2)

        self.btn_cerrar = ctk.CTkButton(self, text="✕", width=30, height=30, corner_radius=0,
                                        fg_color="transparent", hover_color="#EF233C",
                                        command=self.cerrar)
        self.btn_cerrar.pack(side="right", padx=2)

    def start_move(self, event):
        self.x = event.x
        self.y = event.y

    def on_move(self, event):
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.parent.winfo_x() + deltax
        y = self.parent.winfo_y() + deltay
        self.parent.geometry(f"+{x}+{y}")

    def minimizar(self):
        self.parent.iconify()

    def cerrar(self):
        if self.cerrar_func:
            self.cerrar_func()
        else:
            self.parent.destroy()