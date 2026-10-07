## Visão Geral da Arquitetura

Neste modelo, o Orquestrador se comunica diretamente com cada Worker através de requisições **HTTP/HTTPS** (REST), sem intermediários.

* **Orquestrador:** Atua como **Cliente HTTP** (`aiohttp`). Envia a tarefa a todos os Workers ao mesmo tempo, mede a latência de cada resposta e anuncia o resultado.
* **Workers:** Atuam como **Servidores HTTP** (`Flask`), escutando nas portas `5001` e `5002`, e expõem dois endpoints:
  * `POST /tarefa`: recebe o desafio e devolve a resposta calculada.
  * `POST /anuncio`: recebe o resultado da corrida (ganhou ou perdeu).

O vencedor é o Worker mais rápido entre os que deram a resposta da maioria, e recebe `50` Pfitscher Coins.

---

## Requisitos

* Python 3.8+

Crie e ative o ambiente virtual (opcional, mas recomendado):

```
python -m venv venv
.\venv\Scripts\Activate.ps1
```
> No Linux/macOS: `source venv/bin/activate`

Instale as dependências:

```
pip install Flask aiohttp cryptography
```

> O `cryptography` só é necessário no modo HTTPS (`ssl_context='adhoc'` do Flask).

---

## Modos de Execução

> Ordem importante: **inicie os Workers antes do Orquestrador**. O Orquestrador envia as requisições uma única vez e encerra.

### 1. HTTP Puro (Texto Claro)

Em terminais diferentes:

```
python worker.py 5001

python worker.py 5002

python orquestrador.py
```

### 2. HTTPS (Cifrado com TLS)

Em terminais diferentes:

```
python SSL_worker.py 5001

python SSL_worker.py 5002

python SSL_orquestrador.py
```

> Não precisa gerar certificados: o Flask cria um certificado temporário a cada execução (`ssl_context='adhoc'`). Por ser autoassinado, o Orquestrador SSL desativa a verificação (`CERT_NONE`). Use apenas para testes.

---

## Saída Esperada

```
--- RESULTADO DA CORRIDA ---
Trabalhador Porta 5001 | Resposta: 32.0 | Tempo: 8.52 ms
Trabalhador Porta 5002 | Resposta: 32.0 | Tempo: 6.10 ms

[Consenso] A resposta da maioria é: 32.0
VENCEDOR: Porta 5002 com 6.10 ms!
```

---

## Configurações

* `worker_ports` (Orquestrador): lista de URLs dos Workers. Para adicionar mais, inclua novas portas na lista e inicie um Worker para cada uma.
* Em máquinas diferentes: troque `127.0.0.1` pelo IP do Worker no Orquestrador, e no Worker use `host='0.0.0.0'` em `app.run()`.

---

## Problemas Comuns

* **`ModuleNotFoundError`** - rode `pip install Flask aiohttp cryptography`.
* **`Erro ao enviar tarefa ... Cannot connect to host`** - o Worker daquela porta não está rodando.
* **`IndexError` ao iniciar o Worker** - faltou informar a porta (`python worker.py 5001`).
* **Erro de conexão/SSL ao misturar modos** - HTTP só conversa com HTTP e HTTPS só com HTTPS: use `worker.py` com `orquestrador.py`, e `SSL_worker.py` com `SSL_orquestrador.py`.
* **`Address already in use`** - a porta já está ocupada por outro Worker. Encerre-o com `Ctrl+C`.
