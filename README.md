# Protocolos de Redes

Comparação prática de quatro protocolos de comunicação (**Socket TCP, HTTP, WebSocket e MQTT**), cada um com sua versão **em texto claro** e **cifrada (TLS)**.

Em todos eles o mesmo problema é resolvido, mudando apenas o protocolo usado para transportar as mensagens.

---

## O Desafio

Um **Orquestrador** coordena uma corrida entre **Workers**:

1. O Orquestrador envia a mesma tarefa a todos os Workers: uma série numérica, por exemplo `[2, 4, 8, 16]`.
2. Cada Worker calcula o próximo termo da progressão (`32`) e responde.
3. O Orquestrador mede o tempo de resposta de cada um e define a resposta correta pela **maioria**.
4. O Worker mais rápido entre os que acertaram vence e recebe `50` **Pfitscher Coins**. Os demais recebem `0`.

---

## Estrutura do Repositório

| Pasta | Protocolo | Documentação |
|---|---|---|
| [`Socket/`](./Socket) | TCP / TCP + TLS | [README](./Socket/readme.md) |
| [`HTTP/`](./HTTP) | HTTP / HTTPS | [README](./HTTP/readme.md) |
| [`WebSocket/`](./WebSocket) | WS / WSS | [README](./WebSocket/readme.md) |
| [`MQTT/`](./MQTT) | MQTT / MQTTS | [README](./MQTT/readme.md) |

---

## Comparativo

| Protocolo | Orquestrador | Workers | Intermediário | Portas | Versão cifrada |
|---|---|---|---|---|---|
| **Socket** | Cliente TCP | Servidores TCP | Não | `5001`, `5002` | TCP + TLS |
| **HTTP** | Cliente HTTP | Servidores HTTP (Flask) | Não | `5001`, `5002` | HTTPS |
| **WebSocket** | Servidor WS | Clientes WS | Não | `8765` | WSS |
| **MQTT** | Cliente MQTT | Clientes MQTT | Broker (Mosquitto) | `1883` | MQTTS (`8883`) |

---

## Requisitos

* Python 3.8+
* Docker (apenas para o broker do MQTT)
* OpenSSL (apenas para gerar certificados dos modos cifrados que os exigem)

Dependências por protocolo:

| Protocolo | Instalação |
|---|---|
| Socket | Nenhuma (apenas biblioteca padrão) |
| HTTP | `pip install Flask aiohttp cryptography` |
| WebSocket | `pip install websockets` |
| MQTT | `pip install paho-mqtt` |

> Recomenda-se usar um ambiente virtual (`python -m venv venv`). Os detalhes de cada protocolo estão no README da respectiva pasta.

---

## Como Executar

1. Clone o repositório:
   ```
   git clone https://github.com/elison-maiko/Protocolos-de-Redes.git
   cd Protocolos-de-Redes
   ```
2. Entre na pasta do protocolo desejado (ex.: `cd HTTP`).
3. Siga o README da pasta: instalação, ordem de execução e modos (puro e cifrado).

---

## Documentação

📄 **Relatório do trabalho:** [COLE_AQUI_O_LINK_DO_GOOGLE_DOCS](https://docs.google.com/document/d/15CiDHxdGoMlZoRX6hDYCkoGJ8J83lRQCAU1RyxG8nVQ/edit?usp=sharing)

---

## Autores

**Elison Maiko** - [@elison-maiko](https://github.com/elison-maiko)
**Mashima** - [@elison-maiko](https://github.com/elison-maiko)
