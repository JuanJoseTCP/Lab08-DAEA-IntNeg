import math
from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI, HTTPException

from persistence.kafka_consumer import start_consumer
from persistence.sql_postgres import test_postgres_connection, get_pg_server_connection
from persistence.sql_server import test_sql_server_connection, get_sql_server_connection

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Welcome to the FastAPI server!"}

@app.get("/recommendations/{user_id}")
def get_recommendations(user_id: str):
    try:
        pg_conn = get_pg_server_connection()
        sql_conn = get_sql_server_connection()

        # Obtener calificaciones del usuario de PostgreSQL
        cursor = pg_conn.cursor()
        cursor.execute("SELECT movie_id, rating FROM UserRatings WHERE user_id = %s", (user_id,))
        user_ratings = {movie_id: rating for movie_id, rating in cursor.fetchall()}
        pg_conn.close()

        if not user_ratings:
            raise HTTPException(status_code=404, detail="No ratings found for this user.")

        # Obtener calificaciones y detalles de películas de SQL Server
        cursor = sql_conn.cursor()
        cursor.execute("SELECT Ratings.UserID, Movies.MovieID, Ratings.Rating, Movies.Title, Genres FROM Ratings INNER JOIN Movies ON Ratings.MovieID = Movies.MovieID")
        db_ratings = cursor.fetchall()
        sql_conn.close()

        # Construir un diccionario de calificaciones con detalles de las películas
        db_ratings_dict = {}
        movie_details_dict = {}
        for uid, movie_id, rating, title, genres in db_ratings:
            if uid not in db_ratings_dict:
                db_ratings_dict[uid] = {}
            db_ratings_dict[uid][movie_id] = rating

            # Almacenar detalles de las películas
            movie_details_dict[movie_id] = {"title": title, "genres": genres}

        # Calcular similitudes
        similarities = []
        for other_user_id, other_user_ratings in db_ratings_dict.items():
            if other_user_id == user_id:
                continue
            
            pearson_similarity, _ = calculate_pearson_correlation(user_ratings, other_user_ratings)
            similarities.append((other_user_id, pearson_similarity))

        # Ordenar por similitud
        similarities.sort(key=lambda x: x[1], reverse=True)

        # Obtener recomendaciones
        recommended_movies = []
        for other_user_id, similarity in similarities:
            for movie_id in db_ratings_dict[other_user_id]:
                if movie_id not in user_ratings:  # Evitar recomendar películas ya vistas
                    recommended_movies.append({
                        "movie_id": movie_id,
                        "title": movie_details_dict[movie_id]["title"],
                        "genres": movie_details_dict[movie_id]["genres"]
                    })

        return {"recommendations": recommended_movies[:10]}  # Top 10 películas recomendadas

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching recommendations: {e}")

def calculate_pearson_correlation(user_ratings, other_user_ratings):
    common_movies = set(user_ratings.keys()) & set(other_user_ratings.keys())
    
    if len(common_movies) < 2:
        return 0, []
    
    # Calcular sumas necesarias
    sum_user = sum(user_ratings[movie_id] for movie_id in common_movies)
    sum_other = sum(other_user_ratings[movie_id] for movie_id in common_movies)
    
    sum_user_sq = sum(user_ratings[movie_id] ** 2 for movie_id in common_movies)
    sum_other_sq = sum(other_user_ratings[movie_id] ** 2 for movie_id in common_movies)
    
    sum_product = sum(user_ratings[movie_id] * other_user_ratings[movie_id] for movie_id in common_movies)

    # Número de elementos comunes
    n = len(common_movies)

    # Calcular la correlación de Pearson
    numerator = sum_product - (sum_user * sum_other / n)
    denominator = math.sqrt((sum_user_sq - (sum_user ** 2 / n)) * (sum_other_sq - (sum_other ** 2 / n)))

    if denominator == 0:
        return 0, []

    return numerator / denominator, common_movies

if __name__ == "__main__":
    import uvicorn
    start_consumer()
    test_postgres_connection()
    test_sql_server_connection()
    uvicorn.run(app, host="0.0.0.0", port=8000)
