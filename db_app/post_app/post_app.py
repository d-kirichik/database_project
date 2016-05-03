from flask import Blueprint
from flask import request, jsonify
from db_app.executor import *

app = Blueprint('post_app', __name__)


def serialize_post(post, post_id):
    resp = {
        'date': post[0],
        'forum': post[4],
        'id': post_id,
        'isApproved': bool(post[6]),
        'isDeleted': bool(post[10]),
        'isEdited': bool(post[8]),
        'isHighlighted': bool(post[7]),
        'isSpam': bool(post[9]),
        'message': post[2],
        'parent': post[5],
        'thread': post[1],
        'user': post[3]
    }
    return resp


def parse_post_data(json_data):
    res = []
    try:
        res.append(json_data["date"])
        res.append(json_data["thread"])
        res.append(json_data["message"])
        res.append(json_data["user"])
        res.append(json_data["forum"])
    except KeyError:
        res = []
    return res


@app.route('/create/', methods=['POST'])
def create():
    # TODO: check identities
    post_data = request.json
    data = parse_post_data(post_data)
    if(len(data) == 0):
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    optional = [-1, 0, 0, 0, 0, 0]
    for el in optional:
        data.append(el)
    try:
        parent_id = post_data["parent"]
        data[5] = parent_id
    except KeyError:
        pass
    try:
        data[6] = int(post_data["isApproved"])
    except KeyError:
        pass
    try:
        data[7] = int(post_data["isHighlighted"])
    except KeyError:
        pass
    try:
        data[8] = int(post_data["isEdited"])
    except KeyError:
        pass
    try:
        data[9] = int(post_data["isSpam"])
    except KeyError:
        pass
    try:
        data[10] = int(post_data["isDeleted"])
    except KeyError:
        pass
    print(data)
    insert_stmt = ('INSERT INTO Posts (date, thread, message, user, forum, parent, isApproved, isHighlighted, isEdited, isSpam, isDeleted)'
                   'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    )
    inserted_id = execute_insert(insert_stmt, data)
    upd_stmt = ('UPDATE Threads SET posts = posts + 1 WHERE id = %s')
    execute_insert(upd_stmt, data[1])
    post = serialize_post(data, inserted_id)
    answer = {"code": 0, "response": post}
    return jsonify(answer)
