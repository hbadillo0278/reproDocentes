import psutil

# Lista de nombres de procesos sospechosos (puedes ajustarla según tus necesidades)
procesos_sospechosos = [
    "ms-teams.exe", "Microsoft.SharePoint.exe", "svchost.exe", "msedgewebview2.exe",
    "Code.exe", "SearchHost.exe", "chrome.exe", "OneDrive.exe", "explorer.exe",
    "Copilot.exe"
]

def matar_procesos_sospechosos(procesos):
    for proceso in psutil.process_iter(attrs=['pid', 'name']):
        try:
            if proceso.info['name'] in procesos:
                print(f"Finalizando {proceso.info['name']} con PID {proceso.info['pid']}")
                psutil.Process(proceso.info['pid']).terminate()  # Terminar proceso
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass

# Ejecutar la función
matar_procesos_sospechosos(procesos_sospechosos)
