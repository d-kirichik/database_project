from flask import jsonify, Blueprint

app = Blueprint('user_app', __name__)


@app.route('/details/', methods=['GET'])
def details():

    return jsonify({"code": 0, "response": "!"})
