import asyncio
import websockets
import json
import ssl

async def trabalhar():
    uri = "wss://127.0.0.1:8765"
    
    ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    async with websockets.connect(uri, ssl=ssl_context) as websocket:
        print("Conectado ao WSS! Aguardando largada...")
        
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

if __name__ == "__main__":
    asyncio.run(trabalhar())