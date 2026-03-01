import hashlib
import json
import socket
import ssl
import threading


class ClienteSeguro:
    def __init__(self):
        self.conn = None
        self._io_lock = threading.Lock()

    def recvall(self, n):
        data = b""
        while len(data) < n:
            packet = self.conn.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data

    def enviar_json(self, obj):
        data = json.dumps(obj).encode()
        length = len(data).to_bytes(4, "big")
        self.conn.sendall(length + data)

    def recibir_json(self):
        raw_len = self.recvall(4)
        if not raw_len:
            return None
        msg_len = int.from_bytes(raw_len, "big")
        data = self.recvall(msg_len)
        return json.loads(data.decode())

    def conectar(self, ip, usuario, password, cert_path):
        context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
        context.load_verify_locations(cafile=cert_path)
        context.check_hostname = False
        context.verify_mode = ssl.CERT_REQUIRED
        context.minimum_version = ssl.TLSVersion.TLSv1_2

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.conn = context.wrap_socket(sock, server_hostname=ip)
        self.conn.connect((ip, 5000))
        self.conn.settimeout(5)

        password_hash = hashlib.sha256(password.encode()).hexdigest()
        auth_msg = {
            "accion": "AUTENTICAR",
            "usuario": usuario,
            "password_hash": password_hash,
        }
        with self._io_lock:
            self.enviar_json(auth_msg)
            respuesta = self.recibir_json()

        if respuesta and respuesta.get("estado") == "ok":
            return {"status": "ok"}
        return {"status": "error"}

    def enviar(self, data):
        with self._io_lock:
            if not self.conn:
                raise ConnectionError("No hay conexion activa con el servidor.")
            self.enviar_json(data)
            respuesta = self.recibir_json()
            if respuesta is None:
                raise ConnectionError("El servidor cerro la conexion.")
            return respuesta

    def desconectar(self):
        """Cierra la conexion activa si existe."""
        with self._io_lock:
            if self.conn:
                try:
                    self.conn.close()
                except Exception:
                    pass
                self.conn = None
