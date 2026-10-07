from collections import Counter
import json
import random
import ssl
import time
import paho.mqtt.client as mqtt

# --- CONFIGURAÇÕES DE REDE ---
BROKER = "localhost"
PORT = 1883
TOPICO_TAREFAS = "pfitscher/tarefas"
TOPICO_RESPOSTAS = "pfitscher/respostas"
TOPICO_ANUNCIO = "pfitscher/anuncio"


def gerar_serie_aleatoria():
    inicio = random.randint(1, 10)
    razao = random.randint(2, 5)
    serie = [inicio]
    for _ in range(3):
        serie.append(serie[-1] * razao)
    return serie


def ao_receber_resposta(client, userdata, msg):
    """Callback executado quando uma resposta chega ao tópico de respostas."""
    # 1. Medição de alta precisão da recepção
    t_chegada_perf = time.perf_counter()

    try:
        dados = json.loads(msg.payload.decode("utf-8"))
        task_id_atual = userdata.get("task_id")

        if str(dados.get("task id")) == task_id_atual:
            # 2. Calcula a latência exata usando o perf_counter do envio
            t_envio_perf = userdata.get("t_envio_perf", t_chegada_perf)
            latencia_ms = (t_chegada_perf - t_envio_perf) * 1000

            userdata["respostas_recebidas"].append(
                {
                    "computed_value": dados["computed_value"],
                    "latencia": latencia_ms,
                    "worker_id": dados.get("worker_id", "Desconhecido"),
                }
            )
            print(
                f"[Orquestrador] Resposta de '{dados.get('worker_id')}':"
                f" {dados['computed_value']} | Delay: {latencia_ms:.3f} ms"
            )
    except Exception as e:
        print(f"[Orquestrador] Erro ao processar mensagem recebida: {e}")


def processar_resultados(respostas_recebidas):
    """Analisa o consenso das respostas recebidas e define o vencedor."""
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
    # 1. Preparação da Rodada e Estado do Orquestrador
    task_id = str(random.randint(10000, 99999))
    reward = random.randint(5, 100)
    data_series = gerar_serie_aleatoria()
    respostas_recebidas = []

    # Dicionário de estado passado para o MQTT
    userdata_dict = {
        "task_id": task_id,
        "respostas_recebidas": respostas_recebidas,
    }

    # 2. Configuração do Cliente MQTT
    cliente = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id="Orquestrador_01",
        userdata=userdata_dict,
    )

    cliente.on_message = ao_receber_resposta

    # 3. Conexão MQTTS
    print("[Orquestrador] Conectando ao broker Mosquitto...")
    #  cliente.tls_set(ca_certs="ca.crt", cert_reqs=ssl.CERT_NONE)
    #  cliente.tls_insecure_set(True)
    cliente.connect(BROKER, PORT, keepalive=60)
    cliente.subscribe(TOPICO_RESPOSTAS)

    cliente.loop_start()
    time.sleep(1)  # Estabilização da conexão e inscrição

    # 4. Envio da Tarefa
    print(f"\n--- INICIANDO RODADA (TASK ID: {task_id}) ---")
    print(f"[Orquestrador] Série enviada: {data_series}")

    # 3. Separação das medições
    t_envio_unix = time.time() * 1000  # Mantém o padrão no payload JSON
    t_envio_perf = time.perf_counter()  # Usado para o cálculo interno do Python

    task_request = {
        "task id": task_id,
        "data_series": data_series,
        "reward": reward,
        "timestamp_sent": t_envio_unix,
    }

    userdata_dict["t_envio_perf"] = t_envio_perf

    # Publica a mensagem imediatamente após pegar o perf_counter
    cliente.publish(TOPICO_TAREFAS, json.dumps(task_request))

    # 5. Janela de Espera pelas Respostas dos Workers
    time.sleep(3)

    # 6. Avaliação e Anúncio do Vencedor
    vencedor = processar_resultados(respostas_recebidas)
    if vencedor:
        anuncio = {
            "task id": task_id,
            "ganhou": True,
            "reward coins": reward,
            "vencedor_id": vencedor["worker_id"],
        }
        cliente.publish(TOPICO_ANUNCIO, json.dumps(anuncio))

    # 7. Finalização da Conexão
    time.sleep(0.5)
    cliente.loop_stop()
    cliente.disconnect()
    print("[Orquestrador] Execução encerrada.")


if __name__ == "__main__":
    main()