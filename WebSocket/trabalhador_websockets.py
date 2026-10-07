import asyncio
import websockets
import json

async def trabalhar():
    # Protocolo alterado de wss:// para ws://
    uri = "ws://127.0.0.1:8765"

    try:
        # Conexão WS direta sem o contexto ssl
        async with websockets.connect(uri) as websocket:
            print("Conectado ao WS! Aguardando largada...")
            
            tarefa_str = await websocket.recv()
            tarefa = json.loads(tarefa_str)
            serie = tarefa["desafio"]
            
            razao = serie[-1] / serie[-2]
            proximo = serie[-1] * razao
            
            resposta = {"resposta": proximo}
            await websocket.send(json.dumps(resposta))
            print(f"Cálculo concluído ({proximo}). Resposta enviada!")
            
            anuncio_str = await websocket.recv()
            anuncio = json.loads(anuncio_str)
            
            if anuncio["ganhou"]:
                print(f"Recebi {anuncio['reward_coins']} Pfitscher Coins!")
            else:
                print("Perdi.")
    except KeyboardInterrupt:
        print("\n[Aviso] Trabalhador encerrado via Ctrl+C.")
    except Exception as e:
        print(f"[Erro] Falha no trabalhador: {e}")

if __name__ == "__main__":
    asyncio.run(trabalhar())