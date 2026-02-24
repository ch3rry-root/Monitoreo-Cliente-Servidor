🖥️ Sistema de Monitoreo Distribuido

Aplicación cliente-servidor para la gestión y monitoreo remoto de procesos en tiempo real, con comunicación segura mediante TLS, interfaz gráfica moderna basada en CustomTkinter y soporte para múltiples conexiones simultáneas usando pestañas independientes.

✨ Características principales

🔐 Comunicación segura
Conexión TLS 1.2+ con certificados autofirmados y verificación obligatoria del certificado del servidor.

🔑 Autenticación robusta
Las contraseñas se transmiten hasheadas mediante SHA-256.

🗂️ Múltiples servidores
Conexión simultánea a varios servidores, cada uno en su propia pestaña independiente.

📊 Monitoreo en tiempo real
Tabla de procesos (PID, nombre, CPU%, memoria%) y gráficos dinámicos actualizados cada 2 segundos.

⚙️ Gestión remota de procesos

Iniciar comandos remotos

Terminar procesos mediante PID

🚨 Alertas inteligentes
Notificaciones cuando:

CPU > 90%

Memoria > 95%
(sin repeticiones molestas).

📝 Registro de actividades
Login, acciones y errores almacenados localmente y visibles desde el visor de logs

🧹 Cierre limpio
Detención automática de monitoreo al cerrar pestañas o la aplicación.

📋 Requisitos previos
General

Python 3.8+

Servidor

Linux (recomendado Ubuntu)

Puerto 5000 abierto

Cliente

Windows

Archivo de certificado del servidor (server.crt)

🚀 Instalación y configuración

1️⃣ Clonar repositorio
git clone https://github.com/tu-usuario/sistema-monitoreo-distribuido.git
cd sistema-monitoreo-distribuido
2️⃣ Instalar dependencias
pip install -r requirements.txt
3️⃣ Generar certificados autofirmados (Servidor)
openssl req -x509 -newkey rsa:4096 -keyout server.key -out server.crt -days 365 -nodes
4️⃣ Configurar servidor

Copia:

server.crt
server.key

al mismo directorio que servidor_seguro.py.

(Opcional) Cambia credenciales por defecto:

USUARIO_VALIDO = "admin"
PASSWORD_HASH = "..."

Ejecutar servidor:

python servidor_seguro.py
5️⃣ Ejecutar cliente
python -m cliente.main
