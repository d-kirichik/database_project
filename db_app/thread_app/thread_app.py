from flask import Blueprint
from flask import request, jsonify
from db_app.executor import *
import urlparse

app = Blueprint('thread_app', __name__)


def serialize_unicode_thread(thread, thread_id):
    resp = {
        'date': thread[4],
        'forum': thread[0],
        'id': int(thread_id),
        'isClosed': bool(thread[2]),
        'isDeleted': bool(thread[7]),
        'message': thread[5],
        'slug': thread[6],
        'title': thread[1],
        'user': thread[3]
    }
    return resp


def serialize_thread(thread, thread_id):
    resp = {
        'date': thread[4].isoformat(sep=' '),
        'forum': thread[0],
        'id': int(thread_id),
        'isClosed': bool(thread[2]),
        'isDeleted': bool(thread[7]),
        'message': thread[5],
        'posts': thread[8],
        'slug': thread[6],
        'title': thread[1],
        'user': thread[3]
    }
    return resp


def _parse_thread_request_data(json_data):
    res = []
    try:
        res.append((json_data["forum"]))
        res.append((json_data["title"]))
        res.append((json_data["isClosed"]))
        res.append((json_data["user"]))
        res.append((json_data["date"]))
        res.append((json_data["message"]))
        res.append((json_data["slug"]))
        try:
            res.append((json_data["isDeleted"]))
        except KeyError:
            pass
    except KeyError:
        res = []
    return res


@app.route('/create/', methods=['POST'])
def create():
    # TODO: check identities
    thread_data = request.json
    res = _parse_thread_request_data(thread_data)
    if(len(res) == 0):
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    insert_stmt = ('INSERT INTO Threads (forum, title, isClosed, user, date, message, slug, isDeleted) '
                       'VALUES (%s, %s, %s, %s, %s, %s, %s, %s)'
    )
    res[2] = int(res[2])
    if(len(res) == 7):
        res[7] = int(res[7])
    elif(len(res) == 6):
        res.append(0)
    user_id = execute_insert(insert_stmt, res)
    answer = jsonify({"code": 0, "response": serialize_unicode_thread(res, user_id)})
    return answer


@app.route('/details/', methods=['GET'])
def details():
    qs = urlparse.urlparse(request.url).query
    req = urlparse.parse_qs(qs)
    data = []
    try:
        data.append(req["thread"])
    except KeyError:
        answer = {"code": 3, "response": "incorrect request"}
        return jsonify(answer)
    try:
        data.append(req["related"])
    except KeyError:
        pass
    select_stmt = 'SELECT forum, title, isClosed, user, date, message, slug, isDeleted, posts FROM Threads WHERE id = %s'
    threads = execute_select_one(select_stmt, data[0])
    answer = {"code": 0, "response": serialize_thread(threads[0], data[0][0])}
    return jsonify(answer)


@app.route('/close/', methods=['POST'])
def close():
    thread_data = request.json
    try:
        thread_id = thread_data["thread"]
    except KeyError:
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    update_stmt = ('UPDATE Threads SET isClosed = 1 WHERE id = %s')
    execute_insert(update_stmt, thread_id)
    answer = {"code": 0, "response": thread_id}
    return jsonify(answer)


@app.route('/open/', methods=['POST'])
def open():
    thread_data = request.json
    try:
        thread_id = thread_data["thread"]
    except KeyError:
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    update_stmt = ('UPDATE Threads SET isClosed = 0 WHERE id = %s')
    execute_insert(update_stmt, thread_id)
    answer = {"code": 0, "response": thread_id}
    return jsonify(answer)


@app.route('/subscribe/', methods=['POST'])
def subscribe():
    data = request.json
    sub_data = []
    try:
        sub_data.append(data["str"])
        sub_data.append(data["thread"])
    except KeyError:
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    ins_stmt = 'INSERT INTO Subscribe (thread, user) VALUES (%s, %s)'
    ins_id = execute_insert(ins_stmt, sub_data)
    answer = {"code": 0, "response": ins_id}
    return jsonify(answer)


@app.route('/unsubscribe/', methods=['POST'])
def unsubscribe():
    data = request.json
    sub_data = []
    try:
        sub_data.append(data["str"])
        sub_data.append(data["thread"])
    except KeyError:
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    ins_stmt = 'DELETE FROM Subscribe WHERE thread = %s AND user = %s'
    ins_id = execute_insert(ins_stmt, sub_data)
    answer = {"code": 0, "response": ins_id}
    return jsonify(answer)


@app.route('/vote/', methods=['POST'])
def vote():
    data = request.json
    vote_data = []
    upd_stmt = ()
    try:
        vote_data.append(data["vote"])
        vote_data.append(data["thread"])
    except KeyError:
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    if(vote_data[0] == 1):
        upd_stmt = ('UPDATE Threads SET likes = likes + 1 WHERE id = %s')
    if(vote_data[0] == -1):
        upd_stmt = ('UPDATE Threads SET dislikes = dislikes + 1 WHERE id = %s')
    upd_id = execute_insert(upd_stmt, vote_data[1])
    answer = {"code": 0, "response": upd_id}
    return jsonify(answer)


@app.route('/remove/', methods=['POST'])
def remove():
    data = request.json
    rem_data = []
    try:
        rem_data.append(data["thread"])
    except KeyError:
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    upd_stmt = ('UPDATE Threads SET isDeleted = 1 WHERE id = %s')
    execute_insert(upd_stmt, rem_data[0])
    answer = {"code": 0, "response": rem_data[0]}
    return jsonify(answer)


@app.route('/restore/', methods=['POST'])
def restore():
    data = request.json
    rem_data = []
    try:
        rem_data.append(data["thread"])
    except KeyError:
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    upd_stmt = ('UPDATE Threads SET isDeleted = 0 WHERE id = %s')
    execute_insert(upd_stmt, rem_data[0])
    answer = {"code": 0, "response": rem_data[0]}
    return jsonify(answer)


@app.route('/list/', methods=['GET'])
def list():
    qs = urlparse.urlparse(request.url).query
    req = urlparse.parse_qs(qs)
    data = []
    try:
        data.append(req["user"])
        select_stmt = ('SELECT * FROM Threads WHERE user = %s')
    except KeyError:
        try:
            data.append(req["forum"])
            select_stmt = ('SELECT * FROM Threads WHERE forum = %s')
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
    threads = execute_select_one(select_stmt, req_data)
    serialized_thread = threads[0][1:]
    print(threads[0])
    answer = {"code": 0, "response": serialize_thread(serialized_thread, threads[0][0])}
    return jsonify(answer)


@app.route('/listPosts/', methods=['GET'])
def listPosts():
    qs = urlparse.urlparse(request.url).query
    req = urlparse.parse_qs(qs)
    data = []
    try:
        data.append(req["thread"])
    except KeyError:
        answer = {"code": 3, "response": "incorrect request"}
        return jsonify(answer)
    select_stmt = ('SELECT * FROM Posts WHERE thread = %s')
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
    print select_stmt
    req_data = []
    for d in data:
        req_data.append(d[0])
    posts = execute_select_one(select_stmt, req_data)
    print posts
    answer = {"code": 0, "response": []}
    return jsonify(answer)


@app.route('/update/', methods=['POST'])
def update():
    data = request.json
    up_data = []
    try:
        up_data.append(data["message"])
        up_data.append(data["slug"])
        up_data.append(data["thread"])
    except KeyError:
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    update_stmt = ('UPDATE Threads SET message = %s, slug = %s WHERE id = %s')
    ins_id = execute_insert(update_stmt, up_data)
    answer = {"code": 0, "response": ins_id}
    return jsonify(answer)
