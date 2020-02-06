import psycopg2
import psycopg2.extras

import config.db_config as db_config


class Database:

    __connection = None
    __cursor = None

    def connect(self):
        if self.__connection is None:
            try:
                self.__connection = psycopg2.connect(dbname=db_config.db_name, user=db_config.db_user,
                                                 password=db_config.db_pass, host=db_config.db_host,
                                                 port=db_config.db_port)
            except psycopg2.Error as err:
                print("[DB Log] Connection error.")
            else:
                print("[DB Log] Open connection.")
            self.__connection.autocommit = True
            self.__cursor = self.__connection.cursor(cursor_factory=psycopg2.extras.RealDictCursor)
        return self.__cursor


database_cursor = Database().connect()
