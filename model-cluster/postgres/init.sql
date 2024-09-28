CREATE TABLE UserRatings (
  user_id VARCHAR(50) NOT NULL,
  movie_id INTEGER NOT NULL,
  rating INTEGER CHECK (rating >= 1 AND rating <= 5),
  PRIMARY KEY (user_id, movie_id)
);