## Visão Geral da Arquitetura

Neste modelo, o Orquestrador e os Workers se comunicam por **WebSockets**, em uma "corrida" de cálculo.

* **Orquestrador:** Atua como **Servidor WebSocket** (porta `8765`). Espera todos os Workers conectarem, envia o mesmo desafio a todos ao mesmo tempo e mede o tempo de resposta de cada um.
* **Workers:** Atuam como **Clientes WebSocket**, resolvem o desafio e respondem na mesma conexão.

O vencedor é o Worker mais rápido entre os que acertaram (resposta mais comum) e recebe `50` Pfitscher Coins.

---

## Requisitos

* Python 3.8+
* OpenSSL (apenas para o modo cifrado)

```
pip install websockets
```

---

## Modos de Execução

### 1. WebSocket Puro (WS - Texto Claro)

Em terminais diferentes, **nesta ordem**:
```
python orquestrador_Websocket.py

python trabalhador_websockets.py

python trabalhador_websockets.py
```

### 2. WebSocket Cifrado (WSS - TLS)

Gere o certificado autoassinado (necessário apenas uma vez):
```
openssl req -x509 -newkey rsa:2048 -nodes -keyout key.pem -out cert.pem -days 365 -subj "/CN=localhost"
```

Em terminais diferentes, **nesta ordem**:
```
python SSL_orquestrador_websocket.py

python SSL_trabalhador_websocket.py

python SSL_trabalhador_websocket.py
```

> O Worker SSL desativa a verificação do certificado para aceitar o autoassinado. Use apenas para testes.

---

## Configurações

* `TOTAL_TRABALHADORES` (Orquestrador): quantidade de Workers esperados (padrão `2`).
* `uri` (Worker): endereço do Orquestrador (padrão `127.0.0.1`). Em máquinas diferentes, troque pelo IP do Orquestrador e libere a porta `8765` no firewall.

---

## Problemas Comuns

* **`ModuleNotFoundError: websockets`** - rode `pip install websockets`.
* **`FileNotFoundError` no modo SSL** - `cert.pem` e `key.pem` precisam estar na pasta de execução.
* **Largada não acontece** - o número de Workers conectados deve ser igual a `TOTAL_TRABALHADORES`.
