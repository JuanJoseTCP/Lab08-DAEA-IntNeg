CREATE DATABASE MovieLens;
GO

USE MovieLens;
GO

CREATE TABLE Movies (
    MovieID INT PRIMARY KEY,
    Title NVARCHAR(255),
    Genres NVARCHAR(255)
);

CREATE TABLE Ratings (
    UserID NVARCHAR(255),
    MovieID INT,
    Rating FLOAT,
    Timestamp BIGINT
);

CREATE TABLE Users (
    UserID NVARCHAR(255) PRIMARY KEY,
    Gender NVARCHAR(255),
    Age INT,
    Occupation INT,
    ZipCode NVARCHAR(255),
);

BULK INSERT Movies
FROM '/var/opt/mssql/app/data/movies.dat'
WITH (
    FIELDTERMINATOR = '::',
    ROWTERMINATOR = '\n',
    FIRSTROW = 1,
    TABLOCK
);

BULK INSERT Users
FROM '/var/opt/mssql/app/data/users.dat'
WITH (
    FIELDTERMINATOR = '::',
    ROWTERMINATOR = '\n',
    FIRSTROW = 1,
    TABLOCK
);

BULK INSERT Ratings
FROM '/var/opt/mssql/app/data/ratings.dat'
WITH (
    FIELDTERMINATOR = '::',
    ROWTERMINATOR = '\n',
    FIRSTROW = 1,
    TABLOCK
);
GO