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


