from flask import Blueprint
from flask import request, jsonify
from db_app.executor import *
import urlparse

app = Blueprint('post_app', __name__)


def serialize_unicode_post(post, post_id):
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


def serialize_post(post, post_id):
    resp = {
        'date': post[0].isoformat(sep=' '),
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
    insert_stmt = ('INSERT INTO Posts (date, thread, message, user, forum, parent, isApproved, isHighlighted, isEdited, isSpam, isDeleted)'
                   'VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)'
    )
    inserted_id = execute_insert(insert_stmt, data)
    upd_stmt = ('UPDATE Threads SET posts = posts + 1 WHERE id = %s')
    execute_insert(upd_stmt, data[1])
    post = serialize_unicode_post(data, inserted_id)
    answer = {"code": 0, "response": post}
    return jsonify(answer)


@app.route('/details/', methods=['GET'])
def details():
    qs = urlparse.urlparse(request.url).query
    req = urlparse.parse_qs(qs)
    data = []
    try:
        data.append(req["post"])
    except KeyError:
        answer = {"code": 3, "response": "incorrect request"}
        return jsonify(answer)
    select_stmt = ('SELECT * FROM Posts WHERE id = %s')
    post = execute_select_one(select_stmt, data[0])
    post_data = post[0][1:]
    answer = {"code": 0, "response": serialize_post(post_data, post[0][0])}
    return jsonify(answer)


@app.route('/vote/', methods=['POST'])
def vote():
    data = request.json
    vote_data = []
    upd_stmt = ()
    try:
        vote_data.append(data["vote"])
        vote_data.append(data["post"])
    except KeyError:
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    if(vote_data[0] == 1):
        upd_stmt = ('UPDATE Posts SET likes = likes + 1 WHERE id = %s')
    if(vote_data[0] == -1):
        upd_stmt = ('UPDATE Posts SET dislikes = dislikes + 1 WHERE id = %s')
    upd_id = execute_insert(upd_stmt, vote_data[1])
    answer = {"code": 0, "response": upd_id}
    return jsonify(answer)


@app.route('/list/', methods=['GET'])
def list():
    qs = urlparse.urlparse(request.url).query
    req = urlparse.parse_qs(qs)
    data = []
    try:
        data.append(req["thread"])
        select_stmt = ('SELECT * FROM Posts WHERE thread = %s')
    except KeyError:
        try:
            data.append(req["forum"])
            select_stmt = ('SELECT * FROM Posts WHERE forum = %s')
        except KeyError:
            answer = {"code": 3, "response": "incorrect request"}
            return jsonify(answer)
    try:
        data.append(req["since"])
        select_stmt += ' AND data > %s '
    except KeyError:
        pass
    try:
        data.append(req["order"])
        select_stmt += ' ORDER BY %s '
    except KeyError:
        pass
    try:
        data.append(req["limit"])
        select_stmt += ' LIMIT %s '
    except KeyError:
        pass
    req_data = []
    for d in data:
        req_data.append(d[0])
    print(req_data)
    posts = execute_select_one(select_stmt, req_data)
    print(posts)
    serialized_post = posts[0][1:]
    answer = {"code": 0, "response": serialize_post(serialized_post, posts[0][0])}
    return jsonify(answer)


@app.route('/remove/', methods=['POST'])
def remove():
    data = request.json
    rem_data = []
    try:
        rem_data.append(data["post"])
    except KeyError:
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    upd_stmt = ('UPDATE Posts SET isDeleted = 1 WHERE id = %s')
    execute_insert(upd_stmt, rem_data[0])
    answer = {"code": 0, "response": rem_data[0]}
    return jsonify(answer)


@app.route('/restore/', methods=['POST'])
def restore():
    data = request.json
    rem_data = []
    try:
        rem_data.append(data["post"])
    except KeyError:
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    upd_stmt = ('UPDATE Posts SET isDeleted = 0 WHERE id = %s')
    execute_insert(upd_stmt, rem_data[0])
    answer = {"code": 0, "response": rem_data[0]}
    return jsonify(answer)


@app.route('/update/', methods=['POST'])
def update():
    data = request.json
    up_data = []
    try:
        up_data.append(data["message"])
        up_data.append(data["post"])
    except KeyError:
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    update_stmt = ('UPDATE Posts SET message = %s WHERE id = %s')
    ins_id = execute_insert(update_stmt, up_data)
    answer = {"code": 0, "response": ins_id}
    return jsonify(answer)











