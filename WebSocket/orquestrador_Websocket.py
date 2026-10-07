import asyncio
import websockets
import json
import time
import statistics

TOTAL_TRABALHADORES = 2
clientes_conectados = []
respostas = []
largada_event = asyncio.Event()
concluidos_event = asyncio.Event()

async def atender_trabalhador(websocket):
    clientes_conectados.append(websocket)
    
    endereco = f"{websocket.remote_address[0]}:{websocket.remote_address[1]}"
    print(f"Trabalhador conectado de {endereco}")
    
    if len(clientes_conectados) == TOTAL_TRABALHADORES:
        largada_event.set()
    
    await largada_event.wait()
    
    tarefa = {"desafio": [2, 4, 8, 16], "task_id": "12345"}
    tempo_envio = time.perf_counter()
    await websocket.send(json.dumps(tarefa))
    
    try:
        resposta_str = await asyncio.wait_for(websocket.recv(), timeout=2.0)
        tempo_chegada = time.perf_counter()
        resposta_json = json.loads(resposta_str)
        
        respostas.append({
            "ws": websocket,
            "endereco": endereco,
            "valor": resposta_json["resposta"],
            "tempo": (tempo_chegada - tempo_envio) * 1000
        })
    except asyncio.TimeoutError:
        print(f"Tempo limite de {endereco} esgotado.")
    except Exception:
        pass
        
    if len(respostas) == TOTAL_TRABALHADORES:
        concluidos_event.set()
        
    try:
        while True:
            await asyncio.sleep(1)
    except websockets.exceptions.ConnectionClosed:
        pass

async def main():
    # Inicialização do servidor em modo WS simples (sem parâmetro ssl)
    server = await websockets.serve(atender_trabalhador, "0.0.0.0", 8765)
    print(f"Orquestrador WS (sem cifragem) aguardando {TOTAL_TRABALHADORES} trabalhadores...")
    
    try:
        await largada_event.wait()
        try:
            await asyncio.wait_for(concluidos_event.wait(), timeout=3.0)
        except asyncio.TimeoutError:
            pass

        print("\n--- RESULTADO DA CORRIDA ---")
        ws_vencedor = None
        if respostas:
            for r in respostas:
                print(f"Trabalhador {r['endereco']} | Resposta: {r['valor']} | Tempo: {r['tempo']:.2f} ms")
            
            valores = [r["valor"] for r in respostas]
            try:
                moda = statistics.mode(valores)
                acertadores = [r for r in respostas if r["valor"] == moda]
                acertadores.sort(key=lambda x: x["tempo"])
                
                if acertadores:
                    vencedor = acertadores[0]
                    ws_vencedor = vencedor['ws']
                    print(f"VENCEDOR: {vencedor['endereco']} com {vencedor['tempo']:.2f} ms!")
            except statistics.StatisticsError:
                print("Sem maioria absoluta. Empate.")
        
        for ws in clientes_conectados:
            try:
                ganhou = (ws == ws_vencedor)
                anuncio = {
                    "task_id": "12345",
                    "ganhou": ganhou,
                    "reward_coins": 50 if ganhou else 0
                }
                await ws.send(json.dumps(anuncio))
                await ws.close()
            except Exception:
                pass

    except asyncio.CancelledError:
        pass
    finally:
        server.close()
        await server.wait_closed()

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[Aviso] Orquestrador encerrado via Ctrl+C.")