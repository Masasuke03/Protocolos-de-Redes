# Projeto de Redes - Orquestrador e Workers (HTTP/HTTPS)

Este projeto implementa uma arquitetura Orquestrador-Worker concorrente utilizando comunicação HTTP/HTTPS. O orquestrador envia tarefas para múltiplos workers processarem em paralelo, avalia as respostas recebidas e anuncia o vencedor com base na menor latência.

---
##  Criando Ambiente Virtual

Abra o terminal na pasta do projeto e execute os comandos abaixo:

####  No Windows (PowerShell):
```bash
python -m venv venv
.\venv\Scripts\Activate.ps1
```

####  No Linux / macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

##  Requisitos e Instalação

### Bibliotecas Necessárias (`pip install`)

Para rodar o projeto, é necessário instalar os pacotes utilizados pelo orquestrador e pelos workers:

- **Flask**: Framework web para os workers criarem os endpoints HTTP.
- **aiohttp**: Cliente HTTP assíncrono para o orquestrador fazer requisições concorrentes aos workers.
- **PyOpenSSL** *(ou Cryptography)*: Necessário para o suporte ao parâmetro `ssl_context='adhoc'` do Flask.

Você pode instalar todas de uma vez com o comando:

```bash
pip install Flask aiohttp pyOpenSSL
```

---

## Como Executar

 O Orquestrador está configurado para se comunicar nas portas 5001 e 5002, portanto é necessário rodar os workers antes de executar o orquestrador!

 Caso seja preferível adicionar mais workers, é possivel alterar a lista `worker_ports` no orquestrador

---

### Passo 1: Iniciar os Workers

Abra dois terminais diferentes (com o ambiente virtual `venv` ativado) e inicie um worker em cada porta definida:

* **Terminal 1 (Worker 1 - Porta 5001):**
  ```bash
  python worker.py 5001
  ```

* **Terminal 2 (Worker 2 - Porta 5002):**
  ```bash
  python worker.py 5002
  ```

---

### Passo 2: Executar o Orquestrador


* **Terminal 3 (Orquestrador):**
  ```bash
  python orquestrador.py
  ```

---

## 📋 Fluxo de Execução

1. Os **Workers** iniciam seus servidores HTTP locais com suporte a SSL/TLS (`adhoc`).
2. O **Orquestrador** gera uma série numérica aleatória e envia de forma concorrente para `https://localhost:5001` e `https://localhost:5002`.
3. Os **Workers** calculam a predição da série e retornam a resposta.
4. O **Orquestrador** calcula a latência de cada resposta, escolhe a menor latência correta como **vencedora** e dispara uma notificação de `/anuncio` informando o resultado aos workers.

---

## Como desativar o TLS/HTTPS (Rodar em HTTP puro)

Para rodar o projeto sem criptografia SSL/TLS (HTTP puro), basta realizar as seguintes pequenas alterações nos arquivos:

### 1. No `worker.py`
Remova o parâmetro `ssl_context='adhoc'` do `app.run()` no final do arquivo:

**Aqui:**
```python
if __name__ == '__main__':
    app.run(host='127.0.0.1', port=porta_worker, ssl_context='adhoc')
```
### 2. No `orquestrador.py`

Altere as URLs de `https://` para `http://` e remova a verificação de SSL no `aiohttp.TCPConnector`:

**Aqui:**
```python
worker_ports = ["https://localhost:5001", "https://localhost:5002"]

```

```python
conn = aiohttp.TCPConnector(ssl=ssl_context)
```


