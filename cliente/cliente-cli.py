import socket
import ssl
import json
import hashlib

PORT = 5000

USERNAME = "admin"
PASSWORD = "admin123"


def conectar(server_ip):
    context = ssl.create_default_context()
    context.check_hostname = False
    context.verify_mode = ssl.CERT_NONE  # Solo para pruebas

    sock = socket.create_connection((server_ip, PORT))
    conn = context.wrap_socket(sock, server_hostname=server_ip)
    return conn


def autenticar(conn):
    password_hash = hashlib.sha256(PASSWORD.encode()).hexdigest()

    mensaje = {
        "action": "AUTH",
        "username": USERNAME,
        "password_hash": password_hash
    }

    conn.sendall(json.dumps(mensaje).encode())
    respuesta = json.loads(conn.recv(8192).decode())

    if respuesta.get("status") != "ok":
        print("Autenticación falló")
        print(respuesta)
        return False

    print("Autenticación exitosa")
    return True


def enviar_comando(conn, comando):
    conn.sendall(json.dumps(comando).encode())
    respuesta = json.loads(conn.recv(65536).decode())
    return respuesta


def menu():
    print("\n===== CLIENTE SEGURO =====")
    print("1 - Listar procesos")
    print("2 - Iniciar proceso")
    print("3 - Matar proceso")
    print("4 - Monitor sistema")
    print("0 - Salir")


def main():
    print("===== CONEXIÓN AL SERVIDOR =====")
    server_ip = input("Ingrese IP o DNS del servidor: ")

    try:
        conn = conectar(server_ip)
        print("Conectado al servidor")
    except Exception as e:
        print("No se pudo conectar al servidor:", e)
        return

    if not autenticar(conn):
        conn.close()
        return

    while True:
        menu()
        opcion = input("Seleccione opción: ")

        if opcion == "1":
            respuesta = enviar_comando(conn, {"action": "LIST"})
            print(json.dumps(respuesta[:10], indent=2))

        elif opcion == "2":
            cmd = input("Comando a ejecutar (ej: sleep 30): ")
            respuesta = enviar_comando(conn, {
                "action": "START",
                "command": cmd
            })
            print(respuesta)

        elif opcion == "3":
            pid = input("PID a matar: ")
            respuesta = enviar_comando(conn, {
                "action": "KILL",
                "pid": pid
            })
            print(respuesta)

        elif opcion == "4":
            respuesta = enviar_comando(conn, {"action": "MONITOR_SYSTEM"})
            print(respuesta)

        elif opcion == "0":
            print("Saliendo...")
            break

        else:
            print("Opción inválida")

    conn.close()


if __name__ == "__main__":
    main()
