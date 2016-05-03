from flask import Blueprint
from flask import request, jsonify
from db_app.executor import *

app = Blueprint('thread_app', __name__)


def str_to_bool(str_req):
    if(str_req == "true"):
        return 1
    else:
        return 0


def serialize_thread(thread):
    thread = thread[0]
    resp = {
        'date': thread[5],
        'forum': thread[1],
        'id': thread[0],
        'isClosed': bool(thread[3]),
        'isDeleted': bool(thread[8]),
        'message': thread[6],
        'slug': thread[7],
        'title': thread[2],
        'user': thread[4]
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
            res.append((json_data["isClosed"]))
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
    res[2] = str_to_bool(res[2])
    if(len(res) == 7):
        res[7] = str_to_bool(res[7])
    elif(len(res) == 6):
        res.append(0)
    print(res)
    user_id = execute_insert(insert_stmt, res)
    select_stmt = ('SELECT id, forum, title, isClosed, user, date, message, slug, isDeleted FROM Threads WHERE id = %s')
    resp = execute_select_one(select_stmt, user_id)
    answer = jsonify({"code": 0, "response": serialize_thread(resp)})
    return answer


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
