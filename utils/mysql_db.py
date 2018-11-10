import pymysql.cursors


def get_mysql(db, host='localhost', port=3306,
              user='root', password=None, autocommit=True,
              charset='utf8'):
    conn = pymysql.connect(host=host, port=int(port),
                           user=user, password=password,
                           db=db, charset=charset, autocommit=autocommit,
                           cursorclass=pymysql.cursors.DictCursor)
    return conn

