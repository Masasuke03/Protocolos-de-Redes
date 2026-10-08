##  Visão Geral da Arquitetura

Neste modelo, a comunicação ocorre através de ligações TCP persistentes de fluxo contínuo.

* **Orquestrador:** Atua como **Servidor TCP**, mantendo-se à escuta na porta 65432 e aguardando a ligação dos trabalhadores. 
* **Workers:** Atuam como **Clientes TCP**, estabelecendo a ligação ativa diretamente para o IP do Orquestrador (127.0.0.1).
* **Payload:** Objetos JSON serializados, codificados em UTF-8 e separados pelo delimitador de quebra de linha (\n).

---

## Pré-requisitos e Instalação

É necessário ter o Python 3.x instalado.

A aplicação utiliza exclusivamente bibliotecas nativas do Python (socket, ssl, json, threading), não sendo necessária a instalação de pacotes externos.

---

## Geração de Certificados de Segurança (TLS)

Antes de iniciar a execução, é estritamente necessário gerar os certificados de segurança locais. 
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
python orquestrador_socket.py
```

2. Nos outros dois terminais, inicie os Trabalhadores para formar o consenso e dar a largada:
```
python trabalhador_socket.py
```
