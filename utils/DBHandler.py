import sqlite3

class DBHandler:

    CONNECTION = sqlite3.connect("ScuffBot.sqlite")
    CURSOR = CONNECTION.cursor()

    @staticmethod
    def execute(command, *values):
        DBHandler.CURSOR.execute(command, tuple(values))
        DBHandler.CONNECTION.commit()

    @staticmethod
    def field(command, *values):
        DBHandler.CURSOR.execute(command, tuple(values))
        fetch =  DBHandler.CURSOR.fetchone()
        if fetch is not None:
            return fetch[0]
        return None

    @staticmethod
    def record(command, *values):
        DBHandler.CURSOR.execute(command, tuple(values))
        return  DBHandler.CURSOR.fetchone()

    @staticmethod
    def records(command, *values):
        DBHandler.CURSOR.execute(command, tuple(values))
        return  DBHandler.CURSOR.fetchall()

    @staticmethod
    def column(command, *values):
        DBHandler.CURSOR.execute(command, tuple(values))
        return [item[0] for item in DBHandler.CURSOR.fetchall()]



