import socket
import threading
import time
import csv
import ast

# Porta usada para escutar HELLO via UDP
BROADCAST_PORT = 50000

# Tempo máximo sem HELLO para considerar OFFLINE
TIMEOUT = 30


# -------------------------------------------------
# Classe que representa um cliente conhecido
# -------------------------------------------------
class ClienteInfo:
    def __init__(self, ip, port):
        self.ip = ip                  # IP do cliente
        self.port = port              # Porta TCP do cliente
        self.last_seen = time.time()  # Último HELLO recebido
        self.data = None              # Dados coletados do cliente


# -------------------------------------------------
# Classe principal do servidor
# -------------------------------------------------
class Servidor:
    def __init__(self):
        # Dicionário de clientes (IP -> ClienteInfo)
        self.clientes = {}

    # -------------------------------------------------
    # Escuta mensagens HELLO via UDP (broadcast)
    # -------------------------------------------------
    def escutar_broadcast(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.bind(("", BROADCAST_PORT))

        while True:
            msg, addr = sock.recvfrom(1024)
            ip = addr[0]

            # Extrai a porta TCP do cliente
            port = int(msg.decode().split("=")[1])

            # Se for um novo cliente, adiciona
            if ip not in self.clientes:
                self.clientes[ip] = ClienteInfo(ip, port)

            # Atualiza o último HELLO recebido
            self.clientes[ip].last_seen = time.time()

    # -------------------------------------------------
    # Coleta dados dos clientes via TCP
    # -------------------------------------------------
    def atualizar_clientes(self):
        while True:
            for c in self.clientes.values():
                # Ignora clientes offline
                if time.time() - c.last_seen > TIMEOUT:
                    continue

                try:
                    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    s.connect((c.ip, c.port))

                    # Solicita dados
                    s.send(b"GET_DATA")

                    # Recebe resposta
                    resposta = s.recv(8192).decode()

                    # Converte string para dicionário
                    c.data = ast.literal_eval(resposta)

                    s.close()
                except:
                    pass

            time.sleep(10)

    # -------------------------------------------------
    # Calcula as médias das métricas dos clientes ONLINE
    # -------------------------------------------------
    def calcular_medias(self):
        total_ram = total_disco = total_cores = 0
        count = 0

        for c in self.clientes.values():
            if c.data and (time.time() - c.last_seen < TIMEOUT):
                total_ram += c.data["ram_livre"]
                total_disco += c.data["disco_livre"]
                total_cores += c.data["cores"]
                count += 1

        # Evita divisão por zero
        if count == 0:
            return None

        return {
            "media_ram": total_ram / count,
            "media_disco": total_disco / count,
            "media_cores": total_cores / count
        }

    # -------------------------------------------------
    # Dashboard no terminal
    # -------------------------------------------------
    def dashboard(self):
        while True:
            time.sleep(5)

            print("\n====== DASHBOARD ======")
            online = 0

            for ip, c in self.clientes.items():
                status = "ONLINE" if time.time() - c.last_seen < TIMEOUT else "OFFLINE"
                if status == "ONLINE":
                    online += 1
                print(f"{ip} | {status}")

            print(f"Online: {online} | Offline: {len(self.clientes) - online}")

            # Exibe médias
            medias = self.calcular_medias()
            if medias:
                print("\n--- MÉDIAS ---")
                print(f"RAM livre média (MB): {medias['media_ram']:.2f}")
                print(f"Disco livre médio (GB): {medias['media_disco']:.2f}")
                print(f"Núcleos médios: {medias['media_cores']:.2f}")

    # -------------------------------------------------
    # Inicializa o servidor
    # -------------------------------------------------
    def start(self):
        threading.Thread(target=self.escutar_broadcast, daemon=True).start()
        threading.Thread(target=self.atualizar_clientes, daemon=True).start()
        threading.Thread(target=self.dashboard, daemon=True).start()

        while True:
            time.sleep(1)


if __name__ == "__main__":
    Servidor().start()