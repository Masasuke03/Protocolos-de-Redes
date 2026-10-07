import socket
import json
import ssl

def trabalhar():
    IP_ORQUESTRADOR = '127.0.0.1' 
    PORT = 65432

    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    with ssl_context.wrap_socket(socket.socket(socket.AF_INET, socket.SOCK_STREAM), server_hostname=IP_ORQUESTRADOR) as s:
        
        s.connect((IP_ORQUESTRADOR, PORT))
        print("Conectado! Aguardando a largada do Orquestrador...")

        buffer_tarefa = ""
        while True:
            parte = s.recv(1024).decode('utf-8')
            buffer_tarefa += parte
            if '\n' in buffer_tarefa:
                break

        linha_json = buffer_tarefa.split('\n')[0]
        tarefa = json.loads(linha_json)
        serie = tarefa["desafio"]

        razao = serie[-1] / serie[-2]
        proximo = serie[-1] * razao

        resposta = {"resposta": proximo}
        mensagem_envio = json.dumps(resposta) + "\n"
        
        s.sendall(mensagem_envio.encode('utf-8'))
        print(f"Cálculo concluído ({proximo}). Resposta enviada!")
        print("Aguardando o anúncio do vencedor...")

        buffer_anuncio = ""
        while True:
            parte = s.recv(1024).decode('utf-8')
            if not parte:
                break
            buffer_anuncio += parte
            if '\n' in buffer_anuncio:
                break
        
        if buffer_anuncio:
            linha_anuncio = buffer_anuncio.split('\n')[0]
            anuncio = json.loads(linha_anuncio)
            
            if anuncio["ganhou"]:
                print(f"Recebi {anuncio['reward_coins']} Pfitscher Coins!")
            else:
                print("Perdi.")

if __name__ == "__main__":
    trabalhar()