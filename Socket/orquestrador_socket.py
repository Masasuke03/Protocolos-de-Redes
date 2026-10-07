import socket
import threading
import time
import json
import statistics

HOST = '0.0.0.0'
PORT = 65432
TOTAL_TRABALHADORES = 2
TIMEOUT_REDE = 2.0

trabalhadores_prontos = []
respostas_recebidas = []
lock = threading.Lock()
largada_event = threading.Event()

def atender_trabalhador(conn, addr):
    endereco = f"{addr[0]}:{addr[1]}"
    try:
        with lock:
            trabalhadores_prontos.append(conn)
            if len(trabalhadores_prontos) == TOTAL_TRABALHADORES:
                largada_event.set()

        largada_event.wait()

        tarefa = {"desafio": [2, 4, 8, 16], "task_id": "12345"}
        mensagem = json.dumps(tarefa) + "\n"
        
        tempo_envio = time.perf_counter()
        conn.sendall(mensagem.encode('utf-8'))

        conn.settimeout(TIMEOUT_REDE)
        buffer = ""
        while True:
            parte = conn.recv(1024).decode('utf-8')
            if not parte:
                break
            buffer += parte
            if '\n' in buffer:
                break
        
        tempo_chegada = time.perf_counter()
        
        if buffer:
            linha_json = buffer.split('\n')[0]
            resposta_json = json.loads(linha_json)
            atraso_ms = (tempo_chegada - tempo_envio) * 1000
            
            with lock:
                respostas_recebidas.append({
                    "conn": conn,
                    "endereco": endereco,
                    "valor": resposta_json["resposta"],
                    "tempo": atraso_ms
                })
    except socket.timeout:
        print(f"[Erro] Trabalhador {endereco} estourou o tempo limite.")
    except Exception as e:
        print(f"[Erro] Falha na conexão com {endereco}: {e}")

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((HOST, PORT))
        s.listen()
        s.settimeout(1.0)  # Permite verificar o Ctrl+C periodicamente
        print(f"Orquestrador Sockets (sem TLS) aguardando {TOTAL_TRABALHADORES} trabalhadores...")

        threads = []
        try:
            while len(threads) < TOTAL_TRABALHADORES:
                try:
                    conn, addr = s.accept()
                    t = threading.Thread(target=atender_trabalhador, args=(conn, addr))
                    t.daemon = True  # Encerra com o programa principal
                    t.start()
                    threads.append(t)
                except socket.timeout:
                    continue
        except KeyboardInterrupt:
            print("\n[Aviso] Execução interrompida pelo usuário via Ctrl+C. Encerrando...")
            return

        for t in threads:
            t.join()

    print("\n--- RESULTADO DA CORRIDA ---")
    conn_vencedor = None
    
    if not respostas_recebidas:
        print("Nenhum trabalhador enviou resposta válida.")
    else:
        for r in respostas_recebidas:
            print(f"Trabalhador {r['endereco']} | Resposta: {r['valor']} | Tempo: {r['tempo']:.2f} ms")

        valores = [r["valor"] for r in respostas_recebidas]
        try:
            moda = statistics.mode(valores)
            print(f"\n[Consenso] A resposta da maioria é: {moda}")

            acertadores = [r for r in respostas_recebidas if r["valor"] == moda]
            acertadores.sort(key=lambda x: x["tempo"])
            vencedor = acertadores[0]
            conn_vencedor = vencedor['conn']

            print(f"VENCEDOR: {vencedor['endereco']} com {vencedor['tempo']:.2f} ms!")
        except statistics.StatisticsError:
            print("\n[Empate Total] Nenhuma resposta formou maioria absoluta.")

    print("\nEnviando Winner Announcement e encerrando...")
    for conn in trabalhadores_prontos:
        try:
            ganhou = (conn == conn_vencedor)
            anuncio = {
                "task_id": "12345",
                "ganhou": ganhou,
                "reward_coins": 50 if ganhou else 0
            }
            mensagem_anuncio = json.dumps(anuncio) + "\n"
            conn.sendall(mensagem_anuncio.encode('utf-8'))
            conn.close()
        except Exception:
            pass

if __name__ == "__main__":
    main()