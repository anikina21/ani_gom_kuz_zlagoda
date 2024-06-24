import mysql.connector
from mysql.connector import Error
import bcrypt

class DatabaseManager:
    def __init__(self, host, user, password, database):
        self.host = host
        self.user = user
        self.password = password
        self.database = database

    def connect(self):
        try:
            self.conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database
            )
            self.cursor = self.conn.cursor()
        except Error as err:
            print(f"Error: {err}")
            self.conn = None
            self.cursor = None

    def disconnect(self):
        if self.cursor:
            self.cursor.close()
        if self.conn:
            self.conn.close()

    def execute_query(self, query, params=None):
        try:
            self.connect()
            self.cursor.execute(query, params)
            result = self.cursor.fetchall()
            self.conn.commit()
            return result
        except Error as err:
            print(f"Error: {err}")
            return None
        finally:
            self.disconnect()

    def execute_non_query(self, query, params=None):
        try:
            self.connect()
            self.cursor.execute(query, params)
            self.conn.commit()
        except Error as err:
            print(f"Error: {err}")
        finally:
            self.disconnect()