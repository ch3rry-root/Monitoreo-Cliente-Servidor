import threading
from tkinter import ttk

import customtkinter as ctk

from cliente import acciones
from cliente.constantes import (
    COLOR_INPUT,
    COLOR_MUTED,
    COLOR_PRIMARIO,
    COLOR_SEPARADOR,
    COLOR_TEXTO,
    FONDO_PANEL,
)


class PanelProcesos(ctk.CTkFrame):
    _style_inicializado = False

    def __init__(self, parent, cliente):
        super().__init__(parent, fg_color="transparent")
        self.cliente = cliente
        self.monitoreando = False
        self.after_id = None
        self._destruido = False

        self._crear_layout()
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

    def _crear_layout(self):
        top = ctk.CTkFrame(self, fg_color="transparent")
        top.pack(fill="x", pady=(0, 10))

        ctk.CTkLabel(
            top,
            text="VISTA DE PROCESOS",
            text_color=COLOR_TEXTO,
            font=ctk.CTkFont(size=15, weight="bold"),
        ).pack(side="left")

        self.lbl_total = ctk.CTkLabel(
            top,
            text="0 filas",
            text_color=COLOR_MUTED,
            font=ctk.CTkFont(size=12),
        )
        self.lbl_total.pack(side="right")

        shell = ctk.CTkFrame(self, fg_color=FONDO_PANEL, corner_radius=8)
        shell.pack(fill="both", expand=True)
        tabla_shell = ctk.CTkFrame(shell, fg_color=COLOR_INPUT, corner_radius=6)
        tabla_shell.pack(fill="both", expand=True, padx=12, pady=12)

        self._configurar_estilo_tabla()

        columnas = ("pid", "nombre", "cpu", "memoria")
        self.tabla = ttk.Treeview(
            tabla_shell,
            columns=columnas,
            show="headings",
            style="Procesos.Treeview",
            selectmode="browse",
            takefocus=False,
        )

        self.tabla.heading("pid", text="PID")
        self.tabla.heading("nombre", text="NOMBRE")
        self.tabla.heading("cpu", text="CPU %")
        self.tabla.heading("memoria", text="MEMORIA %")

        self.tabla.column("pid", width=100, anchor="center", stretch=False)
        self.tabla.column("nombre", width=640, anchor="w", stretch=True)
        self.tabla.column("cpu", width=110, anchor="center", stretch=False)
        self.tabla.column("memoria", width=130, anchor="center", stretch=False)

        scroll = ctk.CTkScrollbar(
            tabla_shell,
            orientation="vertical",
            command=self.tabla.yview,
            fg_color="transparent",
            button_color=COLOR_SEPARADOR,
            button_hover_color=COLOR_MUTED,
            width=12,
            corner_radius=10,
        )
        self.tabla.configure(yscrollcommand=scroll.set)

        self.tabla.pack(side="left", fill="both", expand=True, padx=(10, 6), pady=10)
        scroll.pack(side="right", fill="y", padx=(0, 8), pady=10)

    @classmethod
    def _configurar_estilo_tabla(cls):
        if cls._style_inicializado:
            return

        style = ttk.Style()
        if "clam" in style.theme_names():
            style.theme_use("clam")

        style.configure(
            "Procesos.Treeview",
            background=COLOR_INPUT,
            foreground=COLOR_TEXTO,
            fieldbackground=COLOR_INPUT,
            rowheight=30,
            borderwidth=0,
            relief="flat",
            font=("Segoe UI", 10),
            lightcolor=COLOR_INPUT,
            darkcolor=COLOR_INPUT,
            bordercolor=COLOR_INPUT,
            selectborderwidth=0,
        )
        style.configure(
            "Procesos.Treeview.Heading",
            background=FONDO_PANEL,
            foreground=COLOR_MUTED,
            borderwidth=0,
            relief="flat",
            font=("Segoe UI", 10, "bold"),
            lightcolor=FONDO_PANEL,
            darkcolor=FONDO_PANEL,
            bordercolor=FONDO_PANEL,
        )
        style.map(
            "Procesos.Treeview",
            background=[("selected", COLOR_PRIMARIO)],
            foreground=[("selected", "#0C111B")],
        )
        style.map(
            "Procesos.Treeview.Heading",
            background=[("active", FONDO_PANEL), ("pressed", FONDO_PANEL)],
            foreground=[("active", COLOR_MUTED), ("pressed", COLOR_MUTED)],
        )
        style.layout("Procesos.Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

        cls._style_inicializado = True

    def actualizar_tabla(self, datos):
        if not self._esta_vivo():
            return

        children = self.tabla.get_children()
        if children:
            self.tabla.delete(*children)

        if isinstance(datos, dict) and "error" in datos:
            self.tabla.insert("", "end", values=("ERR", datos["error"], "", ""))
            self.lbl_total.configure(text="ERROR")
            return

        if not isinstance(datos, list):
            self.tabla.insert("", "end", values=("ERR", "Formato de datos invalido", "", ""))
            self.lbl_total.configure(text="ERROR")
            return

        if not datos:
            self.lbl_total.configure(text="0 filas")
            return

        for i, proc in enumerate(datos):
            pid = proc.get("pid", "")
            nombre = proc.get("name", "")
            cpu = proc.get("cpu_percent", 0)
            memoria = proc.get("memory_percent", 0)
            tag = "par" if i % 2 == 0 else "impar"

            self.tabla.insert(
                "",
                "end",
                values=(
                    str(pid),
                    str(nombre),
                    f"{cpu:.2f}" if cpu is not None else "N/D",
                    f"{memoria:.2f}" if memoria is not None else "N/D",
                ),
                tags=(tag,),
            )

        self.tabla.tag_configure("par", background=COLOR_INPUT)
        self.tabla.tag_configure("impar", background="#171A22")
        self.lbl_total.configure(text=f"{len(datos)} filas")

    def obtener_procesos_periodicamente(self):
        if not self.monitoreando or not self._esta_vivo():
            return

        def tarea():
            if not self.monitoreando or not self._esta_vivo():
                return

            try:
                datos = acciones.listar_procesos(self.cliente)
                self._safe_after(0, lambda datos=datos: self.actualizar_tabla(datos))
            except Exception as e:
                self._safe_after(0, lambda e=e: self.actualizar_tabla({"error": str(e)}))
            finally:
                if self.monitoreando and self._esta_vivo():
                    self.after_id = self._safe_after(2000, self.obtener_procesos_periodicamente)

        threading.Thread(target=tarea, daemon=True).start()

    def iniciar_monitoreo(self):
        if self.monitoreando:
            return
        self.monitoreando = True
        self.obtener_procesos_periodicamente()

    def detener(self):
        self.monitoreando = False
        if self.after_id:
            try:
                self.after_cancel(self.after_id)
            except Exception:
                pass
            self.after_id = None
