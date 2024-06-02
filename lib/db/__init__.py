import logging
import sqlite3

class DB:
    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def connect(self):
        self.connection = sqlite3.connect("db/SixMan.db")
        self.cursor = self.connection.cursor()
        self.logger.info(f"[DB] DB Connected")

    def execute(self, command, *values):
        self.cursor.execute(command, tuple(values))
        self.connection.commit()

    def field(self, command, *values):
        self.cursor.execute(command, tuple(values))
        fetch = self.cursor.fetchone()
        if fetch is not None:
            return fetch[0]
        return None

    def record(self, command, *values):
        self.cursor.execute(command, tuple(values))
        return self.cursor.fetchone()

    def records(self, command, *values):
        self.cursor.execute(command, tuple(values))
        return self.cursor.fetchall()

    def column(self, command, *values):
        self.cursor.execute(command, tuple(values))
        return [item[0] for item in self.cursor.fetchall()]