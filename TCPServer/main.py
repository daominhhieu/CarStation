import selectors
import sys
import socket
import types
import traceback
from TCPMessageHandler import Message
from DatabaseHandler import MyDatabase
from cryptography.fernet import Fernet

import time
import base64

DEBUG = "DEBUG_MODE"
HOST = '172.20.10.3'
PORT = 2312
TIMEOUT = 5

sel = selectors.DefaultSelector()

def init_db():
    usr_db_template = ['phone TEXT',
                        'password TEXT',
                        'budget INTEGER',
                        'vehicle_name TEXT',
                        'vehicle_mass INTEGER']

    histoty_db_template = ['phone TEXT',
                            'longitude REAL',
                            'Latitude REAL',
                            'money INTEGER',
                            'time TEXT',
                            'vehicle_name TEXT',
                            'vehicle_mass INTEGER']

    street_db_template = ['street TEXT',
                            'fee INTEGER']

    ipKey_db_template = ['ip TEXT',
                        'key1 TEXT',
                        'key2 TEXT',
                        'key3 TEXT',
                        'key4 TEXT']
    
    

    usrDB = MyDatabase('User Database')
    usrDB.createTable('user', usr_db_template)
    usrDB.createTable('history', histoty_db_template)
    usrDB.createTable('street', street_db_template)
    usrDB.createTable('ipKey', ipKey_db_template)


def accept_wrapper(sock):
    usrDB = MyDatabase('User Database')
    conn, addr = sock.accept()  # Should be ready to read
    print('accepted connection from', addr)
    conn.setblocking(False)#use non blocking mode on socket operation
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    print('address: ',addr[0])
    Skey = None
    KeyNotExist = False

    if(usrDB.getData('ipKey','ip',addr[0]) == []):
        Skey = Fernet.generate_key().decode("utf-8")
        print('secrete key not stored: ',Skey)      
        KeyNotExist = True
    else:
        for sub_Skey in usrDB.getData('ipKey','ip',addr[0]):
            Skey = sub_Skey[1]+sub_Skey[2]+sub_Skey[3]+sub_Skey[4]
        print('secrete key stored: ',Skey)

    fernetKey = Fernet(Skey.encode())
    message = Message(sel, conn, addr, fernetKey, Skey) # initiate message object with found connection
    
    #IMPORTANT !
    sel.register(conn, selectors.EVENT_READ, data=message)# push message object into selector
    if(KeyNotExist):
        message.startConnection()

def TCPConnectionRun():
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Avoid bind() exception: OSError: [Errno 48] Address already in use
    lsock.bind((HOST, PORT))
    lsock.listen()
    print("listening on", (HOST, PORT))
    lsock.setblocking(False) #use non blocking mode on socket operation
    sel.register(lsock, selectors.EVENT_READ, data=None)
    

    while True:
        try:
            events = sel.select(timeout=0)
            for key, mask in events:
                if key.data is None:
                    accept_wrapper(key.fileobj)
                else:
                    #IMPORTANT !
                    message = key.data # pull message object from selector
                    try:
                        message.process_events(mask)
                    except Exception:
                        print(
                            "main: error: exception for",
                            f"{message.addr}:\n{traceback.format_exc()}",
                        )

                        message.close()
            
        except KeyboardInterrupt:
            break
    

def initTCPserver():
    usrDB = MyDatabase('User Database')
    usrDB.deleteAllData('ipKey')
    print("ipKey table length: " + str(usrDB.getTableLength('ipKey')))

def main():
    # init_db()
    initTCPserver()
    TCPConnectionRun()




if __name__ == "__main__":
    main()
