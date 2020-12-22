import sqlite3
DEBUG = "DEBUG_MODE"

class MyDatabase:
    def __init__(self, database_name):
        super().__init__()
        self.database_name = database_name
        if(self.database_name == DEBUG):
            self.conn = sqlite3.connect(':memory:')
        else:
            self.conn = sqlite3.connect(database_name+".db")
        self.c = self.conn.cursor()

    
    def insertData(self, table, data):
        if(isinstance(data, list) and (len(data) == getTableLength(table))):
            loc_place_holder = ''
            for i in data:
                loc_place_holder += "\'{}\',".format(i)
            self.c.execute("INSERT INTO {} VALUES ({})".format(table, loc_place_holder[:-1]))
            self.conn.commit()
        else:
            pass
    
    def updateData(self, table, data, condition):
        if(isinstance(data, list) and isinstance(condition, list)):
            self.c.execute("""UPDATE {} SET {}='{}' WHERE {}='{}'""".format(
                                    table, data[0], data[1], condition[0], condition[1]))
            self.conn.commit()
        else:
            pass

    def deleteData(self, table, data, value):
        self.c.execute("DELETE from {} WHERE {} = '{}'")
        self.conn.commit()

    def createTable(self, table, data):
        if(isinstance(data, list)):
            loc_place_holder = ''
            for i in data:
                loc_place_holder += "{},".format(i)
            self.c.execute("""CREATE TABLE {}({})""".format(table,loc_place_holder[:-1]))
            self.conn.commit()
        else:
            pass

    def getData(self, table, data, value):
        self.c.execute("SELECT * FROM {} WHERE {}='{}'".format(table,data, value))
        tmp = self.c.fetchall()
        self.conn.commit()
        return tmp
    
    def getTableLength(self, table):
        self.c.execute("SELECT * FROM {}".format(table))
        tmp = len(self.c.fetchall)
        self.conn.commit()
        return tmp
    
    def closeDB(self):
        self.conn.close()