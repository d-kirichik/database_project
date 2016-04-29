import MySQLdb


def connect_to_db():
    return MySQLdb.connect(host='localhost', user='user', passwd='1234',
                           db='database_project', charset='utf8', use_unicode=True)


def execute(query):
    connection = connect_to_db()
    cursor = connection.cursor()
    cursor.execute(query)
    ret = cursor.fetchall()
    cursor.close()
    connection.close()
    return ret
