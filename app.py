from flask import Flask
from routes.search import search_bp
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

app.register_blueprint(search_bp)

if __name__ == "__main__":
    app.run(debug=True)
