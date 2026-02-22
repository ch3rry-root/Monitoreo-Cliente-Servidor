import customtkinter as ctk

class PanelTexto(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="transparent")
        self.textbox = ctk.CTkTextbox(self, font=("Consolas", 13))
        self.textbox.pack(expand=True, fill="both")

    def escribir(self, texto):
        self.textbox.insert("end", texto + "\n")
        self.textbox.see("end")

    def detener(self):
        # Este panel no tiene actualizaciones periódicas, pero se define por consistencia
        pass