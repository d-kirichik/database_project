import MySQLdb


def connect_to_db():
    return MySQLdb.connect(host='localhost', user='user', passwd='1234',
                           db='database_project', charset='utf8', use_unicode=True)


def execute_select_all(query):
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute(query)
    ret = cursor.fetchall()
    cursor.close()
    connection.close()
    return ret


def execute_insert(query, params):
    connection = connect_to_db()
    cursor = connection.cursor()
    entity_id = -1
    try:
        cursor.execute(query, params)
        entity_id = cursor.lastrowid
        connection.commit()
        cursor.close()
    except Exception, MySQLdb.Error:
        connection.rollaback()
    return entity_id


def execute_select_one(query, params):
    connection = connect_to_db()
    cursor = connection.cursor()
    result = []
    try:
        cursor.execute(query, params)
        result = cursor.fetchall()
        cursor.close()
    except Exception, MySQLdb.Error:
        result = []
        cursor.close()
    return result


