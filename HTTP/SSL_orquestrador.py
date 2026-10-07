import asyncio
from collections import Counter
import random
import aiohttp
import ssl
import time

worker_ports = ["https://127.0.0.1:5001", "https://127.0.0.1:5002"]

def gerar_serie_aleatoria():
    inicio = random.randint(1, 10)
    razao = random.randint(2, 5)
    serie = [inicio]
    for _ in range(3):
        serie.append(serie[-1] * razao)
    return serie

async def enviar_tarefa(session, url, payload):
    t_envio_perf = time.perf_counter()

    try: 
        async with session.post(f"{url}/tarefa", json=payload) as response:
            resposta_json = await response.json()
            t_retorno_perf = time.perf_counter()
            latencia_ms = (t_retorno_perf - t_envio_perf) * 1000

            return {
                "worker_url": url,
                "valor": resposta_json.get("resposta"),
                "tempo": latencia_ms
            }
    except Exception as e:
        print(f"[Aviso] Erro ao enviar tarefa para {url}: {e}")
        return None

async def enviar_anuncio(session, url, payload):
    try:
        async with session.post(f"{url}/anuncio", json=payload) as response:
            await response.json()
    except Exception as e:
        print(f"[Aviso] Erro ao enviar anúncio para {url}: {e}")

async def main():
    task_id = "12345"
    serie = [2, 4, 8, 16]

    payload = {
        "desafio": serie,
        "task_id": task_id
    }

    print(f"\nINICIANDO A RODADA HTTPS/TLS - TASK ID: {task_id}")
    print(f"[Orquestrador] Enviando tarefa para os workers: {serie}")

    # Ignora a verificação do certificado adhoc gerado pelo Flask
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False
    ssl_context.verify_mode = ssl.CERT_NONE

    connector = aiohttp.TCPConnector(ssl=ssl_context)

    async with aiohttp.ClientSession(connector=connector) as session:
        tasks_pendentes = [enviar_tarefa(session, url, payload) for url in worker_ports]
        resultados = await asyncio.gather(*tasks_pendentes)
        respostas_validas = [res for res in resultados if res is not None]

        if not respostas_validas:
            print("[Orquestrador] Nenhum worker respondeu à tarefa.")
            return

        print("\n--- RESULTADO DA CORRIDA ---")
        for r in respostas_validas:
            porta = r['worker_url'].split(':')[-1]
            print(f"Trabalhador Porta {porta} | Resposta: {r['valor']} | Tempo: {r['tempo']:.2f} ms")

        valores = [r["valor"] for r in respostas_validas]
        url_vencedor = None
        try:
            moda = Counter(valores).most_common(1)[0][0]
            print(f"\n[Consenso] A resposta da maioria é: {moda}")

            acertadores = [r for r in respostas_validas if r["valor"] == moda]
            acertadores.sort(key=lambda x: x["tempo"])
            vencedor = acertadores[0]
            url_vencedor = vencedor['worker_url']

            porta_vencedora = url_vencedor.split(':')[-1]
            print(f"VENCEDOR: Porta {porta_vencedora} com {vencedor['tempo']:.2f} ms!")
        except Exception:
            print("\n[Empate Total] Nenhuma resposta formou maioria absoluta.")

        print("\nEnviando Winner Announcement e encerrando...")
        tarefa_anuncio = []
        for url in worker_ports:
            ganhou = (url == url_vencedor)
            anuncio_payload = {
                "task_id": task_id,
                "ganhou": ganhou,
                "reward_coins": 50 if ganhou else 0
            }
            tarefa_anuncio.append(enviar_anuncio(session, url, anuncio_payload))

        await asyncio.gather(*tarefa_anuncio)
        print("\n[Orquestrador] TAREFA HTTPS FINALIZADA\n")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n[Aviso] Execução interrompida pelo usuário.")