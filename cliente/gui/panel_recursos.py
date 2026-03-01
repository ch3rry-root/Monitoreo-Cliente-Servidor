import threading

import customtkinter as ctk
import matplotlib
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from cliente import acciones
from cliente.constantes import (
    COLOR_BORDE,
    COLOR_ERROR,
    COLOR_MUTED,
    COLOR_PRIMARIO,
    COLOR_SUCCESS,
    COLOR_TEXTO,
    COLOR_WARNING,
    FONDO_PANEL,
)

matplotlib.use("TkAgg")


class PanelRecursos(ctk.CTkFrame):
    def __init__(
        self,
        parent,
        cliente,
        callback_alerta=None,
        callback_metrica=None,
    ):
        super().__init__(parent, fg_color="transparent")
        self.cliente = cliente
        self.callback_alerta = callback_alerta
        self.callback_metrica = callback_metrica

        self.monitoreando = False
        self.after_id = None

        self.alerta_cpu_activa = False
        self.alerta_mem_activa = False

        self.tiempos = list(range(60))
        self.cpu_hist = [0.0] * 60
        self.mem_hist = [0.0] * 60

        self.area_cpu = None
        self.area_mem = None
        self._destruido = False

        self._crear_widgets()
        self.bind("<Destroy>", self._on_destroy, add="+")

    def _on_destroy(self, _event):
        self._destruido = True
        self.monitoreando = False
        if self.after_id:
            try:
                self.after_cancel(self.after_id)
            except Exception:
                pass
            self.after_id = None

    def _esta_vivo(self):
        return not self._destruido and self.winfo_exists()

    def _safe_after(self, ms, callback):
        if not self._esta_vivo():
            return None
        try:
            return self.after(ms, callback)
        except Exception:
            return None

    def _crear_widgets(self):
        metrics_row = ctk.CTkFrame(self, fg_color="transparent")
        metrics_row.pack(fill="x", padx=2, pady=(0, 10))

        self.card_cpu = self._crear_card_metrica(metrics_row, "CPU")
        self.card_cpu.pack(side="left", fill="x", expand=True, padx=(0, 8))

        self.card_mem = self._crear_card_metrica(metrics_row, "Memoria")
        self.card_mem.pack(side="left", fill="x", expand=True, padx=(8, 0))

        chart_shell = ctk.CTkFrame(self, fg_color=FONDO_PANEL, corner_radius=8)
        chart_shell.pack(fill="both", expand=True)

        self.fig = Figure(figsize=(10, 5), dpi=100, facecolor=FONDO_PANEL)
        self.ax_cpu = self.fig.add_subplot(211)
        self.ax_mem = self.fig.add_subplot(212)

        self._estilizar_eje(self.ax_cpu, "Uso de CPU %")
        self._estilizar_eje(self.ax_mem, "Uso de Memoria %")

        (self.linea_cpu,) = self.ax_cpu.plot(self.tiempos, self.cpu_hist, color=COLOR_PRIMARIO, linewidth=2.2)
        (self.linea_mem,) = self.ax_mem.plot(self.tiempos, self.mem_hist, color=COLOR_WARNING, linewidth=2.2)

        self.area_cpu = self.ax_cpu.fill_between(self.tiempos, self.cpu_hist, color=COLOR_PRIMARIO, alpha=0.18)
        self.area_mem = self.ax_mem.fill_between(self.tiempos, self.mem_hist, color=COLOR_WARNING, alpha=0.18)

        self.fig.tight_layout(pad=2.0)

        self.canvas = FigureCanvasTkAgg(self.fig, master=chart_shell)
        self.canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

    def _crear_card_metrica(self, parent, titulo):
        card = ctk.CTkFrame(parent, fg_color=FONDO_PANEL, corner_radius=8)

        ctk.CTkLabel(
            card,
            text=titulo,
            text_color=COLOR_MUTED,
            font=ctk.CTkFont(size=12, weight="bold"),
        ).pack(anchor="w", padx=16, pady=(14, 2))

        valor = ctk.CTkLabel(
            card,
            text="0.0%",
            text_color=COLOR_TEXTO,
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        valor.pack(anchor="w", padx=16)

        estado = ctk.CTkLabel(
            card,
            text="normal",
            text_color=COLOR_SUCCESS,
            font=ctk.CTkFont(size=11, weight="bold"),
        )
        estado.pack(anchor="w", padx=16, pady=(2, 12))

        if titulo == "CPU":
            self.lbl_cpu_valor = valor
            self.lbl_cpu_estado = estado
        else:
            self.lbl_mem_valor = valor
            self.lbl_mem_estado = estado

        return card

    def _estilizar_eje(self, axis, titulo):
        axis.set_facecolor("#1A1D24")
        axis.set_xlim(0, 60)
        axis.set_ylim(0, 100)
        axis.set_title(titulo, fontsize=12, color=COLOR_TEXTO, loc="left", pad=8)
        axis.tick_params(colors=COLOR_MUTED)
        axis.grid(True, linestyle="--", linewidth=0.8, alpha=0.24)

        for spine in axis.spines.values():
            spine.set_color(COLOR_BORDE)

    def mostrar_alerta_emergente(self, titulo, mensaje):
        if callable(self.callback_alerta):
            self.callback_alerta(titulo, mensaje, "warning")

    def _estado_metrica(self, valor, warning, critical):
        if valor >= critical:
            return "critico", COLOR_ERROR
        if valor >= warning:
            return "alto", COLOR_WARNING
        return "normal", COLOR_SUCCESS

    def agregar_dato(self, cpu, memoria):
        if not self._esta_vivo():
            return

        try:
            cpu = float(cpu)
        except Exception:
            cpu = 0.0

        try:
            memoria = float(memoria)
        except Exception:
            memoria = 0.0

        self.cpu_hist.pop(0)
        self.cpu_hist.append(cpu)
        self.mem_hist.pop(0)
        self.mem_hist.append(memoria)

        self.linea_cpu.set_data(self.tiempos, self.cpu_hist)
        self.linea_mem.set_data(self.tiempos, self.mem_hist)

        if self.area_cpu:
            self.area_cpu.remove()
        if self.area_mem:
            self.area_mem.remove()

        self.area_cpu = self.ax_cpu.fill_between(self.tiempos, self.cpu_hist, color=COLOR_PRIMARIO, alpha=0.18)
        self.area_mem = self.ax_mem.fill_between(self.tiempos, self.mem_hist, color=COLOR_WARNING, alpha=0.18)

        estado_cpu, color_cpu = self._estado_metrica(cpu, warning=70, critical=90)
        estado_mem, color_mem = self._estado_metrica(memoria, warning=80, critical=95)

        if self._esta_vivo():
            self.lbl_cpu_valor.configure(text=f"{cpu:.1f}%")
            self.lbl_mem_valor.configure(text=f"{memoria:.1f}%")
            self.lbl_cpu_estado.configure(text=estado_cpu.upper(), text_color=color_cpu)
            self.lbl_mem_estado.configure(text=estado_mem.upper(), text_color=color_mem)
            self.canvas.draw_idle()

        if self.callback_metrica:
            self.callback_metrica(cpu, memoria)

        if cpu > 90 and not self.alerta_cpu_activa:
            self.alerta_cpu_activa = True
            self.mostrar_alerta_emergente("Alerta CPU", f"CPU en {cpu:.1f}%")
        elif cpu <= 90:
            self.alerta_cpu_activa = False

        if memoria > 95 and not self.alerta_mem_activa:
            self.alerta_mem_activa = True
            self.mostrar_alerta_emergente("Alerta Memoria", f"Memoria en {memoria:.1f}%")
        elif memoria <= 95:
            self.alerta_mem_activa = False

    def obtener_recursos_periodicamente(self):
        if not self.monitoreando or not self._esta_vivo():
            return

        def tarea():
            if not self.monitoreando or not self._esta_vivo():
                return
            try:
                datos = acciones.monitorear_recursos(self.cliente)
                cpu = datos.get("cpu", 0)
                memoria = datos.get("memoria", 0)
                self._safe_after(0, lambda cpu=cpu, memoria=memoria: self.agregar_dato(cpu, memoria))
            except Exception as e:
                print(f"Error obteniendo recursos: {e}")
            finally:
                if self.monitoreando and self._esta_vivo():
                    self.after_id = self._safe_after(2000, self.obtener_recursos_periodicamente)

        threading.Thread(target=tarea, daemon=True).start()

    def iniciar_monitoreo(self):
        if self.monitoreando:
            return
        self.monitoreando = True
        self.obtener_recursos_periodicamente()

    def detener(self):
        self.monitoreando = False
        if self.after_id:
            try:
                self.after_cancel(self.after_id)
            except Exception:
                pass
            self.after_id = None
