from flask import Flask, render_template, request, jsonify, make_response, g
from flask_sqlalchemy import SQLAlchemy
from redis import Redis
import json
import random
import os
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

app = Flask(__name__)

# Obtener las credenciales desde las variables de entorno, usando valores por defecto si no están definidas
server = os.getenv('SQL_SERVER', 'localhost')  # Valor por defecto
database = os.getenv('SQL_DATABASE', 'MovieLens')  # Valor por defecto
username = os.getenv('SQL_USERNAME', 'SA')  # Valor por defecto
password = os.getenv('SQL_PASSWORD', 'StrongPass123!')  # Valor por defecto
redis_host = os.getenv('REDIS_HOST', 'localhost')  # Valor por defecto

connection_string = f'mssql+pyodbc://{username}:{password}@{server}/{database}?driver=ODBC+Driver+17+for+SQL+Server'

app.config['SQLALCHEMY_DATABASE_URI'] = connection_string
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Movie(db.Model):
    __tablename__ = 'movies'
    MovieID = db.Column(db.Integer, primary_key=True)
    Title = db.Column(db.String(255))
    Genres = db.Column(db.String(255))

def get_redis():
    if not hasattr(g, 'redis'):
        g.redis = Redis(host=redis_host, db=0, socket_timeout=5)
    return g.redis

@app.route("/")
def index():
    voter_id = request.cookies.get('voter_id')
    if not voter_id:
        voter_id = hex(random.getrandbits(64))[2:-1]

    page = request.args.get('page', 1, type=int)
    per_page = 10
    movies_paginate = db.paginate(db.select(Movie).order_by(Movie.MovieID), page=page, per_page=per_page)

    resp = make_response(render_template(
        'index.html', 
        movies=movies_paginate, 
        page=page
    ))
    resp.set_cookie('voter_id', voter_id)
    return resp

@app.route("/vote", methods=["POST"])
def vote():
    data = json.loads(request.data.decode('utf-8'))
    data["user_id"] = request.cookies.get("voter_id")
    redis = get_redis()
    redis.rpush('votes', json.dumps(data))
    return jsonify(
        status=201
    )

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=80, debug=True, threaded=True)
