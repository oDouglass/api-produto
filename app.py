from flask import Flask, jsonify, request
import requests

app = Flask(__name__)

# URL da API de estoque (pode ser alterada conforme o ambiente)
API_ESTOQUE_URL = 'http://localhost:5000'

# Rota para listar produtos (chama a API de estoque)
@app.route('/produtos', methods=['GET'])
def listar_produtos():
    try:
        resposta = requests.get(f'{API_ESTOQUE_URL}/produtos')
        return jsonify(resposta.json()), resposta.status_code
    except requests.exceptions.RequestException:
        return jsonify({'mensagem': 'Erro ao conectar com a API de estoque.'}), 500

@app.route('/produtos', methods=['POST'])
def adicionar_produto():
    try:
        dados = request.json
        resposta = requests.post(f'{API_ESTOQUE_URL}/produtos', json=dados)
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
        return jsonify(resposta.json()), resposta.status_code
    except requests.exceptions.RequestException:
        return jsonify({'mensagem': 'Erro ao conectar com a API de estoque.'}), 500

@app.route('/produtos/<int:produto_id>', methods=['DELETE'])
def deletar_produto(produto_id):
    try:
        resposta = requests.delete(f'{API_ESTOQUE_URL}/produtos/{produto_id}')
        return jsonify(resposta.json()), resposta.status_code
    except requests.exceptions.RequestException:
        return jsonify({'mensagem': 'Erro ao conectar com a API de estoque.'}), 500


@app.route('/')
def home():
    return 'API de Varejo - Consome a API de Estoque'

if __name__ == '__main__':
    app.run(port=5001, debug=True)
