##  Visão Geral da Arquitetura

Neste modelo, o Orquestrador comunica diretamente com cada Worker através de conexões TCP dedicadas (P2P), sem intermediários.

* **Orquestrador:** Atua como **Cliente TCP**, abrindo conexões diretas para o IP e porta de cada Worker e enviando as tarefas em paralelo.
* **Workers:** Atuam como **Servidores TCP**, escutando em portas locais dedicadas (`5001`, `5002`), processando as requisições e devolvendo as respostas na mesma sessão de socket.

---

## Modos de Execução

### 1. Socket TCP Puro (Texto Claro - Porta 1883 / Portas locais)
* **Comunicação:** Transmissão direta de fluxos de bytes (`bytes stream`) sobre o protocolo TCP.
* **Payload:** Objetos JSON serializados e codificados em `utf-8`.

### Executando
* **Em terminais diferentes execute:**
```
python orquestrador_socket.py

python trabalhador_socket.py
```


### 2. Socket TCP Cifrado
* **Em terminais diferentes execute:**
```
python SSL_orquestrador_socket.py

python SSL_trabalhador_socket.py
