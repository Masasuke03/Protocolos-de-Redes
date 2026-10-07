## Visão Geral da Arquitetura

Neste modelo, Orquestrador e Workers **não se falam diretamente**: toda a comunicação passa por um **Broker MQTT (Mosquitto)**, usando o padrão publicar/assinar.

* **Broker (Mosquitto):** Roda em Docker e distribui as mensagens entre os clientes.
* **Orquestrador:** Publica a tarefa em `pfitscher/tarefas`, escuta as respostas em `pfitscher/respostas`, escolhe o vencedor e publica o resultado em `pfitscher/anuncio`.
* **Workers:** Assinam `pfitscher/tarefas` e `pfitscher/anuncio`, e respondem em `pfitscher/respostas`.

O vencedor é o Worker mais rápido entre os que deram a resposta da maioria, e recebe `50` Pfitscher Coins.

---

## Requisitos

* Python 3.8+
* Docker
* OpenSSL (apenas para o modo cifrado)

```
pip install paho-mqtt
```

> Os códigos usam `mqtt.CallbackAPIVersion.VERSION2`, que exige **paho-mqtt 2.0 ou superior**.

---

## Arquivos

| Arquivo | Função |
|---|---|
| `orchestrator.py` / `worker1.py` / `worker2.py` | Modo puro (porta `1883`) |
| `MQTTS_orquestrador.py` / `TLS_worker1.py` / `TLS_worker2.py` | Modo cifrado (porta `8883`) |
| `mosquitto.conf` | Configuração do broker |
| `server.crt` / `server.key` | Certificado e chave do broker (modo cifrado) |
| `ca.crt` | Lido pelos clientes TLS (ver seção Certificados) |

---

## Configuração do Broker

Crie o `mosquitto.conf` com os dois listeners (um único broker atende os dois modos):

```
listener 1883
allow_anonymous true

listener 8883
allow_anonymous true
cafile /mosquitto/config/ca.crt
certfile /mosquitto/config/server.crt
keyfile /mosquitto/config/server.key
```

Suba o broker (PowerShell, dentro da pasta do projeto):

```
docker run -d --name mosquitto -p 1883:1883 -p 8883:8883 -v "${PWD}/mosquitto.conf:/mosquitto/config/mosquitto.conf" -v "${PWD}/ca.crt:/mosquitto/config/ca.crt" -v "${PWD}/server.crt:/mosquitto/config/server.crt" -v "${PWD}/server.key:/mosquitto/config/server.key" eclipse-mosquitto
```

---

## Modos de Execução

> Ordem importante: **Broker → Workers → Orquestrador**. O Orquestrador publica a tarefa uma única vez; Workers que ainda não estiverem conectados perdem a rodada.

### 1. MQTT Puro (Texto Claro - Porta 1883)

Em terminais diferentes:
```
python worker1.py

python worker2.py

python orchestrator.py
```

### 2. MQTTS (Cifrado com TLS - Porta 8883)

Em terminais diferentes:
```
python TLS_worker1.py

python TLS_worker2.py

python MQTTS_orquestrador.py
```

---

## Certificados: quais são realmente necessários?

| Arquivo | Necessário? | Motivo |
|---|---|---|
| `server.crt` + `server.key` | **Sim** | O broker precisa deles para abrir o listener TLS. |
| `ca.crt` | **Só existir** | Os clientes chamam `tls_set(ca_certs="ca.crt")`, então o arquivo precisa existir, mas com `CERT_NONE` seu conteúdo não é usado para validar nada. |

Nos Workers e no Orquestrador TLS, `cert_reqs=ssl.CERT_NONE` e `tls_insecure_set(True)` fazem o cliente **aceitar qualquer certificado**. O tráfego fica cifrado, mas o broker não é autenticado (vulnerável a man-in-the-middle). Para estudo e testes locais isso é suficiente.

### Gerando o mínimo necessário

Um único certificado autoassinado basta (sem CA, sem `.cnf`):

```
openssl req -x509 -newkey rsa:2048 -nodes -keyout server.key -out server.crt -days 365 -subj "/CN=localhost" -addext "subjectAltName=DNS:localhost,IP:127.0.0.1"

copy server.crt ca.crt
```

### Ativando a validação de verdade (opcional)

Com o certificado acima (que contém `localhost` e `127.0.0.1`), nos clientes TLS troque:

```python
cliente.tls_set(ca_certs="ca.crt", cert_reqs=ssl.CERT_NONE)
cliente.tls_insecure_set(True)
```
por:
```python
cliente.tls_set(ca_certs="ca.crt", cert_reqs=ssl.CERT_REQUIRED)
```

Assim o cliente só conecta se o broker apresentar exatamente o certificado em que ele confia.

---

## Problemas Comuns

* **`ModuleNotFoundError: paho`** - rode `pip install paho-mqtt`.
* **`AttributeError: CallbackAPIVersion`** - paho-mqtt antigo. Rode `pip install --upgrade paho-mqtt`.
* **`FileNotFoundError: ca.crt`** - os clientes TLS precisam do `ca.crt` na pasta de execução.
* **`Connection refused`** - o container não está rodando ou a porta (`1883`/`8883`) não foi publicada. Confira com `docker ps`.
* **"Nenhuma resposta recebida"** - os Workers precisam estar conectados **antes** do Orquestrador.
