from flask import Flask, request, render_template, send_from_directory, jsonify, redirect, url_for
from elasticsearch import Elasticsearch
import os

app = Flask(__name__, template_folder='../templates', static_folder='../static')
es = Elasticsearch(
    [{'host': 'localhost', 'port': 9200, 'scheme': 'http'}]
)

@app.route('/')
def index():
    return render_template('search.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        # 无论用户名和密码是什么，都重定向到搜索页面
        return redirect(url_for('index'))
    return render_template('login.html')

@app.route('/logout')
def logout():
    return redirect(url_for('login'))

@app.route('/search', methods=['GET'])
def search_recipe():
    query = request.args.get('q')
    response = es.search(
        index="recipes",
        body={
            "query": {
                "match": {
                    "strMeal": query
                }
            }
        }
    )
    hits = response['hits']['hits']
    return render_template('search_results.html', hits=hits, query=query)

@app.route('/meals', methods=['GET'])
def list_meals():
    response = es.search(
        index="recipes",
        body={
            "query": {
                "match_all": {}
            },
            "size": 1000  # Adjust the size according to your data volume
        }
    )
    hits = response['hits']['hits']
    meals = [hit['_source']['strMeal'] for hit in hits]
    return jsonify(meals)

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static', 'image'),
                               'favicon.png', mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)
