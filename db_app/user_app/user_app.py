from flask import jsonify, Blueprint
from flask import request
from db_app.executor import *
import urlparse

app = Blueprint('user_app', __name__)


def serialize_user(user):
    user = user[0]
    resp = {
        'about': user[2],
        'email': user[1],
        'id': user[0],
        'isAnonymous': bool(user[3]),
        'name': user[4],
        'username': user[5]
    }
    return resp


def __parse_user_request_data(json_data):
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
    res = __parse_user_request_data(user_data)
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


@app.route('/details/', methods=['GET'])
def details():
    #TODO add followers and subscriptions
    qs = urlparse.urlparse(request.url).query
    mail = urlparse.parse_qs(qs)
    user_mail = mail["user"]
    select_stmt = (
        'SELECT id, email, about, isAnonymous, name, username FROM Users WHERE email = %s'
    )
    user = execute_select_one(select_stmt, user_mail)
    answer = jsonify({"code": 0, "response": serialize_user(user)})
    return answer


@app.route('/follow/', methods=['POST'])
def follow():
    user_data = request.json
    data = []
    try:
        data.append(user_data["follower"])
        data.append(user_data["followee"])
        #TODO: validate mail
    except KeyError:
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    insert_stmt = (
        'INSERT INTO Followers (follower_mail, followee_mail) '
        'VALUES (%s, %s)'
    )
    #TODO: validate user
    pair_id = execute_insert(insert_stmt, data)
    return jsonify({"code": 0, "response": pair_id})


@app.route('/unfollow/', methods=['POST'])
def unfollow():
    user_data = request.json
    data = []
    try:
        data.append(user_data["follower"])
        data.append(user_data["followee"])
        #TODO: validate mail
    except KeyError:
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    #TODO: validate user
    delete_stmt = ('DELETE FROM Followers WHERE follower_mail = % s AND followee_mail = % s')
    insert_id = execute_insert(delete_stmt, data)
    return jsonify({"code": 0, "response": insert_id})

@app.route('/updateProfile/', methods=['POST'])
def update():
    #TODO: validate, add followers and subscriptions
    user_data = request.json
    res = []
    try:
        res.append(user_data["about"])
        res.append(user_data["name"])
        res.append(user_data["user"])
    except KeyError:
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    update_stmt = ('UPDATE Users SET about = %s, name = %s WHERE email = %s')
    execute_insert(update_stmt, res)
    select_stmt = ('SELECT id, email, about, isAnonymous, name, username FROM Users WHERE email = %s')
    resp = execute_select_one(select_stmt, res[2])
    answer = jsonify({"code": 0, "response": serialize_user(resp)})
    return answer












