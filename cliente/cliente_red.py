import socket
import ssl
import json
import hashlib

class ClienteSeguro:
    def __init__(self):
        self.conn = None

    # ======================
    # RECIBIR EXACTAMENTE N BYTES
    # ======================
    def recvall(self, n):
        data = b""
        while len(data) < n:
            packet = self.conn.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data

    # ======================
    # ENVIAR JSON
    # ======================
    def enviar_json(self, obj):
        data = json.dumps(obj).encode()
        length = len(data).to_bytes(4, "big")
        self.conn.sendall(length + data)

    # ======================
    # RECIBIR JSON
    # ======================
    def recibir_json(self):
        raw_len = self.recvall(4)
        if not raw_len:
            return None

        msg_len = int.from_bytes(raw_len, "big")
        data = self.recvall(msg_len)
        return json.loads(data.decode())

    # ======================
    # CONECTAR (LOGIN)
    # ======================
    def conectar(self, ip, usuario, password):
        context = ssl.create_default_context()
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn = context.wrap_socket(sock)
        self.conn.connect((ip, 5000))  # Puerto hardcodeado (se puede mejorar)

        password_hash = hashlib.sha256(password.encode()).hexdigest()

        auth_msg = {
            "accion": "AUTENTICAR",
            "usuario": usuario,
            "password_hash": password_hash
        }

        self.enviar_json(auth_msg)
        respuesta = self.recibir_json()

        if respuesta and respuesta.get("estado") == "ok":
            return {"status": "ok"}
        else:
            return {"status": "error"}

    # ======================
    # API GENERAL
    # ======================
    def enviar(self, data):
        self.enviar_json(data)
        return self.recibir_json()