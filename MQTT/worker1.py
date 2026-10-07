import json
import time
import paho.mqtt.client as mqtt

# --- CONFIGURAÇÕES ---
BROKER = "127.0.0.1"
PORT = 1883
WORKER_ID = "Worker_01"  

TOPICO_TAREFAS = "pfitscher/tarefas"
TOPICO_RESPOSTAS = "pfitscher/respostas"
TOPICO_ANUNCIO = "pfitscher/anuncio"

def processar_tarefa(client, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        task_id = payload.get("task_id") or payload.get("task id")
        data_series = payload.get("desafio") or payload.get("data_series", [])

        print(f"\n[{WORKER_ID}] Tarefa recebida (ID: {task_id}): {data_series}")

        # Simulação de processamento da tarefa
        resposta = {
            "resposta": 32.0,
            "worker_id": WORKER_ID,
            "task_id": task_id
        }

        client.publish(TOPICO_RESPOSTAS, json.dumps(resposta))
        print(f"[{WORKER_ID}] Resposta enviada: 32.0")

    except Exception as e:
        print(f"[{WORKER_ID}] Erro ao processar tarefa: {e}")

def processar_anuncio(client, msg):
    try:
        payload = json.loads(msg.payload.decode("utf-8"))
        
        if payload.get("ganhou") or payload.get("vencedor_id") == WORKER_ID:
            reward = payload.get("reward_coins") or payload.get("reward coins", 50)
            print(f"[{WORKER_ID}] Recebi {reward} Pfitscher Coins!")
        else:
            print(f"[{WORKER_ID}] Perdi.")

    except Exception as e:
        print(f"[{WORKER_ID}] Erro ao processar anúncio: {e}")

def ao_receber_mensagem(client, userdata, msg):
    if msg.topic == TOPICO_TAREFAS:
        processar_tarefa(client, msg)
    elif msg.topic == TOPICO_ANUNCIO:
        processar_anuncio(client, msg)

def ao_conectar(client, userdata, flags, rc, properties=None):
    if rc == 0:
        print(f"[{WORKER_ID}] Conectado ao broker Mosquitto (Sem TLS)!")
        client.subscribe([(TOPICO_TAREFAS, 0), (TOPICO_ANUNCIO, 0)])
        print(f"[{WORKER_ID}] Aguardando tarefas em '{TOPICO_TAREFAS}'...")
    else:
        print(f"[{WORKER_ID}] Falha na conexão. Código de retorno: {rc}")

cliente = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2, client_id=WORKER_ID)
cliente.on_connect = ao_conectar
cliente.on_message = ao_receber_mensagem

print(f"[{WORKER_ID}] Conectando ao broker em {BROKER}:{PORT}...")
cliente.connect(BROKER, PORT, keepalive=60)
cliente.loop_forever()