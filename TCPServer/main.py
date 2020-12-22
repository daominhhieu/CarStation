import selectors
import sys
import socket
import types
import traceback
from TCPMessageHandler import Message
from DatabaseHandler import MyDatabase

DEBUG = "DEBUG_MODE"
MSG_LENGTH = 1024
HOST = 'localhost'
PORT = 2312

sel = selectors.DefaultSelector()

def init_db():
    usr_db_template = ['phone TEXT',
                        'password TEXT',
                        'budget INTEGER',
                        'key INTEGER',
                        'vehicle_name TEXT',
                        'vehicle_mass INTEGER']

    histoty_db_template = ['phone TEXT',
                            'street TEXT',
                            'money INTEGER',
                            'time TEXT',
                            'vehicle_name TEXT',
                            'vehicle_mass INTEGER']

    street_db_template = ['street TEXT',
                            'fee INTEGER']
    
    

    usrDB = MyDatabase('User Database')
    usrDB.createTable('user', usr_db_template)
    usrDB.createTable('history', histoty_db_template)
    usrDB.createTable('street', street_db_template)

def accept_wrapper(sock):
    conn, addr = sock.accept()  # Should be ready to read
    print('accepted connection from', addr)
    conn.setblocking(False)#use non blocking mode on socket operation
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    message = Message(sel, conn, addr) # initiate message object with found connection
    #IMPORTANT !
    sel.register(conn, selectors.EVENT_READ, data=message)# push message object into selector

def TCPConnectionRun():
    lsock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Avoid bind() exception: OSError: [Errno 48] Address already in use
    lsock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    lsock.bind((HOST, PORT))
    lsock.listen()
    print("listening on", (HOST, PORT))
    lsock.setblocking(False) #use non blocking mode on socket operation
    sel.register(lsock, selectors.EVENT_READ, data=None)

    while True:
        events = sel.select(timeout=None)
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
    

def main():
    try:
        TCPConnectionRun()
    except KeyboardInterrupt:
        print("caught keyboard interrupt, exiting")
    finally:
        sel.close()


if __name__ == "__main__":
    main()