from collections import Counter
import json
import random
import ssl
import time
import paho.mqtt.client as mqtt

# --- CONFIGURAÇÕES DE REDE ---
BROKER = "127.0.0.1"
PORT = 8883  # Porta MQTTS com TLS
TOPICO_TAREFAS = "pfitscher/tarefas"
TOPICO_RESPOSTAS = "pfitscher/respostas"
TOPICO_ANUNCIO = "pfitscher/anuncio"

def ao_receber_resposta(client, userdata, msg):
    t_chegada_perf = time.perf_counter()

    try:
        dados = json.loads(msg.payload.decode("utf-8"))
        task_id_atual = userdata.get("task_id")

        if str(dados.get("task_id")) == task_id_atual:
            t_envio_perf = userdata.get("t_envio_perf", t_chegada_perf)
            latencia_ms = (t_chegada_perf - t_envio_perf) * 1000

            userdata["respostas_recebidas"].append({
                "computed_value": dados.get("resposta"),
                "latencia": latencia_ms,
                "worker_id": dados.get("worker_id", "Desconhecido"),
            })
            print(
                f"[Orquestrador] Resposta de '{dados.get('worker_id')}':"
                f" {dados.get('resposta')} | Delay: {latencia_ms:.3f} ms"
            )
    except Exception as e:
        print(f"[Orquestrador] Erro ao processar mensagem recebida: {e}")

def processar_resultados(respostas_recebidas):
    print("\n--- RESULTADO DA CORRIDA ---")
    if not respostas_recebidas:
        print("Nenhuma resposta recebida dentro do tempo limite.")
        return None

    valores = [r["computed_value"] for r in respostas_recebidas]
    maioria = Counter(valores).most_common(1)[0][0]
    print(f"Resposta da maioria (consenso): {maioria}")

    respostas_validas = [
        r for r in respostas_recebidas if r["computed_value"] == maioria
    ]

    if respostas_validas:
        vencedor = min(respostas_validas, key=lambda x: x["latencia"])
        print(
            f"VENCEDOR: {vencedor['worker_id']} com latência de"
            f" {vencedor['latencia']:.3f} ms"
        )
        return vencedor

    return None

def main():
    task_id = "12345"
    data_series = [2, 4, 8, 16]
    respostas_recebidas = []

    userdata_dict = {
        "task_id": task_id,
        "respostas_recebidas": respostas_recebidas,
    }

    cliente = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id="Orquestrador_01",
        userdata=userdata_dict,
    )

    cliente.on_message = ao_receber_resposta

    # --- ATIVAÇÃO DO TLS ---
    cliente.tls_set(ca_certs="ca.crt", cert_reqs=ssl.CERT_NONE)
    cliente.tls_insecure_set(True)

    print("[Orquestrador] Conectando ao broker Mosquitto via TLS (porta 8883)...")
    cliente.connect(BROKER, PORT, keepalive=60)
    cliente.subscribe(TOPICO_RESPOSTAS)

    cliente.loop_start()
    time.sleep(1)

    print(f"\n--- INICIANDO RODADA (TASK ID: {task_id}) ---")
    print(f"[Orquestrador] Série enviada: {data_series}")

    task_request = {
        "desafio": data_series,
        "task_id": task_id
    }

    t_envio_perf = time.perf_counter()
    userdata_dict["t_envio_perf"] = t_envio_perf

    cliente.publish(TOPICO_TAREFAS, json.dumps(task_request))

    time.sleep(2)

    vencedor = processar_resultados(respostas_recebidas)
    
    if vencedor:
        anuncio = {
            "task_id": task_id,
            "ganhou": True,
            "reward_coins": 50,
            "vencedor_id": vencedor["worker_id"],
        }
        cliente.publish(TOPICO_ANUNCIO, json.dumps(anuncio))

    time.sleep(0.5)
    cliente.loop_stop()
    cliente.disconnect()
    print("[Orquestrador] Execução encerrada.")

if __name__ == "__main__":
    main()