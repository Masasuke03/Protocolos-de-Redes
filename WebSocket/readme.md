##  Visão Geral da Arquitetura

Neste modelo, a comunicação ocorre através de ligações TCP persistentes assíncronas.

* **Orquestrador:** Atua como **Servidor WS**, mantendo-se à escuta na porta 8765 e aguardando a ligação dos trabalhadores. 
* **Workers:** Atuam como **Clientes WS**, estabelecendo a ligação ativa e o Handshake HTTP diretamente para o IP do Orquestrador (127.0.0.1).
* **Payload:** Objetos JSON serializados e codificados em UTF-8.
  
---

## Pré-requisitos e Instalação

É necessário ter o Python 3.x instalado.
Ao contrário do Socket, o WebSocket não é nativo do Python. É obrigatória a instalação da biblioteca assíncrona correspondente:

```
pip install websockets
```

---

## Geração de Certificados de Segurança (WSS)

Antes de iniciar a execução da comunicação cifrada, é estritamente necessário gerar os certificados de segurança locais. 
Na raiz do diretório do projeto, execute o seguinte comando no terminal para criar as chaves:

```
openssl req -x509 -newkey rsa:4096 -keyout key.pem -out cert.pem -days 365 -nodes
```

---
### Executando
Todos os testes estão configurados para correr no ambiente local (localhost - 127.0.0.1). 
**Abra 3 terminais distintos e execute:**

1. No primeiro terminal, inicie o Orquestrador:
```
python orquestrador_websocket.py
```

2. Nos outros dois terminais, inicie os Trabalhadores para formar o consenso e dar a largada:
```
python trabalhador_websocket.py
```
