from flask import jsonify, Blueprint
from flask import request
from db_app.executor import *

app = Blueprint('user_app', __name__)


def serialize_user(user):
    user = user[0]
    response = {
        'about': user[2],
        'email': user[1],
        'id': user[0],
        'isAnonymous': bool(user[3]),
        'name': user[4],
        'username': user[5]
    }
    return response


def parse_request_data(json_data):
    res = []
    try:
        res.append((json_data["username"]))
        res.append((json_data["about"]))
        res.append((json_data["name"]))
        res.append((json_data["email"]))
        try:
            res.append((json_data["isAnonymous"]))
        except KeyError:
            pass
    except KeyError:
        res = []
    return res


@app.route('/create/', methods=['POST'])
def create():
    user_data = request.json
    insert_stmt = ()
    data = ()
    res = parse_request_data(user_data)
    if(len(res) == 0):
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    select_stmt = ('SELECT id, email, about, isAnonymous, name, username FROM Users WHERE email = %s')
    usr = execute_select_one(select_stmt, res[3])
    if(len(usr) != 0):
        answer = {"code": 5, "response": "User already exists"}
        return jsonify(answer)
    if(len(res) == 4):
        insert_stmt = (
            'INSERT INTO Users (username, about, name, email) '
            'VALUES (%s, %s, %s, %s)'
        )
        data = (res[0], res[1], res[2], res[3])
    if(len(res) == 5):
        if(res[4] == "true"):
            res[4] = 1
        elif(res[4] == "false"):
            res[4] = 0
        insert_stmt = (
            'INSERT INTO Users (username, about, name, email, isAnonymous) '
            'VALUES (%s, %s, %s, %s, %s)'
        )
        data = (res[0], res[1], res[2], res[3], res[4])
    user_id = execute_insert(insert_stmt, data)
    select_stmt = ('SELECT id, email, about, isAnonymous, name, username FROM Users WHERE id = %s')
    resp = execute_select_one(select_stmt, user_id)
    answer = jsonify({"code": 0, "response": serialize_user(resp)})
    return answer

