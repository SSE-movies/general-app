from flask import Flask, render_template

app = Flask(
    __name__, template_folder="src/templates", static_folder="src/static"
)


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/search")
def search():
    """Route to search for a movie"""
    # return render_template("search.html")
    return


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
