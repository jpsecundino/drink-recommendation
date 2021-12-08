from flask import Flask
from cocktail_recommendation import recommend

app = Flask(__name__)


@app.route('/')
def hello():
    print('hello world!')

@app.route('/<id>')
def recommend_cocktail(id):
    return recommend(int(id))


if __name__ == '__main__':
    app.run()
