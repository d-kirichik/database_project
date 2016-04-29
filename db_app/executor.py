import MySQLdb


def connect_to_db():
    return MySQLdb.connect(host='localhost', user='user', password='1234',
                           db='database_project', charset='utf8', use_unicode=True)
