import socket
import pydbus


port = 3  # Normal port for rfcomm?
buf_size = 1024

bus = pydbus.SystemBus()
adapter = bus.get('org.bluez', '/org/bluez/hci0')
adapter_addr = adapter.Address


s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
s.bind((adapter_addr, port))
s.listen(1)
try:
    print('Listening for connection...')
    client, address = s.accept()
    print(f'Connected to {address}')

    while True:
        data = client.recv(buf_size)
        if data:
            print(data)
except Exception as e:
    print(f'Something went wrong: {e}')
    client.close()
    s.close()