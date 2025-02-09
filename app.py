from flask import Flask
app = Flask(__name__)

@app.route("/")
def hello_movies():
 return "Hello, this web app will provide more information about movies"

# if __name__ == "__main__":
#     app.run(host='0.0.0.0', port=80)