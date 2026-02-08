import socket
import threading
import time
import platform
import psutil
import uuid

# Porta usada para broadcast de descoberta
BROADCAST_PORT = 50000

# Endereço de broadcast (envia para toda a LAN)
BROADCAST_ADDR = "255.255.255.255"

# Intervalo entre os HELLO (em segundos)
HELLO_INTERVAL = 5


class Cliente:
    def __init__(self):
        # Define dinamicamente uma porta TCP livre
        self.tcp_port = self._get_free_port()

        # Controle de execução do cliente
        self.running = True

    # -------------------------------------------------
    # Obtém uma porta TCP livre no sistema
    # -------------------------------------------------
    def _get_free_port(self):
        s = socket.socket()
        s.bind(("", 0))               # Porta 0 = SO escolhe uma porta livre
        port = s.getsockname()[1]     # Obtém a porta escolhida
        s.close()
        return port

    # -------------------------------------------------
    # Coleta todas as métricas exigidas no trabalho
    # -------------------------------------------------
    def coletar_dados(self):
        interfaces = []

        # Percorre todas as interfaces de rede
        for nome, addrs in psutil.net_if_addrs().items():
            stats = psutil.net_if_stats().get(nome)

            for addr in addrs:
                # Considera apenas IPv4
                if addr.family == socket.AF_INET:
                    interfaces.append({
                        "interface": nome,
                        "ip": addr.address,
                        "status": "UP" if stats and stats.isup else "DOWN"
                    })

        # Retorna todas as métricas em um dicionário
        return {
            "os": platform.system(),                              # Sistema operacional
            "cores": psutil.cpu_count(logical=False),             # Núcleos físicos
            "ram_livre": psutil.virtual_memory().available // (1024 ** 2),  # MB
            "disco_livre": psutil.disk_usage("/").free // (1024 ** 3),       # GB
            "interfaces": interfaces,                             # Interfaces de rede
            "mac": hex(uuid.getnode())                             # MAC Address
        }

    # -------------------------------------------------
    # Envia HELLO via broadcast UDP
    # -------------------------------------------------
    def enviar_hello(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        # Habilita envio de broadcast
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

        while self.running:
            # Mensagem HELLO contendo a porta TCP do cliente
            msg = f"HELLO;PORT={self.tcp_port}"

            # Envia para toda a rede local
            sock.sendto(msg.encode(), (BROADCAST_ADDR, BROADCAST_PORT))

            time.sleep(HELLO_INTERVAL)

    # -------------------------------------------------
    # Servidor TCP do cliente (fica em escuta)
    # -------------------------------------------------
    def servidor_tcp(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.bind(("", self.tcp_port))
        sock.listen()

        while self.running:
            # Aguarda conexão do servidor
            conn, _ = sock.accept()

            # Recebe comando
            cmd = conn.recv(1024).decode()

            # Se o servidor pedir dados, envia as métricas
            if cmd == "GET_DATA":
                dados = str(self.coletar_dados())
                conn.send(dados.encode())

            conn.close()

    # -------------------------------------------------
    # Inicializa o cliente
    # -------------------------------------------------
    def start(self):
        print(f"[CLIENTE] Escutando TCP na porta {self.tcp_port}")

        # Thread para enviar HELLO
        threading.Thread(target=self.enviar_hello, daemon=True).start()

        # Thread para escutar conexões TCP
        threading.Thread(target=self.servidor_tcp, daemon=True).start()

        # Mantém o programa ativo
        while True:
            time.sleep(1)


if __name__ == "__main__":
    Cliente().start()