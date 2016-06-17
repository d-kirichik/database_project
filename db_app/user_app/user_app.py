import json
from flask import jsonify, Blueprint
from flask import request
from db_app.executor import *
import urlparse

from db_app.post_app.post_app import serialize_post

app = Blueprint('user_app', __name__)


def serialize_user(user, user_id, subscriptions, following, followers):
    resp = {
        'about': user[2],
        'email': user[1],
        'followers': followers,
        'following': following,
        'id': user_id,
        'isAnonymous': bool(user[3]),
        'name': user[4],
        'subscriptions': subscriptions,
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
    following = followers = []
    sub = []
    answer = jsonify({"code": 0, "response": serialize_user(resp[0], user_id, sub, following, followers)})
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
    select_stmt = ('SELECT followee_mail FROM Followers WHERE follower_mail = %s')
    follower = execute_select_one(select_stmt, user_mail)
    following = []
    for fol in follower:
        following.append(fol[0])
    select_stmt = ('SELECT follower_mail FROM Followers WHERE followee_mail = %s')
    follower = execute_select_one(select_stmt, user_mail)
    followers = []
    for fol in follower:
        followers.append(fol[0])
    select_stmt = 'SELECT thread FROM Subscribe WHERE user = %s'
    resp = execute_select_one(select_stmt, user_mail)
    sub = []
    for s in resp:
        sub.append(s[0])
    answer = jsonify({"code": 0, "response": serialize_user(user[0], user[0][0], sub, following, followers)})
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
    sub = following = followers = []
    answer = jsonify({"code": 0, "response": serialize_user(resp[0], resp[0][0], sub, following, followers)})
    return answer


@app.route('/listFollowers/', methods=['GET'])
def listFollowers():
    qs = urlparse.urlparse(request.url).query
    req = urlparse.parse_qs(qs)
    data = []
    count = 0
    try:
        data.append(req["user"])
        count += 1
    except KeyError:
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    select_stmt = 'SELECT follower_mail FROM Followers WHERE followee_mail = %s'
    try:
        data.append(req["since_id"])
        select_stmt += ' AND id >= ' + data[count][0]
        count += 1
    except KeyError:
        pass
    try:
        data.append(req["order"])
        select_stmt += ' ORDER BY followee_mail ' + data[count][0]
        count += 1
    except KeyError:
        pass
    try:
        data.append(req["limit"])
        select_stmt += ' LIMIT ' + data[count][0]
    except KeyError:
        pass
    mails = execute_select_one(select_stmt, data[0])
    select_stmt = 'SELECT id, email, about, isAnonymous, name, username FROM Users WHERE'
    req_data = []
    for mail in mails:
        req_data.append(mail[0])
        if mail == mails[0]:
            select_stmt += ' email = %s '
        else:
            select_stmt += ' or email = %s '
    followers = execute_select_one(select_stmt, req_data)
    answer = []
    for f in followers:
        select_stmt = 'SELECT thread FROM Subscribe WHERE user = %s'
        subs = execute_select_one(select_stmt, f[1])
        sub_data = []
        for s in subs:
            sub_data.append(s[0])
        select_stmt = 'SELECT follower_mail FROM Followers WHERE followee_mail = %s'
        followers = execute_select_one(select_stmt, f[1])
        followers_data = []
        for fol in followers:
            followers_data.append(fol[0])
        select_stmt = 'SELECT followee_mail FROM Followers WHERE follower_mail = %s'
        followee = execute_select_one(select_stmt, f[1])
        followee_data = []
        for fol in followee:
            followee_data.append(fol[0])
        answer.append(serialize_user(f, f[0], sub_data, followee_data, followers_data))
    return json.dumps({"code": 0, "response": answer})


@app.route('/listFollowing/', methods=['GET'])
def listFollowing():
    qs = urlparse.urlparse(request.url).query
    req = urlparse.parse_qs(qs)
    data = []
    count = 0
    try:
        data.append(req["user"])
        count+=1
    except KeyError:
        answer = {"code": 2, "response": "invalid json"}
        return jsonify(answer)
    select_stmt = 'SELECT followee_mail FROM Followers WHERE follower_mail = %s'
    try:
        data.append(req["since_id"])
        select_stmt += ' AND id >= ' + data[count][0]
        count += 1
    except KeyError:
        pass
    try:
        data.append(req["order"])
        select_stmt += ' ORDER BY follower_mail ' + data[count][0]
        count += 1
    except KeyError:
        pass
    try:
        data.append(req["limit"])
        select_stmt += ' LIMIT ' + data[count][0]
    except KeyError:
        pass
    mails = execute_select_one(select_stmt, data[0])
    select_stmt = 'SELECT id, email, about, isAnonymous, name, username FROM Users WHERE'
    req_data = []
    for mail in mails:
        req_data.append(mail[0])
        if mail == mails[0]:
            select_stmt += ' email = %s '
        else:
            select_stmt += ' or email = %s '
    followers = execute_select_one(select_stmt, req_data)
    answer = []
    for f in followers:
        select_stmt = 'SELECT thread FROM Subscribe WHERE user = %s'
        subs = execute_select_one(select_stmt, f[1])
        sub_data = []
        for s in subs:
            sub_data.append(s[0])
        select_stmt = 'SELECT follower_mail FROM Followers WHERE followee_mail = %s'
        followers = execute_select_one(select_stmt, f[1])
        followers_data = []
        for fol in followers:
            followers_data.append(fol[0])
        select_stmt = 'SELECT followee_mail FROM Followers WHERE follower_mail = %s'
        followee = execute_select_one(select_stmt, f[1])
        followee_data = []
        for fol in followee:
            followee_data.append(fol[0])
        answer.append(serialize_user(f, f[0], sub_data, followee_data, followers_data))
    return json.dumps({"code": 0, "response": answer})


@app.route('/listPosts/', methods=['GET'])
def listPosts():
    qs = urlparse.urlparse(request.url).query
    req = urlparse.parse_qs(qs)
    data = []
    try:
        data.append(req["user"])
    except KeyError:
        answer = {"code": 3, "response": "invalid json"}
        return jsonify(answer)
    select_stmt = ('SELECT * FROM Posts WHERE user = %s')
    try:
        data.append(req["since"])
        select_stmt += ' AND date > %s '
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
    posts = execute_select_one(select_stmt, req_data)
    #print(posts)
    answer = []
    for p in posts:
        p_data = p[1:]
        answer.append(serialize_post(p_data, p[0]))
    return json.dumps({"code": 0, "response": answer})






