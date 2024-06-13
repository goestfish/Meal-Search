import requests
from elasticsearch import Elasticsearch, helpers

es = Elasticsearch(
    [{'host': 'localhost', 'port': 9200, 'scheme': 'http'}]
)


def fetch_and_index_recipes():
    url = "https://www.themealdb.com/api/json/v1/1/search.php?s="
    response = requests.get(url)
    recipes = response.json()['meals']

    actions = [
        {
            "_index": "recipes",
            "_id": recipe["idMeal"],
            "_source": recipe
        }
        for recipe in recipes
    ]

    helpers.bulk(es, actions)


if __name__ == "__main__":
    fetch_and_index_recipes()
    print("Recipes indexed successfully.")
