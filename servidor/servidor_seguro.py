import socket
import ssl
import threading
import json
import psutil
import subprocess
import shutil
import hashlib

HOST = "0.0.0.0"
PORT = 5000

USUARIO_VALIDO = "admin"
PASSWORD_HASH = hashlib.sha256("admin123".encode()).hexdigest()


# =========================
# FUNCIONES UTILIDAD
# =========================

def listar_procesos():
    procesos = []
    for proc in psutil.process_iter(['pid', 'name', 'cpu_percent', 'memory_percent']):
        procesos.append(proc.info)
    return procesos


def iniciar_proceso(comando):
    if not comando:
        return {"status": "error", "message": "Comando vacío"}

    if shutil.which(comando.split()[0]) is None:
        return {"status": "error", "message": "Comando no válido"}

    try:
        proceso = subprocess.Popen(
            comando.split(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return {"status": "ok", "pid": proceso.pid}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def matar_proceso(pid):
    try:
        proceso = psutil.Process(int(pid))
        proceso.terminate()
        return {"status": "ok", "message": f"Proceso {pid} terminado"}
    except Exception as e:
        return {"status": "error", "message": str(e)}


def monitor_sistema():
    return {
        "cpu": psutil.cpu_percent(interval=1),
        "memoria": psutil.virtual_memory().percent
    }


# =========================
# MANEJO CLIENTE
# =========================

def manejar_cliente(connstream, addr):
    print(f"[+] Cliente conectado: {addr}")
    autenticado = False

    try:
        while True:
            data = connstream.recv(8192)
            if not data:
                break

            mensaje = json.loads(data.decode())
            accion = mensaje.get("action")

            # ======================
            # AUTENTICACION
            # ======================
            if accion == "AUTH":
                usuario = mensaje.get("username")
                password_hash = mensaje.get("password_hash")

                if usuario == USUARIO_VALIDO and password_hash == PASSWORD_HASH:
                    autenticado = True
                    respuesta = {"status": "ok", "message": "Autenticado"}
                else:
                    respuesta = {"status": "error", "message": "Credenciales inválidas"}

                connstream.sendall(json.dumps(respuesta).encode())
                continue

            # ======================
            # BLOQUEO SI NO AUTH
            # ======================
            if not autenticado:
                respuesta = {"status": "error", "message": "No autenticado"}
                connstream.sendall(json.dumps(respuesta).encode())
                continue

            # ======================
            # ACCIONES
            # ======================

            if accion == "LIST":
                respuesta = listar_procesos()

            elif accion == "START":
                respuesta = iniciar_proceso(mensaje.get("command"))

            elif accion == "KILL":
                respuesta = matar_proceso(mensaje.get("pid"))

            elif accion == "MONITOR_SYSTEM":
                respuesta = monitor_sistema()

            else:
                respuesta = {"status": "error", "message": "Acción desconocida"}

            connstream.sendall(json.dumps(respuesta).encode())

    except Exception as e:
        print(f"[!] Error con cliente {addr}: {e}")

    finally:
        connstream.close()
        print(f"[-] Cliente desconectado: {addr}")


# =========================
# SERVIDOR TLS
# =========================

def iniciar_servidor():
    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(certfile="server.crt", keyfile="server.key")

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen(5)

    print(f"[SERVIDOR SEGURO] Escuchando en puerto {PORT} (TLS activado)")

    while True:
        cliente, addr = sock.accept()

        try:
            connstream = context.wrap_socket(cliente, server_side=True)
        except ssl.SSLError:
            print("[!] Intento de conexión sin TLS detectado")
            cliente.close()
            continue

        thread = threading.Thread(
            target=manejar_cliente,
            args=(connstream, addr)
        )
        thread.start()

if __name__ == "__main__":
    iniciar_servidor()
