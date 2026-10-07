import socket
import json

def trabalhar():
    IP_ORQUESTRADOR = '127.0.0.1' 
    PORT = 65432

    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((IP_ORQUESTRADOR, PORT))
            print("Conectado! Aguardando a largada do Orquestrador...")

            buffer_tarefa = ""
            while True:
                parte = s.recv(1024).decode('utf-8')
                if not parte:
                    break
                buffer_tarefa += parte
                if '\n' in buffer_tarefa:
                    break

            if not buffer_tarefa:
                print("Conexão encerrada pelo orquestrador.")
                return

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
    except KeyboardInterrupt:
        print("\n[Aviso] Trabalhador encerrado via Ctrl+C.")
    except Exception as e:
        print(f"[Erro] Falha no trabalhador: {e}")

if __name__ == "__main__":
    trabalhar()