import customtkinter as ctk
import threading
from tkinter import ttk
from cliente import acciones
from cliente.constantes import COLOR_PRIMARIO

class PanelProcesos(ctk.CTkFrame):
    def __init__(self, parent, cliente):
        super().__init__(parent, fg_color="transparent")
        self.cliente = cliente
        self.monitoreando = False
        self.after_id = None

        self.crear_tabla()

    def crear_tabla(self):
        # Configurar estilo de la tabla para tema oscuro
        style = ttk.Style()
        style.theme_use('clam')
        style.configure("Treeview", 
                        background="#2b2b2b", 
                        foreground="white", 
                        fieldbackground="#2b2b2b",
                        rowheight=25)
        style.configure("Treeview.Heading", 
                        background="#333333", 
                        foreground="white", 
                        relief="flat")
        style.map('Treeview', background=[('selected', COLOR_PRIMARIO)])

        columnas = ('PID', 'Nombre', 'CPU %', 'Memoria %')
        self.tabla = ttk.Treeview(self, columns=columnas, show='headings', height=20)
        self.tabla.heading('PID', text='PID')
        self.tabla.heading('Nombre', text='Nombre')
        self.tabla.heading('CPU %', text='CPU %')
        self.tabla.heading('Memoria %', text='Memoria %')

        self.tabla.column('PID', width=80, anchor='center')
        self.tabla.column('Nombre', width=250)
        self.tabla.column('CPU %', width=80, anchor='center')
        self.tabla.column('Memoria %', width=100, anchor='center')

        scrollbar = ttk.Scrollbar(self, orient='vertical', command=self.tabla.yview)
        self.tabla.configure(yscrollcommand=scrollbar.set)

        self.tabla.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def actualizar_tabla(self, datos):
        # Limpiar filas existentes
        for row in self.tabla.get_children():
            self.tabla.delete(row)

        if isinstance(datos, dict) and "error" in datos:
            self.tabla.insert('', 'end', values=("Error", datos["error"], "", ""))
            return

        if not isinstance(datos, list):
            self.tabla.insert('', 'end', values=("Error", "Formato de datos incorrecto", "", ""))
            return

        for proc in datos:
            pid = proc.get('pid', '')
            nombre = proc.get('name', '')
            cpu = proc.get('cpu_percent', 0)
            memoria = proc.get('memory_percent', 0)
            self.tabla.insert('', 'end', values=(
                pid, 
                nombre, 
                f'{cpu:.2f}' if cpu is not None else 'N/A', 
                f'{memoria:.2f}' if memoria is not None else 'N/A'
            ))

    def obtener_procesos_periodicamente(self):
        if not self.monitoreando:
            return

        def tarea():
            try:
                datos = acciones.listar_procesos(self.cliente)
                self.after(0, lambda: self.actualizar_tabla(datos))
            except Exception as e:
                # Capturamos e en la lambda
                self.after(0, lambda e=e: self.actualizar_tabla({"error": str(e)}))
            finally:
                if self.monitoreando:
                    self.after_id = self.after(2000, self.obtener_procesos_periodicamente)
                    
        threading.Thread(target=tarea, daemon=True).start()

    def iniciar_monitoreo(self):
        self.monitoreando = True
        self.obtener_procesos_periodicamente()

    def detener(self):
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None
        self.monitoreando = False