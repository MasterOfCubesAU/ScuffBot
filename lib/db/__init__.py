import logging
import mysql.connector as mysql
from mysql.connector import errorcode
from dotenv import load_dotenv
import os

load_dotenv()

class DB:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def connect(self):
        try:
            self.connection = mysql.connect(host=os.getenv("DB_HOST"), user=os.getenv("DB_USER"), password=os.getenv("DB_PASS"), database=os.getenv("DB_DATABASE"), autocommit=True)
        except mysql.Error as err:
            if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
                self.logger.error("[DB] Database credentials incorrect.")
            elif err.errno == errorcode.ER_BAD_DB_ERROR:
                self.logger.error("[DB] Database does not exist.")
            else:
                self.logger.error(f"[DB] {err}")
        else:
            self.cursor = self.connection.cursor(dictionary=True)
            self.logger.info("[DB] Connection established.")

    def execute(self, command, *values):
        self.cursor.execute(command, tuple(values))

    def field(self, command, *values):
        self.cursor.execute(command, tuple(values))
        return None if not (data := self.cursor.fetchone()) else list(data.values())[0]
    
    def row(self, command, *values):
        self.cursor.execute(command, tuple(values))
        return self.cursor.fetchone()
    
    def rows(self, command, *values):
        self.cursor.execute(command, tuple(values))
        return self.cursor.fetchall()

    def column(self, command, *values):
        self.cursor.execute(command, tuple(values))
        return [list(row.values())[0] for row in self.cursor.fetchall()]
