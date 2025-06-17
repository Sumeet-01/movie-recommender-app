from flask import Flask, render_template, request
from recommender import recommend

app = Flask(__name__)

@app.route("/", methods=["GET", "POST"])
def home():
    recommendations = []
    movie_title = ""

    if request.method == "POST":
        movie_title = request.form.get("movie")
        recommendations = recommend(movie_title)

    return render_template("index.html", movie=movie_title, results=recommendations)

if __name__ == "__main__":
    app.run(debug=True)
