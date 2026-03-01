
import datetime
import os
from pathlib import Path

LOG_DIR = Path.home() / ".monitoreo"
LOG_FILE = LOG_DIR / "actividades.log"

def asegurar_directorio():
    LOG_DIR.mkdir(exist_ok=True)

def registrar_log(mensaje: str):
    asegurar_directorio()
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(LOG_FILE, "a", encoding="utf-8") as f:
        f.write(f"{timestamp}: {mensaje}\n")

def obtener_ultimos(n=50):
    asegurar_directorio()
    if not LOG_FILE.exists():
        return []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        lineas = f.readlines()
    return lineas[-n:]