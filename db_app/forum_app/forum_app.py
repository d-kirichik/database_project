import json

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


def serialize_user(user, user_id, subscriptions, following, followers):
    resp = {
        'about': user[2],
        'email': user[4],
        'followers': followers,
        'following': following,
        'id': user_id,
        'isAnonymous': bool(user[5]),
        'name': user[3],
        'subscriptions': subscriptions,
        'username': user[1]
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
    forum_data = [forum[0][1], forum[0][2], forum[0][3]]
    answer = {"code": 0, "response": serialize_forum(forum_data, forum[0][0])}
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


@app.route('/listUsers/', methods=['GET'])
def listUsers():
    qs = urlparse.urlparse(request.url).query
    req = urlparse.parse_qs(qs)
    data = []
    try:
        data.append(req["forum"])
    except KeyError:
        answer = {"code": 3, "response": "invalid json"}
        return jsonify(answer)
    select_stmt = ('SELECT * FROM Users WHERE email IN (SELECT DISTINCT user FROM Posts WHERE forum = %s)')
    try:
        data.append(req["since_id"])
        select_stmt += ' AND id >= %s '
    except KeyError:
        pass
    try:
        order = req["order"]
        if order[0] == 'asc':
            select_stmt += 'ORDER BY name asc '
        if order[0] == 'desc':
            select_stmt += 'ORDER BY name desc'
    except KeyError:
        pass
    try:
        data.append(req["limit"])
        select_stmt += ' LIMIT %s '
    except KeyError:
        pass
    req_data = []
    for d in data:
        el = d[0]
        try:
            el = int(d[0])
        except Exception:
            pass
        req_data.append(el)
    print req_data
    print select_stmt
    users = execute_select_one(select_stmt, req_data)
    answer = []
    for u in users:
        print u
        select_stmt = 'SELECT thread FROM Subscribe WHERE user = %s'
        subs = execute_select_one(select_stmt, u[4])
        sub_data = []
        for s in subs:
            sub_data.append(s[0])
        select_stmt = 'SELECT follower_mail FROM Followers WHERE followee_mail = %s'
        followers = execute_select_one(select_stmt, u[4])
        followers_data = []
        for fol in followers:
            followers_data.append(fol[0])
        select_stmt = 'SELECT followee_mail FROM Followers WHERE follower_mail = %s'
        followee = execute_select_one(select_stmt, u[4])
        followee_data = []
        for fol in followee:
            followee_data.append(fol[0])
        answer.append(serialize_user(u, u[0], sub_data, followee_data, followers_data))
    return json.dumps({"code": 0, "response": answer})
