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

def recvall(conn, n):
    data = b""
    while len(data) < n:
        packet = conn.recv(n - len(data))
        if not packet:
            return None
        data += packet
    return data


def recibir_json(conn):
    raw_len = recvall(conn, 4)
    if not raw_len:
        return None

    msg_len = int.from_bytes(raw_len, "big")
    data = recvall(conn, msg_len)

    return json.loads(data.decode())


def enviar_json(conn, obj):
    data = json.dumps(obj).encode()
    conn.sendall(len(data).to_bytes(4, "big") + data)


def listar_procesos():
    procesos = []
    for proc in psutil.process_iter(
        ['pid', 'name', 'cpu_percent', 'memory_percent']
    ):
        procesos.append(proc.info)
    return procesos

def iniciar_proceso(comando):

    if not comando:
        return {"estado": "error", "mensaje": "Comando vacío"}

    if shutil.which(comando.split()[0]) is None:
        return {"estado": "error", "mensaje": "Comando no válido"}

    try:
        proceso = subprocess.Popen(
            comando.split(),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL
        )
        return {"estado": "ok", "pid": proceso.pid}

    except Exception as e:
        return {"estado": "error", "mensaje": str(e)}

def terminar_proceso(pid):
    try:
        proceso = psutil.Process(int(pid))
        proceso.terminate()
        return {"estado": "ok", "mensaje": f"Proceso {pid} terminado"}
    except Exception as e:
        return {"estado": "error", "mensaje": str(e)}


def monitorear_sistema():
    return {
        "cpu": psutil.cpu_percent(interval=None),
        "memoria": psutil.virtual_memory().percent
    }

def manejar_cliente(connstream, addr):

    print(f"[+] Cliente conectado: {addr}")
    autenticado = False

    try:
        while True:

            mensaje = recibir_json(connstream)
            if not mensaje:
                break

            accion = mensaje.get("accion")

            if accion == "AUTENTICAR":

                usuario = mensaje.get("usuario")
                password_hash = mensaje.get("password_hash")

                if usuario == USUARIO_VALIDO and password_hash == PASSWORD_HASH:
                    autenticado = True
                    respuesta = {"estado": "ok", "mensaje": "Autenticado"}
                else:
                    respuesta = {"estado": "error", "mensaje": "Credenciales inválidas"}

                enviar_json(connstream, respuesta)
                continue
            if not autenticado:
                enviar_json(connstream,
                            {"estado": "error", "mensaje": "No autenticado"})
                continue


            if accion == "LISTAR":
                respuesta = listar_procesos()
            elif accion == "INICIAR":
                respuesta = iniciar_proceso(mensaje.get("comando"))
            elif accion == "TERMINAR":
                respuesta = terminar_proceso(mensaje.get("pid"))
            elif accion == "MONITOREAR":
                respuesta = monitorear_sistema()
            else:
                respuesta = {
                    "estado": "error",
                    "mensaje": "Acción desconocida"
                }
            enviar_json(connstream, respuesta)

    except Exception as e:
        print(f"[!] Error con cliente {addr}: {e}")

    finally:
        connstream.close()
        print(f"[-] Cliente desconectado: {addr}")

def iniciar_servidor():

    context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
    context.load_cert_chain(
        certfile="server.crt",
        keyfile="server.key"
    )

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((HOST, PORT))
    sock.listen(5)

    print(f"[SERVIDOR SEGURO] Escuchando en puerto {PORT}")

    while True:

        cliente, addr = sock.accept()

        try:
            connstream = context.wrap_socket(cliente, server_side=True)
        except ssl.SSLError:
            print("[!] Conexion sin TLS detectada")
            cliente.close()
            continue

        thread = threading.Thread(
            target=manejar_cliente,
            args=(connstream, addr),
            daemon=True
        )
        thread.start()


if __name__ == "__main__":
    iniciar_servidor()