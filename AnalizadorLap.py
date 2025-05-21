import psutil

def listar_conexiones():
    for conn in psutil.net_connections(kind='inet'):
        print(f"PID: {conn.pid}, IP: {conn.raddr}, Estado: {conn.status}")

listar_conexiones()
