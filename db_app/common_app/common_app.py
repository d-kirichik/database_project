from flask import jsonify, Blueprint
from db_app.executor import *

app = Blueprint('common_app', __name__)


@app.route('/status/', methods=['GET'])
def status():
    resp = []
    tables = ['Users', 'Threads', 'Forums', 'Posts']

    for t in tables:
        count = len(execute('SELECT id FROM ' + t))
        resp.append(count)

    json = {
        'user': resp[0],
        'thread': resp[1],
        'forum': resp[2],
        'post': resp[3]
    }
    return jsonify({"code": 0, "response": json})

