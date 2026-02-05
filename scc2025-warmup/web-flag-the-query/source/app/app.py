import os
import json
from flask import Flask, request, jsonify, render_template
from flask_pymongo import PyMongo
from bson.json_util import dumps

app = Flask(__name__)

app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://<username>:<pass>@mongo:27017/scc_books_challenge?authSource=admin")
mongo = PyMongo(app)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/query', methods=['GET'])
def query():
    search_param = request.args.get('search', '')

    try:
        search_object = json.loads(search_param)
        query = {"title": search_object} 
        query_print = {"title": search_object}
    except json.JSONDecodeError:
        query = {"title": {"$regex": search_param, "$options": "i"}}
        query_print = {"title": search_param}
    try:
        result_cursor = mongo.db.books.find(query)
        results = list(result_cursor)
        return dumps({
            "received_query": query_print,
            "results": results
        })
    except Exception as e:
        print(f"Query execution failed: {str(e)}")
        return {"error": f"Query execution failed. Please try again {query_print}"}, 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=1331, debug=True)
