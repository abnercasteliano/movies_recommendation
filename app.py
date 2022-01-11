import pandas as pd
from flask import Flask, render_template, request
import jsonify
import requests
from scipy.sparse import csr_matrix
from sklearn.neighbors import NearestNeighbors

# importando os dados
rating_popular_movie = pd.read_csv('popular_movies.csv')

# lista de filmes
movies = list(rating_popular_movie['title'].unique())

app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html', movies=movies)

@app.route('/predict', methods=['POST'])
def predict():
    #### POST ####
    if request.method == 'POST':
        rating_popular_movie = pd.read_csv('popular_movies.csv')
        # forms
        movie=request.form['movie']
        rate=request.form['rate']
        df2 = pd.DataFrame({'userId' : [611], 'movieId': [2], 'rating': [rate], 'title': [movie]}, dtype=float)
        rating_popular_movie = pd.concat([rating_popular_movie, df2], ignore_index=True, axis=0)

        # Tabela Pivot
        movie_features_df = rating_popular_movie.pivot_table(index='title',columns='userId',values='rating').fillna(0)
        
        # Criando uma matriz esparsa
        movie_features_df_matrix = csr_matrix(movie_features_df.values)

        # treinando o KNN
        model_knn = NearestNeighbors(metric = 'cosine', algorithm = 'brute')
        model_knn.fit(movie_features_df_matrix)

        # Gerando a lista dos filmes recomendados
        query_index = movie
        distances, indices = model_knn.kneighbors(movie_features_df.loc[query_index,:].values.reshape(1, -1), n_neighbors = 6)

        # Armazenando os valore em uma lista
        result = []
        for i in range(0, len(distances.flatten())):
            if i != 0:
                result.append(movie_features_df.index[indices.flatten()[i]])
        return render_template('index.html', movies=movies, prediction_texts=result)
    else:
        return render_template('index.html', movies=movies)

if __name__ == "__main__":
    app.run(debug=True)