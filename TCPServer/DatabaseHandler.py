import sqlite3
from datetime import datetime
import math
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

    
    def insertData(self, table, data, value):
        if(isinstance(value, list) and isinstance(data, list)):
            loc_data_place_holder = ''
            loc_value_place_holder = ''
            for i in data:
                loc_data_place_holder += "{},".format(i)
            for i in value:
                loc_value_place_holder += "\'{}\',".format(i)
            self.c.execute("INSERT INTO {} ({}) VALUES ({})".format(table,loc_data_place_holder[:-1], loc_value_place_holder[:-1]))
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
        self.c.execute("DELETE from {} WHERE {} = '{}'".format(table, data, value))
        self.conn.commit()

    def deleteAllData(self, table):
        self.c.execute("DELETE from {}".format(table))
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
        tmp = len(self.c.fetchall())
        self.conn.commit()
        return tmp
    
    def closeDB(self):
        self.conn.close()

def login(phone, password, Skey, addr):
    usrDB = MyDatabase('User Database')
    tmp = usrDB.getData('user','phone',phone)
    if(tmp != []  and tmp[0][1] == password):
        usrDB.updateData('user', ['login', 1],['phone', phone])
        Skey_sub1_length = int(len(Skey)/4)
        Skey_sub2_length = int(len(Skey)/2)
        Skey_sub3_length = Skey_sub1_length + Skey_sub2_length
        tmp_data_list = ['ip','key1','key2','key3','key4']
        tmp_value_list = [addr, 
                        Skey[:Skey_sub1_length],
                        Skey[Skey_sub1_length:Skey_sub2_length],
                        Skey[Skey_sub2_length:Skey_sub3_length],
                        Skey[Skey_sub3_length:]]
        tmp_2 = usrDB.getData('ipkey','ip',addr)
        if(tmp_2 == []):       
            usrDB.insertData('ipKey',tmp_data_list,tmp_value_list)
        return "good"
    else:
        tmp_2 = usrDB.getData('ipkey','ip',addr)
        if(tmp_2 != []):
            usrDB.deleteData('ipkey','ip', addr)
        return "bad"

def logout(phone, addr):
    usrDB = MyDatabase('User Database')
    tmp = usrDB.getData('user','phone',phone)
    if(tmp != [] and tmp[0][5] == 1):
        usrDB.updateData('user', ['login', 0],['phone', phone])
        usrDB.updateData('user', ['vehicle_mass', 0],['phone', phone])
        usrDB.updateData('user', ['vehicle_name', 'None'],['phone', phone])
    tmp = usrDB.getData('ipkey','ip',addr)
    if(tmp != []):
        usrDB.deleteData('ipkey','ip', addr)

def signup(phone, password):
    usrDB = MyDatabase('User Database')
    tmp = usrDB.getData('user','phone',phone)
    if(tmp == []):
        tmp_data_list = ['phone', 'password', 'budget', 
                        'vehicle_name', 'vehicle_mass', 'login']
        tmp_value_list = [phone, password, 0, 'None', 0, 1]
        usrDB.insertData('user',tmp_data_list,tmp_value_list)
        return "good"
    else:
        return "bad"

def addmoney(phone, money):
    usrDB = MyDatabase('User Database')
    loc_time = datetime.now().strftime("%d/%m/%y-%H:%M:%S")
    tmp_data_list = ['phone', 'Longitude1', 'Latitude1',
                    'money', 'time', 'vehicle_name', 'vehicle_mass',
                    'Longitude2', 'Latitude2','street']
    tmp_value_list = [phone, 0, 0, 
                    "+"+money, loc_time ,'None', 0,
                    0, 0, 'None']
    tmp = usrDB.getData('user','phone',phone)
    if(tmp != [] and tmp[0][5] == 1):
        usrDB.updateData('user', ['budget', str(int(tmp[0][2]) + int(money))],['phone', phone])
        usrDB.insertData('history',tmp_data_list,tmp_value_list)
        return "good"
    else:
        return "bad"

def retrievemoney(phone, money):
    usrDB = MyDatabase('User Database')
    time = datetime.now().strftime("%d/%m/%y-%H:%M:%S")
    tmp_data_list = ['phone', 'Longitude1', 'Latitude1',
                    'money', 'time', 'vehicle_name', 'vehicle_mass',
                    'Longitude2', 'Latitude2','street']
    tmp_value_list = [phone, 0, 0, 
                    "-"+money, time ,'None', 0,
                    0, 0, 'None']
    tmp = usrDB.getData('user','phone',phone)
    if(tmp != [] and tmp[0][5] == 1):
        usrDB.updateData('user', ['budget', str(int(tmp[0][2]) - int(money))],['phone', phone])
        usrDB.insertData('history',tmp_data_list,tmp_value_list)
        return "good"
    else:
        return "bad"

def payfee(phone, Longitude1, Latitude1, Longitude2, Latitude2, distance, street):
    usrDB = MyDatabase('User Database')
    #distance = distanceCalculation(Longitude1, Latitude1, Longitude2, Latitude2)
    print("DISTANCE : !!!!! : ", distance)
    tmp = usrDB.getData('user','phone',phone)
    vehicle_name = tmp[0][3]
    vehicle_mass = int(tmp[0][4])
    if(tmp != [] and tmp[0][5] == 1 and vehicle_mass>0):
        money = getstreet(street)*vehicle_mass*int(float(distance))
        if(money != 0):
            time = datetime.now().strftime("%d/%m/%y-%H:%M:%S")
            tmp_data_list = ['phone', 'Longitude1', 'Latitude1',
                            'money', 'time', 'vehicle_name', 'vehicle_mass',
                            'Longitude2', 'Latitude2','street']
            tmp_value_list = [phone, Longitude1, Latitude1, 
                            money, time ,vehicle_name, vehicle_mass,
                            Longitude2, Latitude2, street]
            usrDB.updateData('user', ['budget', int(tmp[0][2]) - money],['phone', phone])
            usrDB.insertData('history',tmp_data_list,tmp_value_list)
            return "good"
    else:
        return "bad"

def registerdriver(phone, vehicle_name, vehicle_mass):
    usrDB = MyDatabase('User Database')
    tmp = usrDB.getData('user','phone',phone)
    if(tmp != [] and tmp[0][5] == 1 and vehicle_mass != 0 and tmp[0][3] == 'None'):
        usrDB.updateData('user', ['vehicle_name', vehicle_name],['phone', phone])
        usrDB.updateData('user', ['vehicle_mass', vehicle_mass],['phone', phone])
        return "good"
    else:
        return "bad"

def gethistory(phone, index):
    int_index = int(index)
    usrDB = MyDatabase('User Database')
    tmp = usrDB.getData('history','phone',phone)
    if(int_index < len(tmp)):
        return tmp[int_index]
    else:
        return []

def getuserinfo(phone):
    usrDB = MyDatabase('User Database')
    return usrDB.getData('user','phone',phone)[0]

def getstreet(street):
    usrDB = MyDatabase('User Database')
    tmp = usrDB.getData('street','street',street)
    if(tmp != []):
        return int(tmp[0][1])
    else:
        return 0

def lostConnection(addr):
    usrDB = MyDatabase('User Database')
    tmp = usrDB.getData('ipkey','ip',addr)
    if(tmp != []):
        usrDB.deleteData('ipkey','ip', addr)

def distanceCalculation(x1, y1, x2 ,y2):
    x1 = float(x1) * 10000000
    x2 = float(x2) * 10000000
    y1 = float(y1) * 10000000
    y2 = float(y2) * 10000000
    print("x1 = ", x1)
    print("FLOAT x1 = ", float(x1))
    print("x2 = ", x2)
    print("FLOAT x2 = ", float(x2))
    delta_x = float(x1) - float(x2)
    print("delta x = ", delta_x)
    delta_y = float(y1) - float(y2)
    print("delta y = ", delta_y)
    return int(math.sqrt(delta_x*delta_x + delta_y*delta_y))