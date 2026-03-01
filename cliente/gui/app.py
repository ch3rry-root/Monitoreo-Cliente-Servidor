import datetime
import queue
import threading
import tkinter as tk

import customtkinter as ctk

from cliente import acciones
from cliente.constantes import (
    COLOR_ACTIVO,
    COLOR_ERROR,
    COLOR_ERROR_HOVER,
    COLOR_FONDO,
    COLOR_HOVER,
    COLOR_INPUT,
    COLOR_MUTED,
    COLOR_PRIMARIO,
    COLOR_SECUNDARIO,
    COLOR_SEPARADOR,
    COLOR_SUCCESS,
    COLOR_SUCCESS_HOVER,
    COLOR_TEXTO,
    FONDO_PANEL,
)
from cliente.logger import registrar_log
from cliente.utils import centrar_ventana

from .mensaje_personalizado import MensajePersonalizado
from .panel_logs import PanelLogs
from .panel_procesos import PanelProcesos
from .panel_recursos import PanelRecursos
from .ventana_iniciar import VentanaIniciar
from .ventana_login import VentanaLogin
from .ventana_matar import VentanaMatar


class App(ctk.CTk):
    TABS = ["Servidores", "Procesos", "Metricas", "Registros", "Conexiones"]
    INTERVALO_SUPERVISION_MS = 3000
    UMBRAL_CPU_ALERTA = 90.0
    UMBRAL_RAM_ALERTA = 95.0
    ALERTA_ANCHO = 360
    ALERTA_ALTO = 44
    ALERTA_Y = 8
    ALERTA_MARGEN_DER = 10

    def __init__(self):
        super().__init__()
        self.title("Panel de control")
        centrar_ventana(self, 1320, 820)
        self.minsize(1120, 700)

        ctk.set_appearance_mode("dark")
        self.configure(fg_color=COLOR_FONDO)

        self.conexiones = {}
        self.servidor_activo = None
        self.server_column_specs = [
            ("SERVIDOR", 300, "w"),
            ("DIRECCION IP", 200, "w"),
            ("ESTADO", 130, "center"),
            ("CPU %", 90, "center"),
            ("RAM %", 90, "center"),
            ("ACTIVO", 120, "center"),
        ]
        self.server_row_widgets = {}

        self.tab_actual = None
        self.panel_dinamico = None
        self._tab_botones = {}
        self._tab_anim_token = 0
        self._tab_render_after_id = None

        self.modal_overlay = None
        self.modal_canvas = None
        self.modal_rect = None
        self.modal_contenedor = None
        self.modal_form = None
        self._supervisor_after_id = None
        self._supervisor_en_ejecucion = False
        self._cola_supervision = queue.Queue()
        self._alertas_consumo = {}
        self._alerta_superior = None
        self._alerta_superior_after_id = None
        self._alerta_anim_token = 0
        self._modal_anim_token = 0

        self.font_logo = ctk.CTkFont(family="Segoe UI", size=17, weight="bold")
        self.font_section_title = ctk.CTkFont(family="Segoe UI", size=15, weight="bold")

        self._crear_top_nav()
        self._set_actions_state(False)
        self._crear_tabs_nav()
        self._crear_area_contenido()
        self._crear_footer()

        self.after(80, lambda: self.cambiar_tab("Servidores", animate=False, force=True))
        self.after(900, self._ciclo_supervision_conexiones)
        self.protocol("WM_DELETE_WINDOW", self.cerrar_aplicacion)

    # ------------------------------
    # Barra superior
    # ------------------------------
    def _crear_top_nav(self):
        self.top_nav = ctk.CTkFrame(self, fg_color=FONDO_PANEL, corner_radius=0, height=60)
        self.top_nav.pack(fill="x", side="top")
        self.top_nav.pack_propagate(False)

        self.top_inner = ctk.CTkFrame(self.top_nav, fg_color="transparent")
        self.top_inner.pack(fill="both", expand=True, padx=18)
        self.top_inner.grid_columnconfigure(0, weight=0)
        self.top_inner.grid_columnconfigure(1, weight=0)
        self.top_inner.grid_columnconfigure(2, weight=1)
        self.top_inner.grid_rowconfigure(0, weight=1)

        logo_frame = ctk.CTkFrame(self.top_inner, fg_color="transparent")
        logo_frame.grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            logo_frame,
            text="Sesiones",
            font=self.font_logo,
            text_color=COLOR_TEXTO,
        ).pack(side="left")

        self.server_selector = ctk.CTkOptionMenu(
            self.top_inner,
            values=["Sin servidores"],
            command=self._cambiar_servidor_activo,
            fg_color=COLOR_INPUT,
            button_color=COLOR_INPUT,
            button_hover_color=COLOR_INPUT,
            dropdown_fg_color=FONDO_PANEL,
            dropdown_hover_color=COLOR_INPUT,
            dropdown_text_color=COLOR_TEXTO,
            text_color=COLOR_TEXTO,
            corner_radius=8,
            height=36,
            width=280,
            dynamic_resizing=False,
        )
        self.server_selector.grid(row=0, column=1, padx=(18, 14), sticky="w")
        self.server_selector.set("Sin servidores")

        actions = ctk.CTkFrame(self.top_inner, fg_color="transparent")
        actions.grid(row=0, column=2, sticky="w")
        self.actions_frame = actions

        self.btn_start = ctk.CTkButton(
            actions,
            text="Iniciar proceso",
            fg_color=COLOR_SUCCESS,
            hover_color=COLOR_SUCCESS_HOVER,
            text_color="#FFFFFF",
            corner_radius=7,
            width=138,
            height=34,
            command=self.abrir_ventana_iniciar,
        )
        self.btn_start.pack(side="left", padx=(0, 8))

        self.btn_kill = ctk.CTkButton(
            actions,
            text="Finalizar proceso",
            fg_color=COLOR_ERROR,
            hover_color=COLOR_ERROR_HOVER,
            text_color="#FFFFFF",
            corner_radius=7,
            width=142,
            height=34,
            command=self.abrir_ventana_matar,
        )
        self.btn_kill.pack(side="left", padx=(0, 8))

        self.btn_restart = ctk.CTkButton(
            actions,
            text="Reiniciar",
            fg_color=COLOR_PRIMARIO,
            hover_color=COLOR_HOVER,
            text_color="#FFFFFF",
            corner_radius=7,
            width=96,
            height=34,
            command=self.reiniciar_vista,
        )
        self.btn_restart.pack(side="left")

        ctk.CTkFrame(self, fg_color=COLOR_SEPARADOR, height=1).pack(fill="x", side="top")

    # ------------------------------
    # Navegacion de tabs
    # ------------------------------
    def _crear_tabs_nav(self):
        self.tabs_nav = ctk.CTkFrame(self, fg_color=COLOR_FONDO, height=46)
        self.tabs_nav.pack(fill="x", side="top")
        self.tabs_nav.pack_propagate(False)

        self.tabs_inner = ctk.CTkFrame(self.tabs_nav, fg_color="transparent")
        self.tabs_inner.pack(fill="both", expand=True, padx=18)

        self.tabs_buttons_frame = ctk.CTkFrame(self.tabs_inner, fg_color="transparent")
        self.tabs_buttons_frame.pack(side="left", fill="y")

        for tab_name in self.TABS:
            btn = ctk.CTkButton(
                self.tabs_buttons_frame,
                text=tab_name,
                fg_color="transparent",
                hover_color="#171B24",
                text_color=COLOR_SECUNDARIO,
                width=110,
                height=42,
                corner_radius=0,
                font=ctk.CTkFont(size=13),
                command=lambda t=tab_name: self.cambiar_tab(t),
            )
            btn.pack(side="left", padx=(0, 12))
            self._tab_botones[tab_name] = btn

        self.underline = ctk.CTkFrame(
            self.tabs_buttons_frame,
            fg_color=COLOR_ACTIVO,
            height=2,
            width=1,
            corner_radius=1,
        )
        self.underline.place(x=0, y=40)

        ctk.CTkFrame(self, fg_color=COLOR_SEPARADOR, height=1).pack(fill="x", side="top")

    def _animar_subrayado(self, target_x, target_w):
        self.tabs_buttons_frame.update_idletasks()
        self._tab_anim_token += 1
        token = self._tab_anim_token

        current_x = self.underline.winfo_x()
        current_w = max(1, self.underline.winfo_width())

        steps = 6
        intervalo = 8
        dx = (target_x - current_x) / steps
        dw = (target_w - current_w) / steps

        def step(i):
            if token != self._tab_anim_token or not self.winfo_exists():
                return
            if i >= steps:
                self.underline.configure(width=target_w)
                self.underline.place_configure(x=target_x)
                return
            self.underline.configure(width=max(1, int(current_w + dw * (i + 1))))
            self.underline.place_configure(x=int(current_x + dx * (i + 1)))
            self.after(intervalo, lambda: step(i + 1))

        step(0)

    def _programar_render_tab(self, delay_ms=0):
        if self._tab_render_after_id:
            try:
                self.after_cancel(self._tab_render_after_id)
            except Exception:
                pass
            self._tab_render_after_id = None

        def ejecutar():
            self._tab_render_after_id = None
            if not self.winfo_exists():
                return
            self._render_tab_content()

        self._tab_render_after_id = self.after(delay_ms, ejecutar)

    def cambiar_tab(self, tab_name, animate=True, force=False):
        if tab_name == self.tab_actual and not force:
            return

        if self.panel_dinamico and hasattr(self.panel_dinamico, "detener"):
            self.panel_dinamico.detener()
        self.panel_dinamico = None

        self.tab_actual = tab_name

        for name, btn in self._tab_botones.items():
            activo = name == tab_name
            btn.configure(text_color=COLOR_PRIMARIO if activo else COLOR_SECUNDARIO)

        self.tabs_buttons_frame.update_idletasks()
        active_btn = self._tab_botones[tab_name]
        target_x = active_btn.winfo_x()
        target_w = active_btn.winfo_width()

        if animate:
            self._animar_subrayado(target_x, target_w)
            self._programar_render_tab(delay_ms=55)
        else:
            self.underline.configure(width=target_w)
            self.underline.place_configure(x=target_x)
            self._programar_render_tab(delay_ms=0)

    # ------------------------------
    # Area de contenido
    # ------------------------------
    def _crear_area_contenido(self):
        self.content_outer = ctk.CTkFrame(self, fg_color="transparent")
        self.content_outer.pack(fill="both", expand=True, padx=18, pady=16)

        self.content = ctk.CTkFrame(self.content_outer, fg_color="transparent")
        self.content.pack(fill="both", expand=True)

    def _limpiar_contenido(self):
        for child in self.content.winfo_children():
            child.destroy()

    def _render_tab_content(self):
        self._limpiar_contenido()

        if self.tab_actual == "Servidores":
            self._render_servers_tab()
            return
        if self.tab_actual == "Procesos":
            self._render_processes_tab()
            return
        if self.tab_actual == "Metricas":
            self._render_metrics_tab()
            return
        if self.tab_actual == "Registros":
            self._render_logs_tab()
            return
        if self.tab_actual == "Conexiones":
            self._render_connections_tab()
            return

    def _render_empty_state(self, titulo="SIN DATOS", detalle="No hay informacion disponible"):
        box = ctk.CTkFrame(self.content, fg_color="transparent")
        box.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(
            box,
            text=titulo,
            text_color=COLOR_MUTED,
            font=ctk.CTkFont(size=24, weight="bold"),
        ).pack()
        ctk.CTkLabel(
            box,
            text=detalle,
            text_color=COLOR_SECUNDARIO,
            font=ctk.CTkFont(size=12),
        ).pack(pady=(6, 0))

    # ------------------------------
    # Tab Servidores
    # ------------------------------
    def _render_servers_tab(self):
        top = ctk.CTkFrame(self.content, fg_color="transparent")
        top.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            top,
            text="INVENTARIO DE SERVIDORES",
            text_color=COLOR_TEXTO,
            font=self.font_section_title,
        ).pack(side="left")

        self.server_filter_entry = ctk.CTkEntry(
            top,
            placeholder_text="Filtrar servidores por nombre o IP",
            fg_color=COLOR_INPUT,
            border_width=1,
            border_color=COLOR_INPUT,
            text_color=COLOR_TEXTO,
            placeholder_text_color=COLOR_MUTED,
            height=34,
            width=320,
        )
        self.server_filter_entry.pack(side="right")
        self.server_filter_entry.bind("<KeyRelease>", lambda _e: self._actualizar_tabla_servidores())
        self.server_filter_entry.bind(
            "<FocusIn>",
            lambda _e: self.server_filter_entry.configure(border_width=2, border_color=COLOR_PRIMARIO),
        )
        self.server_filter_entry.bind(
            "<FocusOut>",
            lambda _e: self.server_filter_entry.configure(border_width=1, border_color=COLOR_INPUT),
        )

        table = ctk.CTkFrame(self.content, fg_color=FONDO_PANEL, corner_radius=8)
        table.pack(fill="both", expand=True)

        header = ctk.CTkFrame(table, fg_color="transparent", height=42)
        header.pack(fill="x", padx=(16, 30), pady=(12, 0))
        header.pack_propagate(False)

        for titulo, ancho, anchor in self.server_column_specs:
            ctk.CTkLabel(
                header,
                text=titulo,
                text_color=COLOR_MUTED,
                font=ctk.CTkFont(size=11, weight="bold"),
                anchor=anchor,
                width=ancho,
            ).pack(side="left", padx=(0, 8), pady=(8, 0))

        ctk.CTkFrame(table, fg_color=COLOR_SEPARADOR, height=1).pack(fill="x", padx=16)

        self.server_rows = ctk.CTkScrollableFrame(table, fg_color="transparent", corner_radius=0)
        self.server_rows.pack(fill="both", expand=True, padx=16, pady=(4, 12))

        self._actualizar_tabla_servidores()

    def _formato_uptime(self, started_at):
        if not started_at:
            return "--"
        delta = datetime.datetime.now() - started_at
        seconds = int(delta.total_seconds())
        h, rem = divmod(seconds, 3600)
        m, s = divmod(rem, 60)
        return f"{h:02}:{m:02}:{s:02}"

    def _widget_vivo(self, widget):
        if widget is None:
            return False
        try:
            return bool(widget.winfo_exists())
        except tk.TclError:
            return False
        except Exception:
            return False

    def _valores_servidor_fila(self, nombre, data):
        estado_txt = "EN LINEA" if data.get("status", "online") == "online" else "DESCONECTADO"
        estado_color = COLOR_SUCCESS if estado_txt == "EN LINEA" else COLOR_MUTED
        cpu = data.get("cpu")
        ram = data.get("ram")
        valores = [
            nombre,
            data.get("ip", "--"),
            estado_txt,
            "--" if cpu is None else f"{cpu:.1f}",
            "--" if ram is None else f"{ram:.1f}",
            self._formato_uptime(data.get("connected_at")) if estado_txt == "EN LINEA" else "--",
        ]
        return valores, estado_color

    def _actualizar_tabla_servidores(self):
        server_rows = getattr(self, "server_rows", None)
        if not self._widget_vivo(server_rows):
            self.server_row_widgets = {}
            return

        try:
            for child in server_rows.winfo_children():
                child.destroy()
        except tk.TclError:
            self.server_row_widgets = {}
            return
        self.server_row_widgets = {}

        filtro = ""
        server_filter = getattr(self, "server_filter_entry", None)
        if self._widget_vivo(server_filter):
            filtro = server_filter.get().strip().lower()

        items = []
        for name, data in self.conexiones.items():
            searchable = f"{name} {data['ip']} {data['usuario']}".lower()
            if filtro and filtro not in searchable:
                continue
            items.append((name, data))

        if not items:
            self._render_no_server_rows()
            return

        for name, data in items:
            row = ctk.CTkFrame(server_rows, fg_color="transparent")
            row.pack(fill="x", pady=(0, 0))

            valores, estado_color = self._valores_servidor_fila(name, data)
            labels = []

            for idx, value in enumerate(valores):
                _, ancho, anchor = self.server_column_specs[idx]
                label = ctk.CTkLabel(
                    row,
                    text=value,
                    text_color=estado_color if idx == 2 else COLOR_TEXTO,
                    font=ctk.CTkFont(size=12, weight="bold" if idx in (0, 2) else "normal"),
                    anchor=anchor,
                    width=ancho,
                )
                label.pack(side="left", padx=(0, 8), pady=(8, 8))
                label.bind("<Button-1>", lambda _e, srv=name: self._seleccionar_servidor_desde_tabla(srv))
                label.bind("<Enter>", lambda _e, fr=row: fr.configure(fg_color=COLOR_INPUT))
                label.bind("<Leave>", lambda _e, fr=row: fr.configure(fg_color="transparent"))
                labels.append(label)

            row.bind("<Enter>", lambda _e, fr=row: fr.configure(fg_color=COLOR_INPUT))
            row.bind("<Leave>", lambda _e, fr=row: fr.configure(fg_color="transparent"))
            row.bind("<Button-1>", lambda _e, srv=name: self._seleccionar_servidor_desde_tabla(srv))
            self.server_row_widgets[name] = {"labels": labels}

            ctk.CTkFrame(server_rows, fg_color=COLOR_SEPARADOR, height=1).pack(fill="x")

    def _actualizar_tabla_servidores_en_vivo(self):
        if not self.server_row_widgets:
            return False

        try:
            for nombre, info in self.server_row_widgets.items():
                data = self.conexiones.get(nombre)
                if not data:
                    continue
                labels = info.get("labels") or []
                valores, estado_color = self._valores_servidor_fila(nombre, data)
                if len(labels) < len(valores):
                    return False
                for idx, value in enumerate(valores):
                    if not labels[idx].winfo_exists():
                        return False
                    labels[idx].configure(
                        text=value,
                        text_color=estado_color if idx == 2 else COLOR_TEXTO,
                    )
            return True
        except Exception:
            return False

    def _render_no_server_rows(self):
        server_rows = getattr(self, "server_rows", None)
        if not self._widget_vivo(server_rows):
            return

        box = ctk.CTkFrame(server_rows, fg_color="transparent")
        box.pack(fill="both", expand=True, pady=80)
        ctk.CTkLabel(
            box,
            text="SIN DATOS",
            text_color=COLOR_MUTED,
            font=ctk.CTkFont(size=22, weight="bold"),
        ).pack()

    def _seleccionar_servidor_desde_tabla(self, nombre):
        if nombre not in self.conexiones:
            return
        self.servidor_activo = nombre
        self.server_selector.set(nombre)
        self._actualizar_estado_acciones()
        self._actualizar_estado_footer()

    # ------------------------------
    # Tabs Procesos / Metricas / Registros
    # ------------------------------
    def _get_servidor_activo_data(self, require_online=True):
        if not self.servidor_activo:
            return None
        data = self.conexiones.get(self.servidor_activo)
        if not data:
            return None
        if require_online and data.get("status") != "online":
            return None
        return data

    def _render_processes_tab(self):
        if not self.servidor_activo:
            self._render_empty_state("SIN DATOS", "Selecciona o crea una conexion de servidor.")
            return

        servidor = self._get_servidor_activo_data()
        if not servidor:
            self._render_empty_state("SERVIDOR DESCONECTADO", "El servidor activo no esta en linea.")
            return

        panel = PanelProcesos(self.content, servidor["cliente"])
        panel.pack(fill="both", expand=True)
        panel.iniciar_monitoreo()
        self.panel_dinamico = panel

    def _render_metrics_tab(self):
        if not self.servidor_activo:
            self._render_empty_state("SIN DATOS", "Selecciona o crea una conexion de servidor.")
            return

        servidor = self._get_servidor_activo_data()
        if not servidor:
            self._render_empty_state("SERVIDOR DESCONECTADO", "El servidor activo no esta en linea.")
            return

        panel = PanelRecursos(
            self.content,
            servidor["cliente"],
            callback_alerta=None,
            callback_metrica=self._actualizar_metrica_activa,
        )
        panel.pack(fill="both", expand=True)
        panel.iniciar_monitoreo()
        self.panel_dinamico = panel

    def _render_logs_tab(self):
        panel = PanelLogs(self.content)
        panel.pack(fill="both", expand=True)
        self.panel_dinamico = panel

    # ------------------------------
    # Tab Conexiones
    # ------------------------------
    def _render_connections_tab(self):
        container = ctk.CTkFrame(self.content, fg_color="transparent")
        container.pack(fill="both", expand=True)

        header = ctk.CTkFrame(container, fg_color="transparent")
        header.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            header,
            text="Gestor de conexiones",
            text_color=COLOR_TEXTO,
            font=ctk.CTkFont(size=16, weight="bold"),
        ).pack(side="left")

        ctk.CTkButton(
            header,
            text="Nueva conexion",
            fg_color=COLOR_PRIMARIO,
            hover_color=COLOR_HOVER,
            text_color="#FFFFFF",
            corner_radius=7,
            height=34,
            width=140,
            command=self.abrir_ventana_login,
        ).pack(side="right", padx=(8, 0))

        data_activa = self.conexiones.get(self.servidor_activo) if self.servidor_activo else None
        activa_online = bool(data_activa and data_activa.get("status") == "online")
        texto_accion_activa = "Desconectar activa" if activa_online else "Eliminar activa"

        ctk.CTkButton(
            header,
            text=texto_accion_activa,
            fg_color=COLOR_ERROR,
            hover_color=COLOR_ERROR_HOVER,
            text_color="#FFFFFF",
            corner_radius=7,
            height=34,
            width=156,
            command=self.cerrar_conexion_activa,
            state="normal" if data_activa else "disabled",
        ).pack(side="right")

        card = ctk.CTkFrame(container, fg_color=FONDO_PANEL, corner_radius=8)
        card.pack(fill="both", expand=True)

        rows = ctk.CTkScrollableFrame(card, fg_color="transparent")
        rows.pack(fill="both", expand=True, padx=14, pady=14)

        if not self.conexiones:
            ctk.CTkLabel(
                rows,
                text="SIN DATOS",
                text_color=COLOR_MUTED,
                font=ctk.CTkFont(size=22, weight="bold"),
            ).pack(pady=80)
            return

        for nombre, data in self.conexiones.items():
            online = data.get("status") == "online"
            estado_txt = "EN LINEA" if online else "DESCONECTADO"
            estado_color = COLOR_SUCCESS if online else COLOR_MUTED

            item = ctk.CTkFrame(rows, fg_color=COLOR_INPUT, corner_radius=8)
            item.pack(fill="x", pady=(0, 8))

            left = ctk.CTkFrame(item, fg_color="transparent")
            left.pack(side="left", fill="both", expand=True, padx=12, pady=10)

            ctk.CTkLabel(
                left,
                text=nombre,
                text_color=COLOR_TEXTO,
                font=ctk.CTkFont(size=13, weight="bold"),
            ).pack(anchor="w")
            ctk.CTkLabel(
                left,
                text=f"{data['ip']} | usuario {data['usuario']}",
                text_color=COLOR_SECUNDARIO,
                font=ctk.CTkFont(size=11),
            ).pack(anchor="w", pady=(2, 0))
            ctk.CTkLabel(
                left,
                text=estado_txt,
                text_color=estado_color,
                font=ctk.CTkFont(size=11, weight="bold"),
            ).pack(anchor="w", pady=(2, 0))

            right = ctk.CTkFrame(item, fg_color="transparent")
            right.pack(side="right", padx=12)

            ctk.CTkButton(
                right,
                text="Seleccionar",
                width=96,
                height=30,
                fg_color=COLOR_PRIMARIO,
                hover_color=COLOR_HOVER,
                text_color="#FFFFFF",
                corner_radius=7,
                command=lambda n=nombre: self._seleccionar_y_volver(n),
            ).pack(side="left", padx=(0, 8), pady=10)

            ctk.CTkButton(
                right,
                text="Desconectar" if online else "Eliminar",
                width=108,
                height=30,
                fg_color=COLOR_ERROR if online else "#334155",
                hover_color=COLOR_ERROR_HOVER if online else "#475569",
                text_color="#FFFFFF",
                corner_radius=7,
                command=lambda n=nombre: self.cerrar_conexion_por_nombre(n),
            ).pack(side="left", pady=10)

    def _seleccionar_y_volver(self, nombre):
        if nombre not in self.conexiones:
            return
        self.servidor_activo = nombre
        self.server_selector.set(nombre)
        self._actualizar_estado_acciones()
        self._actualizar_estado_footer()
        self.cambiar_tab("Servidores")

    # ------------------------------
    # Ciclo de conexiones
    # ------------------------------
    def _servidor_activo_esta_online(self):
        if not self.servidor_activo:
            return False
        data = self.conexiones.get(self.servidor_activo)
        return bool(data and data.get("status") == "online")

    def _actualizar_estado_acciones(self):
        self._set_actions_state(self._servidor_activo_esta_online())

    def _ciclo_supervision_conexiones(self):
        self._supervisor_after_id = None
        if not self.winfo_exists():
            return

        if self._supervisor_en_ejecucion:
            self._supervisor_after_id = self.after(600, self._ciclo_supervision_conexiones)
            return

        objetivos = [
            (nombre, data["cliente"])
            for nombre, data in list(self.conexiones.items())
            if data.get("status") == "online"
        ]

        if not objetivos:
            self._supervisor_after_id = self.after(self.INTERVALO_SUPERVISION_MS, self._ciclo_supervision_conexiones)
            return

        self._supervisor_en_ejecucion = True

        def tarea():
            resultados = []
            for nombre, cliente in objetivos:
                try:
                    datos = acciones.monitorear_recursos(cliente)
                    if not isinstance(datos, dict):
                        raise RuntimeError("Respuesta invalida del servidor.")
                    cpu = float(datos.get("cpu", 0.0))
                    ram = float(datos.get("memoria", 0.0))
                    resultados.append((nombre, True, cpu, ram, ""))
                except Exception as exc:
                    resultados.append((nombre, False, None, None, str(exc)))
            self._cola_supervision.put(resultados)

        threading.Thread(target=tarea, daemon=True).start()
        self.after(70, self._procesar_resultados_supervision_pendientes)

    def _procesar_resultados_supervision_pendientes(self):
        if not self.winfo_exists():
            return

        if not self._supervisor_en_ejecucion:
            return

        try:
            resultados = self._cola_supervision.get_nowait()
        except queue.Empty:
            self.after(70, self._procesar_resultados_supervision_pendientes)
            return

        self._aplicar_resultados_supervision(resultados)

    def _aplicar_resultados_supervision(self, resultados):
        if not self.winfo_exists():
            self._supervisor_en_ejecucion = False
            return

        hubo_cambio_estado = False
        hubo_actualizacion = False

        try:
            for nombre, ok, cpu, ram, error_msg in resultados:
                data = self.conexiones.get(nombre)
                if not data:
                    continue

                if ok:
                    estado_anterior = data.get("status")
                    data["status"] = "online"
                    data["cpu"] = cpu
                    data["ram"] = ram
                    self._evaluar_alertas_consumo(nombre, cpu, ram)
                    hubo_actualizacion = True

                    if estado_anterior != "online":
                        hubo_cambio_estado = True
                        registrar_log(f"Conexion restablecida: {nombre}")
                        self._notificar_sistema("Conexion restablecida", f"{nombre} esta en linea de nuevo.")
                    continue

                estaba_online = data.get("status", "online") == "online"
                data["status"] = "offline"
                data["cpu"] = None
                data["ram"] = None
                self._alertas_consumo[nombre] = {"cpu": False, "ram": False}
                hubo_actualizacion = True

                if estaba_online:
                    hubo_cambio_estado = True
                    detalle = error_msg.strip() if error_msg else "conexion cerrada."
                    registrar_log(f"Conexion perdida: {nombre} ({detalle})")
                    self._notificar_sistema("Conexion perdida", f"{nombre} se desconecto.")

            self._actualizar_estado_acciones()
            self._actualizar_estado_footer()

            if self.tab_actual == "Servidores":
                if hubo_cambio_estado or not self._actualizar_tabla_servidores_en_vivo():
                    self._actualizar_tabla_servidores()
            elif self.tab_actual == "Conexiones" and hubo_cambio_estado:
                self._render_tab_content()
            elif self.tab_actual in ("Procesos", "Metricas") and self.servidor_activo and not self._servidor_activo_esta_online():
                self.cambiar_tab(self.tab_actual, force=True)
        finally:
            self._supervisor_en_ejecucion = False
            if self.winfo_exists():
                self._supervisor_after_id = self.after(
                    self.INTERVALO_SUPERVISION_MS,
                    self._ciclo_supervision_conexiones,
                )

    def _evaluar_alertas_consumo(self, nombre, cpu, ram):
        estado = self._alertas_consumo.setdefault(nombre, {"cpu": False, "ram": False})

        if cpu >= self.UMBRAL_CPU_ALERTA and not estado["cpu"]:
            estado["cpu"] = True
            registrar_log(f"Alerta CPU alta en {nombre}: {cpu:.1f}%")
            self._notificar_sistema("Alerta CPU alta", f"{nombre}: CPU en {cpu:.1f}%")
        elif cpu < self.UMBRAL_CPU_ALERTA:
            estado["cpu"] = False

        if ram >= self.UMBRAL_RAM_ALERTA and not estado["ram"]:
            estado["ram"] = True
            registrar_log(f"Alerta Memoria alta en {nombre}: {ram:.1f}%")
            self._notificar_sistema("Alerta Memoria alta", f"{nombre}: RAM en {ram:.1f}%")
        elif ram < self.UMBRAL_RAM_ALERTA:
            estado["ram"] = False

    def _notificar_sistema(self, titulo, mensaje):
        tipo = "warning"
        titulo_norm = (titulo or "").lower()
        if "perdida" in titulo_norm or "error" in titulo_norm:
            tipo = "error"
        elif "restablecida" in titulo_norm or "ok" in titulo_norm or "exito" in titulo_norm:
            tipo = "success"
        self._mostrar_alerta_superior(titulo, mensaje, tipo=tipo)

    def _color_alerta_superior(self, tipo):
        if tipo == "error":
            return COLOR_ERROR, COLOR_ERROR_HOVER
        if tipo == "success":
            return COLOR_SUCCESS, COLOR_SUCCESS_HOVER
        return COLOR_ERROR, COLOR_ERROR_HOVER

    def _mostrar_alerta_superior(self, titulo, mensaje, tipo="warning", duracion_ms=6000):
        if not self.winfo_exists():
            return

        self._alerta_anim_token += 1
        self.update_idletasks()

        if self._alerta_superior_after_id:
            try:
                self.after_cancel(self._alerta_superior_after_id)
            except Exception:
                pass
            self._alerta_superior_after_id = None

        if self._alerta_superior is not None and self._alerta_superior.winfo_exists():
            try:
                self._alerta_superior.destroy()
            except Exception:
                pass
            self._alerta_superior = None

        color_bg, color_btn = self._color_alerta_superior(tipo)

        self._alerta_superior = ctk.CTkFrame(
            self.top_nav,
            fg_color=color_bg,
            corner_radius=10,
            border_width=1,
            border_color="#F8FAFC",
            width=self.ALERTA_ANCHO,
            height=self.ALERTA_ALTO,
        )
        x_visible, x_oculto = self._posicion_alerta_x()
        self._alerta_superior.place(x=x_oculto, y=self.ALERTA_Y, anchor="nw")
        self._alerta_superior.pack_propagate(False)
        self._alerta_superior.lift()

        ctk.CTkLabel(
            self._alerta_superior,
            text=f"{str(titulo)[:28]}: {str(mensaje)[:90]}",
            text_color="#FFFFFF",
            font=ctk.CTkFont(size=11, weight="bold"),
            anchor="w",
            justify="left",
            wraplength=245,
        ).pack(side="left", padx=(10, 6), pady=6)

        ctk.CTkButton(
            self._alerta_superior,
            text="OK",
            width=52,
            height=24,
            corner_radius=8,
            fg_color=color_btn,
            hover_color=color_btn,
            text_color="#FFFFFF",
            command=lambda: self._cerrar_alerta_superior(animado=True),
        ).pack(side="right", padx=(0, 8), pady=6)

        self._animar_alerta_superior(x_oculto, x_visible, duracion_ms=180)
        self._alerta_superior_after_id = self.after(
            duracion_ms,
            lambda: self._cerrar_alerta_superior(animado=True),
        )

    def _posicion_alerta_x(self):
        self.top_nav.update_idletasks()
        ancho_nav = max(self.top_nav.winfo_width(), 1120)
        x_visible = max(8, ancho_nav - self.ALERTA_ANCHO - self.ALERTA_MARGEN_DER)

        # Evita solaparse con los botones de acciones si la ventana se reduce.
        try:
            x_min = (
                self.top_inner.winfo_x()
                + self.actions_frame.winfo_x()
                + self.actions_frame.winfo_width()
                + 10
            )
            x_visible = max(x_visible, x_min)
        except Exception:
            pass

        x_oculto = ancho_nav + 24
        return x_visible, x_oculto

    def _animar_alerta_superior(self, x_inicio, x_fin, duracion_ms=180, on_finish=None):
        if self._alerta_superior is None or not self._alerta_superior.winfo_exists():
            return

        token = self._alerta_anim_token
        steps = 11
        intervalo = max(10, duracion_ms // steps)
        delta = (x_fin - x_inicio) / steps

        def step(i):
            if token != self._alerta_anim_token:
                return
            if self._alerta_superior is None or not self._alerta_superior.winfo_exists():
                return

            x_actual = int(x_inicio + delta * i)
            self._alerta_superior.place_configure(x=x_actual)

            if i >= steps:
                self._alerta_superior.place_configure(x=x_fin)
                if callable(on_finish):
                    on_finish()
                return

            self.after(intervalo, lambda: step(i + 1))

        step(0)

    def _cerrar_alerta_superior(self, animado=False):
        if self._alerta_superior_after_id:
            try:
                self.after_cancel(self._alerta_superior_after_id)
            except Exception:
                pass
            self._alerta_superior_after_id = None

        if self._alerta_superior is None:
            return

        if not animado:
            try:
                if self._alerta_superior.winfo_exists():
                    self._alerta_superior.destroy()
            except Exception:
                pass
            self._alerta_superior = None
            return

        if not self._alerta_superior.winfo_exists():
            self._alerta_superior = None
            return

        self._alerta_anim_token += 1
        x_actual = int(self._alerta_superior.place_info().get("x", self._posicion_alerta_x()[0]))
        token = self._alerta_anim_token

        def terminar():
            if token != self._alerta_anim_token:
                return
            if self._alerta_superior is not None:
                try:
                    if self._alerta_superior.winfo_exists():
                        self._alerta_superior.destroy()
                except Exception:
                    pass
                self._alerta_superior = None

        self._animar_alerta_superior(
            x_actual,
            self._posicion_alerta_x()[1],
            duracion_ms=170,
            on_finish=terminar,
        )

    def _nombre_conexion(self, ip, usuario):
        base = f"{usuario}@{ip}"
        nombre = base
        index = 2
        while nombre in self.conexiones:
            nombre = f"{base} ({index})"
            index += 1
        return nombre

    def nueva_pestana(self, cliente, ip, usuario, cert_path):
        nombre = self._nombre_conexion(ip, usuario)

        self.conexiones[nombre] = {
            "cliente": cliente,
            "ip": ip,
            "usuario": usuario,
            "cert_path": cert_path,
            "cpu": None,
            "ram": None,
            "status": "online",
            "connected_at": datetime.datetime.now(),
            "location": "Interna",
        }
        self._alertas_consumo[nombre] = {"cpu": False, "ram": False}

        self.servidor_activo = nombre
        self._actualizar_selector_servidores()
        self._actualizar_estado_footer()

        if self.tab_actual in ("Servidores", "Conexiones"):
            self._render_tab_content()

        if self._supervisor_after_id is None and not self._supervisor_en_ejecucion:
            self._supervisor_after_id = self.after(300, self._ciclo_supervision_conexiones)

    def _actualizar_selector_servidores(self):
        if self.conexiones:
            valores = list(self.conexiones.keys())
            self.server_selector.configure(values=valores)
            if self.servidor_activo not in self.conexiones:
                self.servidor_activo = valores[0]
            self.server_selector.set(self.servidor_activo)
            self._actualizar_estado_acciones()
        else:
            self.server_selector.configure(values=["Sin servidores"])
            self.server_selector.set("Sin servidores")
            self.servidor_activo = None
            self._set_actions_state(False)

    def _set_actions_state(self, enabled):
        state = "normal" if enabled else "disabled"
        text_color = "#FFFFFF" if enabled else COLOR_MUTED
        self.btn_start.configure(state=state, text_color=text_color)
        self.btn_kill.configure(state=state, text_color=text_color)
        self.btn_restart.configure(state=state, text_color=text_color)

    def _cambiar_servidor_activo(self, selected):
        if selected not in self.conexiones:
            return
        self.servidor_activo = selected
        self._actualizar_estado_acciones()
        self._actualizar_estado_footer()

        if self.tab_actual in ("Procesos", "Metricas"):
            self.cambiar_tab(self.tab_actual, force=True)
        elif self.tab_actual == "Servidores":
            self._actualizar_tabla_servidores()
        elif self.tab_actual == "Conexiones":
            self._render_tab_content()

    def cerrar_conexion_activa(self):
        if not self.servidor_activo:
            return
        self.cerrar_conexion_por_nombre(self.servidor_activo)

    def cerrar_conexion_por_nombre(self, nombre):
        data = self.conexiones.pop(nombre, None)
        if not data:
            return
        self._alertas_consumo.pop(nombre, None)

        try:
            data["cliente"].desconectar()
        except Exception:
            pass

        if self.servidor_activo == nombre:
            self.servidor_activo = next(iter(self.conexiones), None)

        self._actualizar_selector_servidores()
        self._actualizar_estado_footer()
        self._render_tab_content()

    # ------------------------------
    # Acciones
    # ------------------------------
    def abrir_ventana_login(self):
        self._mostrar_modal(
            lambda parent, on_close: VentanaLogin(
                parent,
                self.nueva_pestana,
                on_close,
                self.mostrar_mensaje_modal,
            ),
            ancho=520,
            alto=500,
        )

    def _obtener_servidor_activo_para_accion(self):
        if not self.servidor_activo:
            return None, "sin_servidor"

        servidor = self._get_servidor_activo_data(require_online=False)
        if not servidor:
            return None, "sin_servidor"

        if servidor.get("status") != "online":
            self.mostrar_mensaje_modal(
                "Servidor desconectado",
                "El servidor activo no esta en linea. Eliminalo o vuelve a conectarlo.",
                tipo="error",
            )
            return None, "offline"

        return servidor, ""

    def abrir_ventana_iniciar(self):
        servidor, motivo = self._obtener_servidor_activo_para_accion()
        if not servidor:
            if motivo == "sin_servidor":
                self.abrir_ventana_login()
            return

        self._mostrar_modal(
            lambda parent, on_close: VentanaIniciar(
                parent,
                servidor["cliente"],
                on_close,
                self.mostrar_mensaje_modal,
            ),
            ancho=500,
            alto=320,
        )

    def abrir_ventana_matar(self):
        servidor, motivo = self._obtener_servidor_activo_para_accion()
        if not servidor:
            if motivo == "sin_servidor":
                self.abrir_ventana_login()
            return

        self._mostrar_modal(
            lambda parent, on_close: VentanaMatar(
                parent,
                servidor["cliente"],
                on_close,
                self.mostrar_mensaje_modal,
            ),
            ancho=480,
            alto=300,
        )

    def reiniciar_vista(self):
        self.cambiar_tab(self.tab_actual, force=True)

    def _actualizar_metrica_activa(self, cpu, ram):
        data = self._get_servidor_activo_data(require_online=False)
        if not data:
            return

        data["cpu"] = cpu
        data["ram"] = ram

        if self.tab_actual == "Servidores":
            self._actualizar_tabla_servidores()

    def mostrar_alerta(self, titulo, mensaje, tipo="warning"):
        self.mostrar_mensaje_modal(titulo, mensaje, tipo=tipo)

    def mostrar_mensaje_modal(self, titulo, mensaje, tipo="warning"):
        self._mostrar_o_reemplazar_modal(
            lambda parent, on_close: MensajePersonalizado(
                parent,
                titulo,
                mensaje,
                tipo=tipo,
                on_close=on_close,
            ),
            ancho=500,
            alto=300,
        )

    def _mostrar_o_reemplazar_modal(self, constructor_formulario, ancho, alto):
        if self.modal_overlay is None:
            self._mostrar_modal(constructor_formulario, ancho, alto)
        else:
            self._reemplazar_contenido_modal(constructor_formulario, ancho, alto)

    def _mostrar_modal(self, constructor_formulario, ancho, alto):
        if self.modal_overlay is not None:
            return

        self._modal_anim_token += 1

        self.modal_overlay = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.modal_overlay.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.modal_overlay.lift()

        self.modal_canvas = tk.Canvas(
            self.modal_overlay,
            highlightthickness=0,
            bd=0,
            bg="#0A0C10",
        )
        self.modal_canvas.place(relx=0, rely=0, relwidth=1, relheight=1)
        self.modal_rect = self.modal_canvas.create_rectangle(
            0,
            0,
            1,
            1,
            fill="#05070B",
            outline="",
            stipple="gray50",
        )
        self.modal_canvas.bind("<Configure>", self._actualizar_fondo_modal)

        self.modal_contenedor = ctk.CTkFrame(
            self.modal_overlay,
            fg_color=FONDO_PANEL,
            corner_radius=14,
            border_width=1,
            border_color=COLOR_SEPARADOR,
            width=ancho,
            height=alto,
        )
        self.modal_contenedor.place(relx=0.5, rely=0.56, anchor="center")

        self.modal_form = constructor_formulario(self.modal_contenedor, self._cerrar_modal)
        self.modal_form.pack(expand=True, fill="both", padx=16, pady=16)
        self._animar_modal_entrada(rely_inicio=0.56, rely_fin=0.5)

        if hasattr(self.modal_form, "focus_principal"):
            self.after(50, self.modal_form.focus_principal)

        self.bind("<Escape>", self._cerrar_modal_desde_tecla)

    def _reemplazar_contenido_modal(self, constructor_formulario, ancho, alto):
        if self.modal_overlay is None or self.modal_contenedor is None:
            self._mostrar_modal(constructor_formulario, ancho, alto)
            return

        if self.modal_form is not None:
            self.modal_form.destroy()
            self.modal_form = None

        self.modal_contenedor.configure(width=ancho, height=alto)
        self.modal_form = constructor_formulario(self.modal_contenedor, self._cerrar_modal)
        self.modal_form.pack(expand=True, fill="both", padx=16, pady=16)
        self.modal_contenedor.place_configure(relx=0.5, rely=0.53, anchor="center")
        self._animar_modal_entrada(rely_inicio=0.53, rely_fin=0.5)

        if hasattr(self.modal_form, "focus_principal"):
            self.after(50, self.modal_form.focus_principal)

    def _animar_modal_entrada(self, rely_inicio=0.56, rely_fin=0.5):
        if self.modal_contenedor is None or not self.modal_contenedor.winfo_exists():
            return

        self._modal_anim_token += 1
        token = self._modal_anim_token
        steps = 14
        intervalo = 12

        def step(i):
            if token != self._modal_anim_token:
                return
            if self.modal_contenedor is None or not self.modal_contenedor.winfo_exists():
                return

            progreso = min(1.0, i / steps)
            eased = 1 - (1 - progreso) ** 3
            rely_actual = rely_inicio + (rely_fin - rely_inicio) * eased
            self.modal_contenedor.place_configure(relx=0.5, rely=rely_actual, anchor="center")

            if i >= steps:
                self.modal_contenedor.place_configure(relx=0.5, rely=rely_fin, anchor="center")
                return

            self.after(intervalo, lambda: step(i + 1))

        step(0)

    def _actualizar_fondo_modal(self, event):
        if self.modal_canvas is None or self.modal_rect is None:
            return
        self.modal_canvas.coords(self.modal_rect, 0, 0, event.width, event.height)

    def _cerrar_modal_desde_tecla(self, event):
        _ = event
        self._cerrar_modal()

    def _cerrar_modal(self):
        self._modal_anim_token += 1
        self.unbind("<Escape>")
        if self.modal_overlay is not None:
            self.modal_overlay.destroy()

        self.modal_overlay = None
        self.modal_canvas = None
        self.modal_rect = None
        self.modal_contenedor = None
        self.modal_form = None

    # ------------------------------
    # Footer y cierre
    # ------------------------------
    def _crear_footer(self):
        ctk.CTkFrame(self, fg_color=COLOR_SEPARADOR, height=1).pack(fill="x", side="bottom")
        self.footer = ctk.CTkFrame(self, fg_color=FONDO_PANEL, height=32, corner_radius=0)
        self.footer.pack(fill="x", side="bottom")
        self.footer.pack_propagate(False)

        self.footer_text = ctk.CTkLabel(
            self.footer,
            text="Sin conexiones activas",
            text_color=COLOR_MUTED,
            anchor="w",
            font=ctk.CTkFont(size=11),
        )
        self.footer_text.pack(fill="x", padx=14)

    def _actualizar_estado_footer(self):
        total = len(self.conexiones)
        if total == 0:
            self.footer_text.configure(text="Sin conexiones activas", text_color=COLOR_MUTED)
            return

        online = sum(1 for data in self.conexiones.values() if data.get("status") == "online")
        activo = self.servidor_activo or "--"
        activo_data = self.conexiones.get(activo) if self.servidor_activo else None
        estado_activo = "EN LINEA" if activo_data and activo_data.get("status") == "online" else "DESCONECTADO"

        self.footer_text.configure(
            text=f"Servidor activo: {activo} ({estado_activo}) | Conexiones en linea: {online}/{total}",
            text_color=COLOR_SECUNDARIO if online > 0 else COLOR_MUTED,
        )

    def cerrar_aplicacion(self):
        self._cerrar_alerta_superior()

        if self._supervisor_after_id:
            try:
                self.after_cancel(self._supervisor_after_id)
            except Exception:
                pass
            self._supervisor_after_id = None
        self._supervisor_en_ejecucion = False

        for data in list(self.conexiones.values()):
            try:
                data["cliente"].desconectar()
            except Exception:
                pass
        self.destroy()
