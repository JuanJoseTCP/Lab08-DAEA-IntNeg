from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import pymssql
import os
import math 
from dotenv import load_dotenv

# Cargar las variables de entorno desde el archivo .env
load_dotenv()

app = FastAPI()

MSSQL_SERVER = os.getenv('SQL_SERVER', 'localhost')
MSSQL_DATABASE = os.getenv('SQL_DATABASE', 'MovieLens')
MSSQL_USERNAME = os.getenv('SQL_USERNAME', 'SA')
MSSQL_PASSWORD = os.getenv('SQL_PASSWORD', 'StrongPass123!')

PG_SERVER = os.getenv('PG_SERVER', 'localhost')
PG_DATABASE = os.getenv('PG_DATABASE', 'MovieLens')
PG_USERNAME = os.getenv('PG_USERNAME', 'SA')
PG_PASSWORD = os.getenv('PG_PASSWORD', 'StrongPass123!')

@app.get("/")
def read_root():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE'")
        tables = cursor.fetchall()
        conn.close()
        return {"tables": [table[0] for table in tables]}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching tables: {e}")

def get_db_connection():
    try:
        conn = pymssql.connect(
            server=SQL_SERVER_HOST,
            user=USERNAME,
            password=PASSWORD,
            database=DATABASE_NAME,
            port=1433
        )
        return conn
    except pymssql.OperationalError as e:
        raise HTTPException(status_code=500, detail=f"Database connection failed: {e}")

class Rating(BaseModel):
    user_id: int
    movie_id: int
    rating: float
    
@app.post("/recommendations/")
def get_recommendations(ratings: list[Rating]):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT UserID, MovieID, Rating FROM Ratings")
        db_ratings = cursor.fetchall()
        conn.close()
        
        db_ratings_dict = {}
        for user_id, movie_id, rating in db_ratings:
            if user_id not in db_ratings_dict:
                db_ratings_dict[user_id] = {}
            db_ratings_dict[user_id][movie_id] = rating
        
        similarities = []
        for user_id, user_ratings in db_ratings_dict.items():
            manhattan_similarity, manhattan_similar_ratings = calculate_manhattan_similarity(ratings, user_ratings)
            pearson_similarity, pearson_similar_ratings = calculate_pearson_correlation(ratings, user_ratings)
            euclidean_similarity, euclidean_similar_ratings = calculate_euclidean_distance(ratings, user_ratings)
            similarities.append((user_id, manhattan_similarity, pearson_similarity, euclidean_similarity, manhattan_similar_ratings, pearson_similar_ratings, euclidean_similar_ratings))
        
        similarities.sort(key=lambda x: (x[1], x[2], x[3]), reverse=True)
        
        return {"recommendations": similarities[:10]}  # Top 10 similar users
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recommendations: {e}")


def calculate_manhattan_similarity(ratings, user_ratings):
    distance = 0
    similar_ratings = []
    for rating in ratings:
        if rating.movie_id in user_ratings:
            distance += abs(rating.rating - user_ratings[rating.movie_id])
            similar_ratings.append((rating.user_id, rating.movie_id, user_ratings[rating.movie_id]))
    return distance, similar_ratings

def calculate_pearson_correlation(ratings, user_ratings):
    common_ratings = [(rating.rating, user_ratings[rating.movie_id]) for rating in ratings if rating.movie_id in user_ratings]
    
    if len(common_ratings) < 2:
        return 0, []
    
    ratings_a, ratings_b = zip(*common_ratings)
    mean_a = sum(ratings_a) / len(ratings_a)
    mean_b = sum(ratings_b) / len(ratings_b)
    
    numerator = sum((a - mean_a) * (b - mean_b) for a, b in common_ratings)
    denominator_a = math.sqrt(sum((a - mean_a) ** 2 for a in ratings_a))
    denominator_b = math.sqrt(sum((b - mean_b) ** 2 for b in ratings_b))
    
    if denominator_a == 0 or denominator_b == 0:
        return 0, common_ratings
    
    return numerator / (denominator_a * denominator_b), common_ratings

def calculate_euclidean_distance(ratings, user_ratings):
    distance = 0
    similar_ratings = []
    for rating in ratings:
        if rating.movie_id in user_ratings:
            distance += (rating.rating - user_ratings[rating.movie_id]) ** 2
            similar_ratings.append((rating.user_id, rating.movie_id, user_ratings[rating.movie_id]))
    return math.sqrt(distance), similar_ratings






