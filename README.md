# Projeto-Final-de-Redes-de-Computadores

## Descrição
Projeto de monitoramento simples em arquitetura Cliente/Servidor. Clientes publicam mensagens de "HELLO" por UDP e também expõem um servidor TCP que fornece métricas do sistema quando solicitado. O servidor descobre clientes, solicita métricas e apresenta um dashboard no terminal com consolidação básica.

## Arquivos
- `servidor.py`: Escuta HELLOs via UDP (porta 50000), mantém a lista de clientes, solicita dados via TCP (`GET_DATA`), calcula médias e exibe um dashboard no terminal.
- `cliente.py`: Envia HELLOs periódicos via UDP informando sua porta TCP, expõe um servidor TCP que responde ao comando `GET_DATA` com um dicionário contendo métricas (SO, núcleos, RAM livre, disco livre, interfaces, MAC).
- `cliente2.py`: Script de teste que envia mensagens HELLO para o servidor (útil para testes locais).

## Como funciona (fluxo resumido)
- Cada cliente escolhe dinamicamente uma porta TCP livre e passa essa porta no HELLO (mensagem: `HELLO;PORT=xxxx`).
- O servidor escuta HELLOs e registra/atualiza a última vez que recebeu mensagem de cada cliente.
- O servidor conecta por TCP ao cliente e manda `GET_DATA` para obter as métricas (retornadas como dicionário).
- O dashboard do servidor exibe clientes, status (ONLINE/OFFLINE) e calcula médias de RAM, disco e núcleos entre os clientes online.

## Requisitos (status de implementação)
Observação: abaixo os itens da lista do professor com o estado atual baseado no código presente.

- 2.1 Coleta por Cliente
	- Quantidade de processadores / núcleos (0,4): ✅️ (`psutil.cpu_count(logical=False)` em `cliente.py`).
	- Memória RAM livre (0,4): ✅️ (`psutil.virtual_memory().available`, em MB).
	- Espaço em disco livre (0,4): ✅️ (`psutil.disk_usage("/").free`, em GB).
	- IPs das interfaces e status UP/DOWN (0,4): PARCIAL ➕️➖️ — Os IPs e o status (UP/DOWN) são coletados, mas o tipo da interface (loopback/ethernet/wifi) não é identificado.
	- Identificação do sistema operacional (0,4): ✅️ (`platform.system()`).

- 2.2 Servidor / Consolidação
	- Dashboard em terminal com lista de clientes, última atualização, sistema operacional e IP principal (0,5): PARCIAL ➕️➖️ — Há dashboard no terminal com lista e status; o código atual não exibe explicitamente a "última atualização" formatada nem o sistema operacional/ IP principal na listagem (os dados existem internamente quando o `GET_DATA` foi bem-sucedido).
	- Consolidação (médias) e contagem online/offline (0,5): ✅️ o servidor calcula médias de RAM, disco e núcleos e conta clientes online/offline.
	- Detalhamento de um cliente selecionado (0,5): ❌️ — não existe interface interativa para detalhar um cliente específico.
	- Exportação de relatórios em CSV/JSON (0,5): ❌️ — não há funções de exportação (embora `csv` esteja importado no servidor, não é usado).

- 3.0. Requisitos principais
	- Arquitetura Cliente/Servidor (1,0): ✅️
	- Descoberta automática na LAN (broadcast/multicast/hello) (1,0): ✅️ atenção: em `cliente.py` o `BROADCAST_ADDR` está definido como `127.0.0.1` por padrão (para testes locais) — para descoberta em LAN real alterar para `255.255.255.255` ou endereço de broadcast da sub-rede.
	- Uso de sockets puros (TCP/UDP) (1,0): ✅️ (uso de sockets UDP para hello e TCP para dados).
	- Paradigma Orientado a Objetos, código modular (1,0): ✅️ (`Cliente` e `Servidor` classes).

- 4.0. Segurança
	- Comunicação segura (criptografia/integridade) (0,5): ❌️
	- Autenticação e controle de acesso (0,3): ❌️
	- Auditoria no servidor (0,2): ❌️

- 5.0. Bônus
	- Controle remoto do mouse (1,0): ❌️
	- Controle remoto do teclado (1,0): ❌️

## Observações / limitações importantes
- O código está funcional para testes locais, mas `BROADCAST_ADDR` em `cliente.py` está configurado para `127.0.0.1` (loopback). Para operar em uma LAN real, precisariamos ajustar para broadcast real (ex.: `255.255.255.255`) e garanti permissões de firewall.

## Como executar (exemplo rápido)
Abra um terminal para o servidor e outro para cada cliente (ou múltiplos clientes):

```bash
python3 servidor.py
python3 cliente.py
# ou, para um cliente de teste que apenas envia HELLOs:
python3 cliente2.py
```