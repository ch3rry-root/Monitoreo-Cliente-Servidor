# Funciones para cada acción del cliente

def listar_procesos(cliente):
    """Solicita la lista de procesos al servidor."""
    return cliente.enviar({"accion": "LISTAR"})

def monitorear_recursos(cliente):
    """Solicita el monitoreo de recursos al servidor."""
    return cliente.enviar({"accion": "MONITOREAR"})

def iniciar_proceso(cliente, comando):
    """Envía una orden para iniciar un proceso."""
    return cliente.enviar({
        "accion": "INICIAR",
        "comando": comando
    })

def terminar_proceso(cliente, pid):
    """Envía una orden para terminar un proceso por PID."""
    return cliente.enviar({
        "accion": "TERMINAR",
        "pid": pid
    })