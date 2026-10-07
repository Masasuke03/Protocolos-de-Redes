from flask import Flask, request, jsonify
import sys

app = Flask(__name__)

porta_worker = int(sys.argv[1]) 

def calcular_predicao(series):
    if len(series) < 2:
        return 0.0
    penultimo = series[-2]
    ultimo = series[-1]
    razao = ultimo / penultimo
    proximo_valor = ultimo * razao
    return proximo_valor

@app.route('/tarefa', methods=['POST'])
def processar_tarefa():
    dados = request.get_json()

    # Leitura das chaves padronizadas
    task_id = dados.get('task_id')
    serie = dados.get('desafio', [])

    print(f"[Porta {porta_worker}] Recebendo tarefa {task_id}: {serie}")

    proximo = calcular_predicao(serie)

    # Resposta idêntica à do Socket
    resposta = {
        "resposta": proximo
    }
    return jsonify(resposta), 200

@app.route('/anuncio', methods=['POST'])
def processar_anuncio():
    dados = request.get_json()
    
    # Processamento do anúncio de resultado
    if dados.get("ganhou"):
        print(f"[Porta {porta_worker}] Recebi {dados.get('reward_coins')} Pfitscher Coins!")
    else:
        print(f"[Porta {porta_worker}] Perdi.")

    return jsonify({"status": "recebido"}), 200

if __name__ == '__main__':
    print(f"Iniciando Worker HTTP na porta {porta_worker}...")
    app.run(host='127.0.0.1', port=porta_worker)