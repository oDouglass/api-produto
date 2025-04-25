from flask import Flask, jsonify, request
import requests
import redis
import json

app = Flask(__name__)

API_ESTOQUE_URL = 'http://localhost:5000'
API_DESCONTOS_URL = 'http://localhost:3000'

CACHE_KEY = "produtos_cache"
CACHE_TIMEOUT = 60  # segundos

client = redis.Redis(host='localhost', port=6379, decode_responses=True)

@app.route('/produtos', methods=['GET'])
def listar_produtos():
    try:
        cache_key = "produtos:lista"
        data = client.get(cache_key)

        if data:
            produtos = json.loads(data)
            cached = True
            print("[CACHE] Lista de produtos recuperada do Redis")
        else:
            produtos = None
            cached = False
            resposta = requests.get(f'{API_ESTOQUE_URL}/produtos')
            if resposta.status_code == 200:
                produtos = resposta.json()
                client.set(cache_key, json.dumps(produtos), ex=CACHE_TIMEOUT)
                print("[API] Lista de produtos recuperada da API e armazenada no Redis")
            else:
                return jsonify({'mensagem': 'Erro ao conectar com a API de estoque.'}), 500

        return jsonify({ 
            "from_cache": cached,
            "produtos": produtos
        }), 200
    except requests.exceptions.RequestException:
        return jsonify({'mensagem': 'Erro ao conectar com a API de estoque.'}), 500

@app.route('/desconto', methods=['GET'])
def listar_descontos():
    try:
        cache_key = "descontos:lista"
        data = client.get(cache_key)

        if data:
            descontos = json.loads(data)
            print("[CACHE] Lista de descontos recuperadas do Redis")
            cached = True
        else:
            descontos = None
            cached = False
            resposta = requests.get(f'{API_DESCONTOS_URL}/produtos-desconto')
            if resposta.status_code == 200:
                descontos = resposta.json()
                client.set(cache_key, json.dumps(descontos), ex=CACHE_TIMEOUT)
                print("[API] Lista de descontos recuperada da API e armazenada no Redis")
            else:
                return jsonify({'mensagem': 'Erro ao conectar com a API de descontos.'}), 500

        return jsonify({
            "from_cache": cached,
            "produtos": descontos  
        }), 200
    except requests.exceptions.RequestException:
        return jsonify({'mensagem': 'Erro ao conectar com a API de descontos.'}), 500

@app.route('/produtos', methods=['POST'])
def adicionar_produto():
    try:
        dados = request.json
        resposta = requests.post(f'{API_ESTOQUE_URL}/produtos', json=dados)

        # invalidar o cache da lista de produtos
        client.delete("produtos:lista")

        return jsonify(resposta.json()), resposta.status_code
    except requests.exceptions.RequestException:
        return jsonify({'mensagem': 'Erro ao conectar com a API de estoque.'}), 500

@app.route('/produtos/<int:produto_id>', methods=['GET'])
def obter_produto(produto_id):
    try:
        resposta = requests.get(f'{API_ESTOQUE_URL}/produtos/{produto_id}')
        return jsonify(resposta.json()), resposta.status_code
    except requests.exceptions.RequestException:
        return jsonify({'mensagem': 'Erro ao conectar com a API de estoque.'}), 500

@app.route('/produtos/<int:produto_id>', methods=['PUT'])
def atualizar_produto(produto_id):
    try:
        dados = request.json
        resposta = requests.put(f'{API_ESTOQUE_URL}/produtos/{produto_id}', json=dados)

        # Invalidar o cache da lista de produtos e do produto específico
        client.delete(f"produto:{produto_id}")
        client.delete("produtos:lista")

        return jsonify(resposta.json()), resposta.status_code
    except requests.exceptions.RequestException:
        return jsonify({'mensagem': 'Erro ao conectar com a API de estoque.'}), 500

@app.route('/produtos/<int:produto_id>', methods=['DELETE'])
def deletar_produto(produto_id):
    try:
        resposta = requests.delete(f'{API_ESTOQUE_URL}/produtos/{produto_id}')

        # Invalidar o cache do produto específico e da lista de produtos
        client.delete(f"produto:{produto_id}")
        client.delete("produtos:lista")

        return jsonify(resposta.json()), resposta.status_code
    except requests.exceptions.RequestException:
        return jsonify({'mensagem': 'Erro ao conectar com a API de estoque.'}), 500

@app.route('/')
def home():
    return 'API de Varejo com Redis Cache ativo - Consome a API de Estoque e API de Descontos'

if __name__ == '__main__':
    app.run(port=5001, debug=True)
