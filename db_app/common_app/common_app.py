from flask import jsonify, Blueprint
from db_app.executor import *

app = Blueprint('common_app', __name__)


@app.route('/status/', methods=['GET'])
def status():
    resp = []
    tables = ['Users', 'Threads', 'Forums', 'Posts']

    for t in tables:
        count = len(execute_select_all('SELECT id FROM ' + t))
        resp.append(count)

    json = {
        'user': resp[0],
        'thread': resp[1],
        'forum': resp[2],
        'post': resp[3]
    }
    return jsonify({"code": 0, "response": json})


@app.route('/clear/', methods=['POST'])
def clear():
    set_stmt = ('SET FOREIGN_KEY_CHECKS=0')
    execute_insert(set_stmt, ())
    tables = ['Users', 'Threads', 'Forums', 'Posts', 'Followers', 'Subscriptions']
    for table in tables:
        del_stmt = ('TRUNCATE TABLE ')
        del_stmt += table
        execute_insert(del_stmt, ())
    set_stmt = ('SET FOREIGN_KEY_CHECKS=1')
    execute_insert(set_stmt, ())
    return jsonify({"code": 0, "response": "OK"})
