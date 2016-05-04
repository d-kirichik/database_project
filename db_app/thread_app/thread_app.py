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
    select_stmt = 'SELECT forum, title, isClosed, user, date, message, slug, isDeleted FROM Threads WHERE id = %s'
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
