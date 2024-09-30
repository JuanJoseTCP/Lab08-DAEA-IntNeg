# Example Movies Voting App
A simple distributed application running across multiple instances, using AWS and Docker Play ground.

## Getting Started
This solution uses the next schema.
First instance:
   As you can see in the next image the first instance contains the flask,redis and .net these ones were implemented using EC2 on AWS. The flask container ask for the movieLens data (https://grouplens.org/datasets/movielens/).
   in this case we are using 1 millon data, so in order to show the information of the movies flask ask for the data and then renderized to the user.After the user select one or more movies.
   the information collected it's send to redis to keep it in cache and then the worker who has c# and .net container redirect the information to a kafka broker
Second instance:
   It's curious but to deploy the entire application we have to start with the broker cuz is the place where all data will go throught, so once we deployed the broker using a EC2 instance we are ready.
   to also in the same instance deploy the Sqlserver container where by using bulk and an init.sql with instructions we can migrate the .dat files. Once both containers are up we use the worker.
   in the first instance as producer alongs the broker.
Third instance:
    In the third instance just because we have the broker up now its possible to use the container that has a fastapi restful wich we use to subscribe on the broker so we are able to consume the rating,movieid and userid given by the user. With this information fastapi uses the pearson algorithm to find movies wich the user hasn't rating yet and with the information of the movies that he rated we provide similar movies to be rated. After this we store the values in postgresql.
Fourth instance:
    In the final step the express container consume the recomendation and shows the result on the /recomendations url.

## Architecture 
<img width="1150" alt="Captura de pantalla 2024-09-29 a la(s) 9 21 18 p  m" src="https://github.com/user-attachments/assets/60ebf39d-d631-4753-a4ef-007457447afe">
