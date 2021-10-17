import json
import uuid
from datetime import timedelta

from flask import Flask, request

from routers.sign import sign
from routers.user import user
from routers.article import article

app = Flask(__name__)
app.register_blueprint(user)
app.register_blueprint(sign)
app.register_blueprint(article)
app.config['SECRET_KEY'] = str(uuid.uuid4())
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(days=1)


@app.route('/')
def index():
    return 'Welcome to Exprimere API!'


if __name__ == '__main__':
    app.run()
