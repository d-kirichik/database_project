from flask import Blueprint
from flask import request, jsonify
from db_app.executor import *
import urlparse
from db_app.thread_app.thread_app import serialize_thread
# TODO: separate methods

app = Blueprint('forum_app', __name__)


def serialize_forum(forum, forum_id):
    resp = {
        'id': forum_id,
        'name': forum[0],
        'short_name': forum[1],
        'user': forum[2]
    }
    return resp


def serialize_post(post):
    resp = {
        'date': post[1],
        'forum': post[5],
        'id': post[0],
        'isApproved': bool(post[7]),
        'isDeleted': bool(post[11]),
        'isEdited': bool(post[9]),
        'isHighlighted': bool(post[8]),
        'isSpam': bool(post[10]),
        'message': post[3],
        'parent': post[6],
        'thread': post[2],
        'user': post[4]
    }
    return resp


@app.route('/create/', methods=['POST'])
def create():
    data = request.json
    forum_data = []
    try:
        forum_data.append(data["name"])
        forum_data.append(data["short_name"])
        forum_data.append(data["user"])
    except KeyError:
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    insert_stmt = ('INSERT INTO Forums (name, slug, user) VALUES (%s, %s, %s)')
    inserted_id = execute_insert(insert_stmt, forum_data)
    forum = serialize_forum(forum_data, inserted_id)
    answer = {"code": 0, "response": forum}
    return jsonify(answer)


@app.route('/details/', methods=['GET'])
def details():
    # TODO: related
    qs = urlparse.urlparse(request.url).query
    req = urlparse.parse_qs(qs)
    data = []
    try:
        data.append(req["forum"])
    except KeyError:
        answer = {"code": 3, "response": "incorrect request"}
        return jsonify(answer)
    count = 1
    select_stmt = ('SELECT * FROM Forums WHERE slug = %s')
    forum = execute_select_one(select_stmt, data[0])
    answer = {"code": 0, "response": serialize_forum(forum[0], forum[0][0])}
    return jsonify(answer)

@app.route('/listPosts/', methods=['GET'])
def listPosts():
    # TODO: number of posts, validation, related
    qs = urlparse.urlparse(request.url).query
    req = urlparse.parse_qs(qs)
    data = []
    try:
        data.append(req["forum"])
    except KeyError:
        answer = {"code": 3, "response": "incorrect request"}
        return jsonify(answer)
    count = 1
    select_stmt = ('SELECT * FROM Posts WHERE forum = %s')
    try:
        data.append(req["since"])
        select_stmt += ' AND date >= ' + data[count][0]
        count += 1
    except KeyError:
        pass
    try:
        data.append(req["order"])
        select_stmt += ' ORDER BY date ' + data[count][0]
        count += 1
    except KeyError:
        select_stmt += ' ORDER BY date DESC'
    try:
        data.append(req["limit"])
        select_stmt += ' LIMIT ' + data[count][0]
    except KeyError:
        pass
    post = execute_select_one(select_stmt, data[0])
    print(post[0])
    answer = {"code": 0, "response": serialize_post(post[0])}
    return jsonify(answer)


@app.route('/listThreads/', methods=['GET'])
def listThreads():
    # TODO: number of threads, validation, related
    qs = urlparse.urlparse(request.url).query
    req = urlparse.parse_qs(qs)
    data = []
    try:
        data.append(req["forum"])
    except KeyError:
        answer = {"code": 3, "response": "incorrect request"}
        return jsonify(answer)
    count = 1
    select_stmt = ('SELECT * FROM Threads WHERE forum = %s')
    try:
        data.append(req["since"])
        select_stmt += ' AND date >= \'' + (data[count][0]) + '\''
        count += 1
    except KeyError:
        pass
    try:
        data.append(req["order"])
        select_stmt += ' ORDER BY date ' + data[count][0]
        count += 1
    except KeyError:
        select_stmt += ' ORDER BY date DESC'
    try:
        data.append(req["limit"])
        select_stmt += ' LIMIT ' + data[count][0]
    except KeyError:
        pass
    thread = execute_select_one(select_stmt, data[0])
    try:
        print(serialize_thread(thread[0], thread[0][0]))
    except Exception as e:
        print e.message
    answer = {"code": 0, "response": serialize_thread(thread[0])}
    return jsonify(answer)