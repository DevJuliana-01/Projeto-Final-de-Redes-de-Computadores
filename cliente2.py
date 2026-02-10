import socket
import time

# 1. Teste UDP Broadcast (servidor.py)
print("=== TESTE UDP ===")
sock_udp = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock_udp.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

try:
    print("[CLIENTE] Iniciando envio de mensagens HELLO...")
    while True:
        sock_udp.sendto(b"HELLO;PORT=12345", ("127.0.0.1", 50000))
        print(f"✓ Mensagem UDP enviada - {time.strftime('%H:%M:%S')}")
        time.sleep(5)  # Envia a cada 5 segundos
except KeyboardInterrupt:
    print("\n[CLIENTE] Encerrando...")
finally:
    sock_udp.close()
    print("[CLIENTE] Socket fechado")
