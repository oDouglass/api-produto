from flask import Flask, jsonify, request
import requests
import redis
import json

app = Flask(__name__)

API_ESTOQUE_URL = 'http://localhost:5000'
API_DESCONTOS_URL = 'http://localhost:3000'

client = redis.Redis(host='localhost', port=6379, decode_responses=True)
  
@app.route('/produtos', methods=['GET'])
def listar_produtos():
    try:
        cache_key = "produtos:lista"
        data = client.get(cache_key)

        if data:
            produtos = json.loads(data)
            # print("[CACHE] Lista de produtos recuperada do Redis")
        else:
            resposta = requests.get(f'{API_ESTOQUE_URL}/produtos')
            produtos = resposta.json()
            client.set(cache_key, json.dumps(produtos), ex=60)
            print("[API] Lista de produtos recuperada da API e armazenada no Redis")

        return jsonify({ 
            "from_cache": True,
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
        else:
            resposta = requests.get(f'{API_DESCONTOS_URL}/produtos-desconto')
            descontos = resposta.json()
            client.set(cache_key, json.dumps(descontos), ex=60)
            print("[API] Lista de descontos recuperada da API descontos e armazenada no Redis")

        return jsonify({
            "from_cache": True,
            "produtos": descontos  
            }), 200
    except requests.exceptions.RequestException:
        return jsonify({'mensagem': 'Erro ao conectar com a API de descontos.'}), 500
   
@app.route('/produtos', methods=['POST'])
def adicionar_produto():
    try:
        dados = request.json
        resposta = requests.post(f'{API_ESTOQUE_URL}/produtos', json=dados)

        # invalidar o cache da lista
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

        #Invalidar o cache
        client.delete(f"produto:{produto_id}")
        client.delete("produtos:lista")

        return jsonify(resposta.json()), resposta.status_code
    except requests.exceptions.RequestException:
        return jsonify({'mensagem': 'Erro ao conectar com a API de estoque.'}), 500

@app.route('/produtos/<int:produto_id>', methods=['DELETE'])
def deletar_produto(produto_id):
    try:
        resposta = requests.delete(f'{API_ESTOQUE_URL}/produtos/{produto_id}')

        #Invalidar o cache
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
