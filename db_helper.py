import psycopg2
import psycopg2.extras

import config.db_config as db_config


class DBHelper:

    def __init__(self):
        self.__connection = None
        self.__cursor = None

    def connect(self):
        self.__connection = psycopg2.connect(dbname=db_config.db_name, user=db_config.db_user,
                                             password=db_config.db_pass, host=db_config.db_host, port=db_config.db_port)
        self.__cursor = self.__connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)

    def get_cursor(self):
        return self.__cursor

    def commit(self):
        self.__connection.commit()

    def close(self):
        self.__cursor.close()
        self.__connection.close()
