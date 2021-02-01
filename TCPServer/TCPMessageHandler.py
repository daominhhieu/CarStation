import sys
import selectors
import json
import io
import struct
from DatabaseHandler import *
from cryptography.fernet import Fernet


MSG_LENGTH = 1024


class Message:
    def __init__(self, selector, sock, addr, fernetkey, key):
        self.selector = selector
        self.sock = sock
        self.addr = addr
        self._recv_buffer = b""
        self._send_buffer = b""
        self._jsonheader_len = None
        self.jsonheader = None
        self.request = None
        self.response_created = False
        self.fernetkey = fernetkey
        self.key = key
        self.messageDecypted = False
        self.messageEncypted = False

    def _set_selector_events_mask(self, mode):
        """Set selector to listen for events: mode is 'r', 'w', or 'rw'."""
        if mode == "r":
            events = selectors.EVENT_READ
        elif mode == "w":
            events = selectors.EVENT_WRITE
        elif mode == "rw":
            events = selectors.EVENT_READ | selectors.EVENT_WRITE
        else:
            raise ValueError(f"Invalid events mask mode {repr(mode)}.")
        self.selector.modify(self.sock, events, data=self)


    def process_events(self, mask):
        if mask & selectors.EVENT_READ:
            self.read()
        if mask & selectors.EVENT_WRITE:
            self.write()

    def read(self):
        self._read()

        if self.messageDecypted == False:
            self.DecryptMessage()

        if self.messageDecypted:
            self.process_protoheader()

        if self._jsonheader_len is not None:
            if self.jsonheader is None:
                self.process_jsonheader()

        if self.jsonheader:
            if self.request is None:
                self.process_request()

    def write(self):
        if self.request:
            if not self.response_created:
                self.create_response()

        self._write()

    def startConnection(self):
        content = {"result": self.key}
        content.update({"addr": self.addr[0]})
        content.update({"action": "virgin"})
        content_encoding = "utf-8"
        response = {
            "content_bytes": self._json_encode(content, content_encoding),
            "content_type": "text/json",
            "content_encoding": content_encoding,
        }
        message = self._create_message(**response)
        self._send_buffer += message
        self._send_buffer += "\n".encode("utf-8")
        print("sending", repr(self._send_buffer), "to", self.addr)
        try:
            sent = self.sock.send(self._send_buffer)
        except BlockingIOError:
            pass
        self._send_buffer = b""


    def close(self):
        print("closing connection to", self.addr)
        try:
            self.selector.unregister(self.sock)
        except Exception as e:
            print(
                "error: selector.unregister() exception for",
                f"{self.addr}: {repr(e)}",
            )

        try:
            self.sock.close()
        except OSError as e:
            print(
                "error: socket.close() exception for",
                f"{self.addr}: {repr(e)}",
            )
        finally:
            # Delete reference to socket object for garbage collection
            self.sock = None
##=====================================================================================READ SECTION
    def _read(self):
        try:
            # Should be ready to read
            data = self.sock.recv(MSG_LENGTH)
        except BlockingIOError:
            # Resource temporarily unavailable (errno EWOULDBLOCK)
            pass
        else:
            if data:
                self._recv_buffer += data
            else:
                lostConnection(self.addr[0])
                print("delete ip in db:..."+self.addr[0])
                raise RuntimeError("Peer closed.")                

    def DecryptMessage(self):
        if(len(self._recv_buffer)>0):
            print("receiving encrypted: "+self._recv_buffer.decode("utf-8"))
            self._recv_buffer = self.fernetkey.decrypt(self._recv_buffer)
            self.messageDecypted = True

    def _json_decode(self, json_bytes, encoding):
        tiow = io.TextIOWrapper(
            io.BytesIO(json_bytes), encoding=encoding, newline=""
        )
        obj = json.load(tiow)
        tiow.close()
        return obj
    
    def process_protoheader(self):
        hdrlen = 1
        if len(self._recv_buffer) >= hdrlen:
            self._jsonheader_len = struct.unpack(
                ">B", self._recv_buffer[:hdrlen]
            )[0]
            self._recv_buffer = self._recv_buffer[hdrlen:]

    def process_jsonheader(self):
        hdrlen = self._jsonheader_len
        if len(self._recv_buffer) >= hdrlen:
            self.jsonheader = self._json_decode(
                self._recv_buffer[:hdrlen], "utf-8"
            )
            self._recv_buffer = self._recv_buffer[hdrlen:]
            for reqhdr in (
                "byteorder",
                "content-length",
                "content-type",
                "content-encoding",
            ):
                if reqhdr not in self.jsonheader:
                    raise ValueError(f'Missing required header "{reqhdr}".')

    def process_request(self):
        content_len = self.jsonheader["content-length"]
        if not len(self._recv_buffer) >= content_len:
            return
        data = self._recv_buffer[:content_len]
        self._recv_buffer = self._recv_buffer[content_len:]
        if self.jsonheader["content-type"] == "text/json":
            encoding = self.jsonheader["content-encoding"]
            self.request = self._json_decode(data, encoding)
            print("received decrypted request", repr(self.request), "from", self.addr)
        else:
            # Binary or unknown content-type
            self.request = data
            print(
                f'received {self.jsonheader["content-type"]} request from',
                self.addr,
            )
        # Set selector to listen for write events, we're done reading.
        self._set_selector_events_mask("w")

##=====================================================================================WRITE SECTION

    def EncryptMessage(self, data):
        output = self.fernetkey.encrypt(data)
        return output

    def _json_encode(self, obj, encoding):
        return json.dumps(obj, ensure_ascii=False).encode(encoding)

    def create_response(self):
        if self.jsonheader["content-type"] == "text/json":
            response = self._create_response_json_content()
        else:
            # Binary or unknown content-type
            response = self._create_response_binary_content()
        message = self._create_message(**response)
        self.response_created = True
        self._send_buffer += message

    def _create_response_json_content(self):
        action = self.request.get("action")
        content = {"action": action}
        if(action == "login"):
            phone = self.request.get("phone")
            password = self.request.get("password")
            key = self.key
            addr = self.addr[0]
            answer = login(phone, password, key, addr)
            content.update({"result": answer})
            if(answer == "good"):
                answer = getuserinfo(phone)
                if(answer != []):
                    content.update({"result": "good"})
                    content.update({"phone": answer[0]})
                    content.update({"password": answer[1]})
                    content.update({"budget": answer[2]})
                    content.update({"vehicle_name": answer[3]})
                    content.update({"vehicle_mass": answer[4]})
                    content.update({"login": answer[5]})
                else:
                    content.update({"result": "bad"})

            
        elif(action == "logout"):
            phone = self.request.get("phone")
            addr = self.addr[0]
            answer = logout(phone, addr)
            content.update({"result": "good"})
        
        elif(action == "signup"):
            phone = self.request.get("phone")
            password = self.request.get("password")
            answer = signup(phone, password)
            content.update({"result": answer})

        elif(action == "addmoney"):
            phone = self.request.get("phone")
            money = self.request.get("money")
            answer = addmoney(phone, money)
            content.update({"result": answer})

        elif(action == "retrievemoney"):
            phone = self.request.get("phone")
            money = self.request.get("money")
            answer = retrievemoney(phone, money)
            content.update({"result": answer})

        elif(action == "payfee"):
            phone = self.request.get("phone")
            Longitude1 = self.request.get("Longitude1")
            Latitude1 = self.request.get("Latitude1")
            Longitude2 = self.request.get("Longitude2")
            Latitude2 = self.request.get("Latitude2")
            distance = self.request.get("distance")
            street = self.request.get("street")
            answer = payfee(phone, Longitude1, Latitude1, Longitude2, Latitude2, distance, street)
            content.update({"result": answer})

        elif(action == "registerdriver"):
            phone = self.request.get("phone")
            vehicle_name = self.request.get("vehicle_name")
            vehicle_mass = self.request.get("vehicle_mass")
            answer = registerdriver(phone, vehicle_name, vehicle_mass)
            content.update({"result": answer})

        elif(action == "gethistory"):
            phone = self.request.get("phone")
            index = self.request.get("index")
            answer = gethistory(phone, index)
            if(answer != []):
                content.update({"result": "good"})
                content.update({"phone": answer[0]})
                content.update({"Longitude1": answer[1]})
                content.update({"Latitude1": answer[2]})
                content.update({"money": answer[3]})
                content.update({"time": answer[4]})
                content.update({"vehicle_name": answer[5]})
                content.update({"vehicle_mass": answer[6]})
                content.update({"Longitude2": answer[7]})
                content.update({"Latitude2": answer[8]})
                content.update({"street": answer[9]})
            else:
                content.update({"result": "bad"})
        
        elif(action == "getuserinfo"):
            phone = self.request.get("phone")
            answer = getuserinfo(phone)
            if(answer != []):
                content.update({"result": "good"})
                content.update({"phone": answer[0]})
                content.update({"password": answer[1]})
                content.update({"budget": answer[2]})
                content.update({"vehicle_name": answer[3]})
                content.update({"vehicle_mass": answer[4]})
                content.update({"login": answer[5]})
            else:
                content.update({"result": "bad"})

        else:
            content.update({"result": "bad"})

        content_encoding = "utf-8"
        response = {
            "content_bytes": self._json_encode(content, content_encoding),
            "content_type": "text/json",
            "content_encoding": content_encoding,
        }
        return response

    def _create_response_binary_content(self):
        response = {
            "content_bytes": b"First 10 bytes of request: "
            + self.request[:10],
            "content_type": "binary/custom-server-binary-type",
            "content_encoding": "binary",
        }
        return response

    def _create_message(
        self, *, content_bytes, content_type, content_encoding
    ):
        jsonheader = {
            "byteorder": sys.byteorder,
            "content-type": content_type,
            "content-encoding": content_encoding,
            "content-length": len(content_bytes),
        }
        jsonheader_bytes = self._json_encode(jsonheader, "utf-8")
        message_hdr = struct.pack(">B", len(jsonheader_bytes))
        message = message_hdr + jsonheader_bytes + content_bytes
        return message
    
    def _write(self):
        if self._send_buffer:
            print("sending :" + self._send_buffer.decode('utf-8'))
            self._send_buffer = self.EncryptMessage(self._send_buffer)
            print("sending encrypted:   ", repr(self._send_buffer), "to", self.addr)
            try:
                # Should be ready to write
                sent = self.sock.send(self._send_buffer)
            except BlockingIOError:
                # Resource temporarily unavailable (errno EWOULDBLOCK)
                pass
            else:
                self._send_buffer = self._send_buffer[sent:]
                # Close when the buffer is drained. The response has been sent.
                if sent and not self._send_buffer:
                    self.close()