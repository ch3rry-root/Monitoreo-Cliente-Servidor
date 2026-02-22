import customtkinter as ctk
import threading
import time
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
from cliente import acciones
from cliente.constantes import COLOR_PRIMARIO
from .mensaje_personalizado import MensajePersonalizado

class PanelRecursos(ctk.CTkFrame):
    def __init__(self, parent, cliente, callback_alerta=None):
        super().__init__(parent, fg_color="transparent")
        self.cliente = cliente
        self.callback_alerta = callback_alerta
        self.monitoreando = False
        self.after_id = None
        
        # Control de alertas para que no se repitan mientras el recurso sigue alto
        self.alerta_cpu_activa = False   # True si ya mostramos alerta de CPU y sigue alta
        self.alerta_mem_activa = False   # True si ya mostramos alerta de memoria y sigue alta
        
        # Historial de datos (últimos 60 puntos)
        self.tiempos = list(range(60))
        self.cpu_hist = [0] * 60
        self.mem_hist = [0] * 60
        
        self.crear_graficos()
    
    def crear_graficos(self):
        self.frame_graficos = ctk.CTkFrame(self, fg_color="transparent")
        self.frame_graficos.pack(expand=True, fill="both")
        
        self.fig = Figure(figsize=(8, 4), dpi=100, facecolor='#2b2b2b')
        
        # Gráfico de CPU
        self.ax_cpu = self.fig.add_subplot(211)
        self.ax_cpu.set_facecolor('#1e1e1e')
        self.ax_cpu.set_title('Uso de CPU (%)', color='white')
        self.ax_cpu.set_xlim(0, 60)
        self.ax_cpu.set_ylim(0, 100)
        self.ax_cpu.tick_params(colors='white')
        self.ax_cpu.grid(True, linestyle='--', alpha=0.3)
        self.linea_cpu, = self.ax_cpu.plot(self.tiempos, self.cpu_hist, color=COLOR_PRIMARIO, linewidth=2)
        
        # Gráfico de Memoria
        self.ax_mem = self.fig.add_subplot(212)
        self.ax_mem.set_facecolor('#1e1e1e')
        self.ax_mem.set_title('Uso de Memoria (%)', color='white')
        self.ax_mem.set_xlim(0, 60)
        self.ax_mem.set_ylim(0, 100)
        self.ax_mem.tick_params(colors='white')
        self.ax_mem.grid(True, linestyle='--', alpha=0.3)
        self.linea_mem, = self.ax_mem.plot(self.tiempos, self.mem_hist, color='#FFA500', linewidth=2)
        
        self.fig.tight_layout()
        
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.frame_graficos)
        self.canvas.get_tk_widget().pack(expand=True, fill="both")
    
    def mostrar_alerta_emergente(self, titulo, mensaje, tipo="error"):
        """Muestra una ventana emergente personalizada."""
        self.after(0, lambda: MensajePersonalizado(self.winfo_toplevel(), titulo, mensaje, tipo))
    
    def agregar_dato(self, cpu, memoria):
        # Rotar historial
        self.cpu_hist.pop(0)
        self.cpu_hist.append(cpu)
        self.mem_hist.pop(0)
        self.mem_hist.append(memoria)
        
        # Actualizar líneas
        self.linea_cpu.set_data(self.tiempos, self.cpu_hist)
        self.linea_mem.set_data(self.tiempos, self.mem_hist)
        
        self.ax_cpu.relim()
        self.ax_cpu.autoscale_view(scalex=False)
        self.ax_mem.relim()
        self.ax_mem.autoscale_view(scalex=False)
        
        self.canvas.draw_idle()
        
        # --- ALERTAS INTELIGENTES ---
        # CPU
        if cpu > 90:
            if not self.alerta_cpu_activa:
                self.alerta_cpu_activa = True
                self.mostrar_alerta_emergente(
                    "Alerta de CPU",
                    f"CPU al {cpu:.1f}% - Alto consumo",
                    "error"
                )
        else:
            # Si baja del umbral, reseteamos el flag para que pueda volver a alertar si sube otra vez
            self.alerta_cpu_activa = False
        
        # Memoria
        if memoria > 95:
            if not self.alerta_mem_activa:
                self.alerta_mem_activa = True
                self.mostrar_alerta_emergente(
                    "Alerta de Memoria",
                    f"Memoria al {memoria:.1f}% - Alto consumo",
                    "error"
                )
        else:
            self.alerta_mem_activa = False
    
    def obtener_recursos_periodicamente(self):
        if not self.monitoreando:
            return
        
        def tarea():
            try:
                datos = acciones.monitorear_recursos(self.cliente)
                cpu = datos.get('cpu', 0)
                memoria = datos.get('memoria', 0)
                self.after(0, lambda: self.agregar_dato(cpu, memoria))
            except Exception as e:
                print(f"Error obteniendo recursos: {e}")
            finally:
                if self.monitoreando:
                    self.after_id = self.after(2000, self.obtener_recursos_periodicamente)
        
        threading.Thread(target=tarea, daemon=True).start()
    
    def iniciar_monitoreo(self):
        self.monitoreando = True
        self.obtener_recursos_periodicamente()
    
    def detener(self):
        if self.after_id:
            self.after_cancel(self.after_id)
            self.after_id = None
        self.monitoreando = False