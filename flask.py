from flask import Flask, request, jsonify
from elasticsearch import Elasticsearch

app = Flask(__name__)
es = Elasticsearch(hosts=["http://localhost:9200"])

@app.route('/')
def home():
    return "Welcome to the Flask Search App"


@app.route('/search', methods=['GET'])
def search():
    query = request.args.get('q')
    if not query:
        return jsonify([])

    res = es.search(index="food_index", body={
        "query": {
            "multi_match": {
                "query": query,
                "fields": ["name", "recipe", "description"]
            }
        }
    })
    return jsonify(res['hits']['hits'])

def create_index():
    es.indices.create(index='food_index', body={
        "mappings": {
            "properties": {
                "name": { "type": "text" },
                "recipe": { "type": "text" },
                "video": { "type": "text" },
                "description": { "type": "text" }
            }
        }
    }, ignore=400)

def index_data():
    food_data = [
        {
            "name": "Pasta",
            "recipe": "Boil water, add pasta, cook for 10 minutes.",
            "video": "http://example.com/video",
            "description": "A classic Italian dish."
        },
        {
            "name": "Pizza",
            "recipe": "Preheat oven, add toppings, bake for 15 minutes.",
            "video": "http://example.com/video2",
            "description": "A popular Italian dish."
        }
    ]

    for food in food_data:
        es.index(index="food_index", body=food)
